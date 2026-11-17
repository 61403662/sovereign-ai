"""Turn structured SQL/BOM query results into natural language via local LLM."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from sovereign_ai.config_loaders import load_models_config, load_rag_config
from sovereign_ai.ollama_client import OllamaClient
from sovereign_ai.paths import repo_root

SQL_NL_SYSTEM = """你是本地制造助手。用户问题已由 SQLite 只读查询完成。
你只能根据消息里的「query_facts」JSON 字段，用自然、简洁的简体中文回答用户。

硬性规则：
1. 金额、数量、供应商代号、材料编码必须与 JSON 完全一致；禁止改数字、禁止四舍五入。
2. 不要编造 JSON 中没有的物料、供应商或型号。
3. 若 JSON 含 total 或 unit_price，回答中必须保留相同数值（如 26.7、2.8）。
4. 禁止 markdown 代码块；禁止「照抄工程清单」：不要用多行「- 物料 × 数量 @ 单价 →」列表格式。
5. 用 2～5 句口语化中文，像同事口头汇报；可一句点明合计，必要时用顿号串联料名，但不要逐行抄表。
6. 若 query_facts 含 currency 为 CNY，回答中须出现「CNY」或「元」至少其一；含 material_code / supplier_code 时须写出代号。"""

_RETRY_USER = (
    "你上一版仍像 BOM 清单体（多行减号列表）。请重写：仅 2～4 句口语中文，不要任何行首「-」，"
    "合计金额与 query_facts 中 total 完全一致。"
)

_ENV_SQL_NL = "SOVEREIGN_SQL_NL_FORMAT"
_NL_TEMPERATURE = 0.65


def _env_sql_nl_override() -> bool | None:
    raw = os.environ.get(_ENV_SQL_NL)
    if raw is None or not str(raw).strip():
        return None
    return str(raw).strip().lower() not in ("0", "false", "no", "off")


def sql_nl_format_enabled(root=None) -> bool:
    """Whether unified ask should LLM-format SQL answers (config + env override)."""
    env = _env_sql_nl_override()
    if env is not None:
        return env
    root = root or repo_root()
    rag = load_rag_config(root)
    return bool(rag.get("sql_nl_format", False))


def _strip_boilerplate(text: str) -> str:
    kept: list[str] = []
    for ln in text.splitlines():
        if "虚构样例" in ln or "非模型臆测" in ln:
            continue
        kept.append(ln.strip())
    return "\n".join(kept).strip()


def answers_too_similar(template: str, natural: str) -> bool:
    """True when NL output still looks like the SQL template (for demo warnings)."""
    a = _strip_boilerplate(template).casefold()
    b = _strip_boilerplate(natural).casefold()
    if not b:
        return True
    if a == b or b in a or a in b:
        return True
    a_bullets = sum(1 for ln in a.splitlines() if ln.lstrip().startswith("-"))
    b_bullets = sum(1 for ln in b.splitlines() if ln.lstrip().startswith("-"))
    if a_bullets >= 2 and b_bullets >= 2:
        return True
    # heavy overlap of numeric lines
    a_nums = set(re.findall(r"\d+\.?\d*", a))
    b_nums = set(re.findall(r"\d+\.?\d*", b))
    if a_nums and a_nums == b_nums and len(a.splitlines()) >= 4 and len(b.splitlines()) >= 4:
        return True
    return False


def _build_user_message(question: str, bom_result: dict[str, Any]) -> str:
    payload = {
        "user_question": question,
        "intent": bom_result.get("intent"),
        "query_facts": bom_result.get("data"),
    }
    return (
        f"用户问题：{question}\n\n"
        "请仅依据 query_facts 作答（勿编造）：\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def _call_nl_chat(
    client: OllamaClient,
    question: str,
    bom_result: dict[str, Any],
    template: str,
) -> str:
    user_content = _build_user_message(question, bom_result)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SQL_NL_SYSTEM},
        {"role": "user", "content": user_content},
    ]
    text = client.chat(messages, temperature=_NL_TEMPERATURE)
    text = (text or "").strip()
    if text and answers_too_similar(template, text):
        messages.append({"role": "assistant", "content": text})
        messages.append({"role": "user", "content": _RETRY_USER})
        text = (client.chat(messages, temperature=_NL_TEMPERATURE) or "").strip()
    return text


def maybe_naturalize_sql_answer(
    question: str,
    bom_result: dict[str, Any],
    root=None,
    *,
    force_nl: bool | None = None,
) -> str:
    """Return LLM-phrased answer, or template text if disabled or Ollama fails."""
    root = root or repo_root()
    template = str(bom_result.get("answer") or "")
    use_nl = sql_nl_format_enabled(root) if force_nl is None else force_nl
    if not use_nl:
        return template

    models = load_models_config(root)
    client = OllamaClient(
        str(models["ollama_base_url"]),
        str(models["chat_model"]),
        str(models["embed_model"]),
    )
    try:
        text = _call_nl_chat(client, question, bom_result, template)
        return text or template
    except Exception:
        return template


def compare_template_and_nl(question: str, root=None) -> dict[str, Any]:
    """Run BOM SQL once; return template answer and optional NL phrasing (for demos)."""
    from sovereign_ai.bom.runner import answer_bom_question

    bom = answer_bom_question(question)
    if not bom.get("ok"):
        return {"ok": False, "error": bom.get("error"), "question": question}
    template = str(bom.get("answer") or "")
    natural = maybe_naturalize_sql_answer(question, bom, root=root, force_nl=True)
    similar = answers_too_similar(template, natural)
    return {
        "ok": True,
        "question": question,
        "intent": bom.get("intent"),
        "data": bom.get("data"),
        "template": template,
        "natural": natural,
        "same_template_fallback": natural == template,
        "nl_looks_like_template": similar,
    }
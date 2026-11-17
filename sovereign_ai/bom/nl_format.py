"""Turn structured SQL/BOM query results into natural language via local LLM."""

from __future__ import annotations

import json
import os
from typing import Any

from sovereign_ai.config_loaders import load_models_config, load_rag_config
from sovereign_ai.ollama_client import OllamaClient
from sovereign_ai.paths import repo_root

SQL_NL_SYSTEM = """你是本地制造助手。用户问题已由 SQLite 只读查询完成。
你只能根据消息里的「查询结果 JSON」用自然、简洁的简体中文回答。

硬性规则：
1. 金额、数量、供应商名称/代号、材料编码必须与 JSON 完全一致；禁止改数字、禁止四舍五入。
2. 不要编造 JSON 中没有的物料、供应商或型号。
3. 若 JSON 含 total 或 unit_price，回答中必须保留相同数值。
4. 不要用 markdown 代码块；可分点叙述，适合口语阅读。"""

_ENV_SQL_NL = "SOVEREIGN_SQL_NL_FORMAT"


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
    payload = {
        "user_question": question,
        "intent": bom_result.get("intent"),
        "data": bom_result.get("data"),
        "verified_template": bom_result.get("answer"),
    }
    user_content = (
        f"用户问题：{question}\n\n"
        f"查询结果 JSON：\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
    try:
        text = client.chat(
            [
                {"role": "system", "content": SQL_NL_SYSTEM},
                {"role": "user", "content": user_content},
            ]
        )
        return (text or "").strip() or template
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
    return {
        "ok": True,
        "question": question,
        "intent": bom.get("intent"),
        "data": bom.get("data"),
        "template": template,
        "natural": natural,
        "same_template_fallback": natural == template,
    }
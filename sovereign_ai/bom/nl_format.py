"""Turn structured SQL/BOM query results into natural language via local LLM."""

from __future__ import annotations

import json
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


def maybe_naturalize_sql_answer(
    question: str,
    bom_result: dict[str, Any],
    root=None,
) -> str:
    """Return LLM-phrased answer, or template text if disabled or Ollama fails."""
    root = root or repo_root()
    rag = load_rag_config(root)
    if not rag.get("sql_nl_format", True):
        return str(bom_result.get("answer") or "")

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
        return (text or "").strip() or str(bom_result.get("answer") or "")
    except Exception:
        return str(bom_result.get("answer") or "")
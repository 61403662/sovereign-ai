"""Choose sql (BOM) vs rag for a natural-language question."""

from __future__ import annotations

from sovereign_ai.bom.db import database_ready
from sovereign_ai.bom.router import BomIntent, classify_bom_question
from sovereign_ai.paths import repo_root

# Price/BOM wording — prefer SQL even when doc keywords appear (e.g. 检验 + 材料费).
_SQL_STRONG = (
    "材料费",
    "材料费用",
    "多少钱",
    "报价",
    "最低价",
    "哪家",
    "BOM",
    "bom",
    "有哪些料",
    "物料清单",
    "型号列表",
    "哪些型号",
    "风机型号",
    "样例库",
)

# Document / process questions — prefer RAG when no strong SQL/BOM ask.
_RAG_OVERRIDE = (
    "检验",
    "让步",
    "工艺",
    "规范",
    "SOP",
    "装配",
    "划痕",
    "来料",
    "AQL",
    "计划",
    "Scope",
    "目标与原则",
    "后端",
    "前端",
)


def should_use_bom(question: str, root=None) -> bool:
    q = (question or "").strip()
    if not q:
        return False
    root = root or repo_root()
    if not database_ready(root):
        return False
    intent = classify_bom_question(q)
    if intent == BomIntent.UNKNOWN:
        return False
    if any(k in q for k in _SQL_STRONG):
        return True
    if any(k in q for k in _RAG_OVERRIDE):
        return False
    return True


def route_label(question: str, root=None) -> str:
    return "sql" if should_use_bom(question, root) else "rag"
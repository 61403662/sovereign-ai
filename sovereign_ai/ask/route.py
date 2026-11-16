"""Choose sql (BOM) vs rag for a natural-language question."""

from __future__ import annotations

from sovereign_ai.bom.db import database_ready
from sovereign_ai.bom.router import BomIntent, classify_bom_question
from sovereign_ai.paths import repo_root

# Document / process questions — prefer RAG even if a model code appears.
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
    if any(k in q for k in _RAG_OVERRIDE):
        return False
    if classify_bom_question(q) == BomIntent.UNKNOWN:
        return False
    root = root or repo_root()
    return database_ready(root)


def route_label(question: str, root=None) -> str:
    return "sql" if should_use_bom(question, root) else "rag"
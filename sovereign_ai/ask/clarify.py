"""Clarify ambiguous dual-intent questions before routing (AI-13)."""

from __future__ import annotations

import os
from typing import Any

from sovereign_ai.ask.route import _RAG_OVERRIDE, _SQL_STRONG, should_use_bom
from sovereign_ai.bom.db import database_ready
from sovereign_ai.paths import repo_root

# Document cues that with 价钱 still mean AI-10 single SQL (价赢), not clarify.
_PRICE_WIN_DOC_ONLY = frozenset(
    {"检验", "工艺", "计划", "Scope", "后端", "前端", "目标与原则", "装配"}
)

_CLARIFY_OPTIONS = (
    {"id": "rag", "label": "只要文档/规程（RAG）"},
    {"id": "sql", "label": "只要价钱/BOM（SQL）"},
    {"id": "compound", "label": "两个都要（复合答）"},
)


def clarify_enabled() -> bool:
    v = (os.environ.get("SOVEREIGN_CLARIFY") or "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def should_clarify(question: str, root=None) -> bool:
    q = (question or "").strip()
    if not clarify_enabled() or not q:
        return False
    root = root or repo_root()
    if not database_ready(root):
        return False

    from sovereign_ai.ask.compound import should_compound

    if should_compound(q, root):
        return False

    has_sql = any(k in q for k in _SQL_STRONG)
    has_doc = any(k in q for k in _RAG_OVERRIDE)
    if not (has_sql and has_doc):
        return False

    if should_use_bom(q, root):
        doc_hits = [k for k in _RAG_OVERRIDE if k in q]
        priceish = any(
            k in q for k in ("材料费", "材料费用", "多少钱", "报价", "总价", "估算", "价格")
        )
        if priceish and doc_hits and all(d in _PRICE_WIN_DOC_ONLY for d in doc_hits):
            return False

    return True


def build_clarify_response(question: str) -> dict[str, Any]:
    return {
        "ok": True,
        "clarify": True,
        "route": "clarify",
        "error": None,
        "question": question,
        "answer": "",
        "prompt": (
            "这句话里既有「规程/检验类」意思，又有「价钱/BOM」意思，系统不能替你猜现在要哪一种。"
            "请再执行一次并带上 --choice（或浏览器里点选）："
        ),
        "options": list(_CLARIFY_OPTIONS),
        "hint": (
            '示例: python -m sovereign_ai.ask "你的原问题" --choice rag'
            " | sql | compound"
        ),
        "citations": [],
        "citations_text": "",
    }
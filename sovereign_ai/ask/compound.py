"""Detect and merge RAG + SQL when user explicitly asks for both."""

from __future__ import annotations

from sovereign_ai.ask.route import _RAG_OVERRIDE, _SQL_STRONG
from sovereign_ai.bom.db import database_ready
from sovereign_ai.paths import repo_root

# Explicit dual-intent cues (avoid 检验+材料费 which AI-10 routes to SQL only).
_COMPOUND_MARKERS = ("同时", "并且", "还要", "顺便", "另外")


def split_compound_parts(question: str) -> tuple[str, str]:
    """Split on first 同时/并且/… into (doc-ish, price-ish) clauses."""
    q = (question or "").strip()
    for m in _COMPOUND_MARKERS:
        if m in q:
            left, right = q.split(m, 1)
            return left.strip(), right.strip()
    for sep in ("？", "?", "；", ";"):
        if sep in q:
            left, _, right = q.partition(sep)
            left, right = left.strip(), right.strip()
            if left and right:
                if not left.endswith(("？", "?")):
                    left = left + "？"
                return left, right
    return q, q


def should_compound(question: str, root=None) -> bool:
    q = (question or "").strip()
    if not q or not database_ready(root or repo_root()):
        return False
    if not any(m in q for m in _COMPOUND_MARKERS):
        return False
    has_sql = any(k in q for k in _SQL_STRONG)
    has_doc = any(k in q for k in _RAG_OVERRIDE)
    return has_sql and has_doc
"""JSONL load + pass/fail rules (no Ollama/Chroma import)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class QaCase:
    line_no: int
    question: str
    expected_contains: list[str]
    expected_source: str | None
    expected_route: str | None = None
    expected_contains_any: list[str] | None = None


@dataclass
class QaVerdict:
    case: QaCase
    passed: bool
    detail: str
    ok: bool
    answer: str
    citations: list[dict[str, Any]]


def _normalize(s: str) -> str:
    return (s or "").casefold()


def load_jsonl(path: Path) -> list[QaCase]:
    cases: list[QaCase] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        row = json.loads(line)
        question = str(row.get("question") or "").strip()
        if not question:
            raise ValueError(f"{path}:{line_no}: missing question")
        raw_contains = row.get("expected_contains") or []
        if isinstance(raw_contains, str):
            raw_contains = [raw_contains]
        expected_contains = [str(x) for x in raw_contains]
        src = row.get("expected_source")
        expected_source = None if src is None else str(src)
        route_raw = row.get("expected_route", row.get("route"))
        expected_route = None if route_raw is None else str(route_raw).strip().lower()
        any_raw = row.get("expected_contains_any")
        expected_contains_any: list[str] | None = None
        if any_raw:
            if isinstance(any_raw, str):
                any_raw = [any_raw]
            expected_contains_any = [str(x) for x in any_raw]
        cases.append(
            QaCase(
                line_no=line_no,
                question=question,
                expected_contains=expected_contains,
                expected_source=expected_source,
                expected_route=expected_route,
                expected_contains_any=expected_contains_any,
            )
        )
    return cases


def _answer_has_needle(answer: str, needle: str) -> bool:
    if needle in answer:
        return True
    return _normalize(needle) in _normalize(answer)


def grade_case(case: QaCase, result: dict[str, Any]) -> QaVerdict:
    ok = bool(result.get("ok"))
    answer = str(result.get("answer") or "")
    citations = list(result.get("citations") or [])
    if not ok:
        return QaVerdict(
            case=case,
            passed=False,
            detail=result.get("error") or "ask returned ok=False",
            ok=False,
            answer=answer,
            citations=citations,
        )

    if case.expected_contains_any:
        if not any(_answer_has_needle(answer, n) for n in case.expected_contains_any):
            return QaVerdict(
                case=case,
                passed=False,
                detail=f"answer missing any of {case.expected_contains_any!r}",
                ok=True,
                answer=answer,
                citations=citations,
            )

    missing: list[str] = []
    for needle in case.expected_contains:
        if needle in answer:
            continue
        if _normalize(needle) in _normalize(answer):
            continue
        missing.append(needle)
    if missing:
        return QaVerdict(
            case=case,
            passed=False,
            detail=f"answer missing expected substrings: {missing!r}",
            ok=True,
            answer=answer,
            citations=citations,
        )

    if case.expected_route:
        actual = str(result.get("route") or "").strip().lower()
        if actual != case.expected_route:
            return QaVerdict(
                case=case,
                passed=False,
                detail=f"expected route {case.expected_route!r}, got {actual!r}",
                ok=True,
                answer=answer,
                citations=citations,
            )

    if case.expected_source:
        sources = [str(c.get("source") or "") for c in citations]
        norm_expected = case.expected_source.replace("\\", "/")
        expected_name = Path(norm_expected).name

        def _source_ok(src: str) -> bool:
            norm = src.replace("\\", "/")
            if norm_expected in norm:
                return True
            return expected_name and Path(norm).name == expected_name

        if not any(_source_ok(s) for s in sources):
            return QaVerdict(
                case=case,
                passed=False,
                detail=f"citations sources {sources!r} do not include {case.expected_source!r}",
                ok=True,
                answer=answer,
                citations=citations,
            )

    return QaVerdict(
        case=case,
        passed=True,
        detail="ok",
        ok=True,
        answer=answer,
        citations=citations,
    )
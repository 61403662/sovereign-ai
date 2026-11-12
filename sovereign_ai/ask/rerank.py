import re


def _question_intent(question: str) -> set[str]:
    q = question.casefold()
    intents: set[str] = set()
    if any(t in q for t in ("后端", "backend", "接口", "api", "服务端")):
        intents.add("backend")
    if any(t in q for t in ("前端", "frontend", "界面", "ui")):
        intents.add("frontend")
    if any(t in q for t in ("测试", "test", "验收", "回归")):
        intents.add("tests")
    if any(t in q for t in ("总体目标", "项目目标", "目标是什么", "管什么", "分别管")):
        intents.add("goals")
    return intents


def _coop_ids(question: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"COOP-\d+", question, flags=re.I)))


def _coop_boost(source: str, text: str, coop_ids: list[str]) -> float:
    if not coop_ids:
        return 0.0
    src = source.casefold()
    prefix = (text[:160] if text else "").casefold()
    boost = 0.0
    for coop in coop_ids:
        num = coop.split("-", 1)[-1] if "-" in coop else coop
        if num in src or num in prefix or coop.casefold() in prefix:
            boost += 0.28
    return boost


def _heading_boost(heading: str, text: str, intents: set[str]) -> float:
    """Lower distance is better; return delta to subtract from distance."""
    h = heading.casefold()
    prefix = (text[:160] if text else "").casefold()
    boost = 0.0
    if "backend" in intents:
        if h == "backend plan" or "backend plan" in prefix:
            boost += 0.4
        elif h == "scope":
            boost -= 0.25
    if "frontend" in intents:
        if h == "frontend plan" or "frontend plan" in prefix:
            boost += 0.4
    if "tests" in intents:
        if h == "tests" or "regression" in prefix:
            boost += 0.35
    if "goals" in intents:
        if h == "目标与原则" or "目标与原则" in prefix:
            boost += 0.55
        elif h in ("子计划导航", "plan 管理约束"):
            boost -= 0.35
        elif any(
            token in heading
            for token in ("缺口", "单据跟踪", "真实但已有", "条件成立", "已排除")
        ):
            boost -= 0.45
    return boost


def rerank_hits(question: str, hits: list[dict]) -> list[dict]:
    if not hits:
        return hits
    intents = _question_intent(question)
    coop_ids = _coop_ids(question)

    def sort_key(h: dict) -> float:
        dist = float(h.get("distance") if h.get("distance") is not None else 1.0)
        source = str(h.get("source") or "")
        text = str(h.get("text") or "")
        boost = _heading_boost(
            str(h.get("heading") or ""),
            text,
            intents,
        )
        boost += _coop_boost(source, text, coop_ids)
        return dist - boost

    return sorted(hits, key=sort_key)


def merge_hits(primary: list[dict], *others: list[dict]) -> list[dict]:
    seen: set[tuple[str, str, str]] = set()
    merged: list[dict] = []
    for group in (primary, *others):
        for h in group:
            key = (
                str(h.get("source") or ""),
                str(h.get("heading") or ""),
                str(h.get("text", ""))[:96],
            )
            if key in seen:
                continue
            seen.add(key)
            merged.append(h)
    return merged


def supplemental_embed_queries(question: str) -> list[str]:
    """Short extra queries so goal/compare questions pull the right sections."""
    coop_ids = _coop_ids(question)
    intents = _question_intent(question)
    queries: list[str] = []
    if "goals" in intents:
        lead = coop_ids[0] if coop_ids else "COOP"
        queries.append(f"{lead} 目标与原则 FAN POD PSI assignee ORG")
    if len(coop_ids) >= 2:
        for cid in coop_ids:
            queries.append(f"{cid} scope SKUNK pipeline expand AI-POD DoD deployment")
    return queries


def effective_top_k(question: str, base_top_k: int, *, multi_coop_multiplier: int = 2, cap: int = 16) -> int:
    """Widen retrieval when several COOP tickets are named in one question."""
    n = len(_coop_ids(question))
    if n >= 2:
        return min(cap, max(base_top_k, base_top_k * multi_coop_multiplier))
    return base_top_k

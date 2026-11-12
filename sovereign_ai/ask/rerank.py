def _question_intent(question: str) -> set[str]:
    q = question.casefold()
    intents: set[str] = set()
    if any(t in q for t in ("后端", "backend", "接口", "api", "服务端")):
        intents.add("backend")
    if any(t in q for t in ("前端", "frontend", "界面", "ui")):
        intents.add("frontend")
    if any(t in q for t in ("测试", "test", "验收", "回归")):
        intents.add("tests")
    return intents


def _heading_boost(heading: str, text: str, intents: set[str]) -> float:
    """Lower distance is better; return delta to subtract from distance."""
    h = heading.casefold()
    prefix = (text[:120] if text else "").casefold()
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
    return boost


def rerank_hits(question: str, hits: list[dict]) -> list[dict]:
    if not hits:
        return hits
    intents = _question_intent(question)
    if not intents:
        return hits

    def sort_key(h: dict) -> float:
        dist = float(h.get("distance") if h.get("distance") is not None else 1.0)
        boost = _heading_boost(
            str(h.get("heading") or ""),
            str(h.get("text") or ""),
            intents,
        )
        return dist - boost

    return sorted(hits, key=sort_key)

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
    if "目标与原则" in question or ("目标" in question and "原则" in question):
        intents.add("goals")
    return intents


def coop_ids_from_question(question: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"COOP-\d+", question, flags=re.I)))


def _coop_ids(question: str) -> list[str]:
    return coop_ids_from_question(question)


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
            for token in (
                "缺口",
                "单据跟踪",
                "真实但已有",
                "条件成立",
                "已排除",
                "预期拆单",
                "et/st",
                "checkpoint",
            )
        ):
            boost -= 0.45
    return boost


def _explicit_section_boost(question: str, heading: str, text: str) -> float:
    """When the user names a section (e.g. 目标与原则), strongly prefer that heading."""
    boost = 0.0
    if "目标与原则" in question:
        if heading == "目标与原则" or "目标与原则" in (text[:100] if text else ""):
            boost += 0.7
        elif heading == "子计划导航":
            boost -= 0.5
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
        boost += _explicit_section_boost(
            question, str(h.get("heading") or ""), text
        )
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
    if "goals" in intents or "目标与原则" in question:
        lead = coop_ids[0] if coop_ids else "COOP"
        queries.append(f"{lead} 目标与原则 FAN POD PSI assignee ORG JIRADC_FEATURE_LIST")
    if len(coop_ids) >= 2:
        for cid in coop_ids:
            queries.append(f"{cid} scope SKUNK pipeline expand AI-POD DoD deployment")
    return queries


def _coop_num(coop_id: str) -> str:
    return coop_id.split("-", 1)[-1] if "-" in coop_id else coop_id


def missing_coop_ids(hits: list[dict], coop_ids: list[str]) -> list[str]:
    if not coop_ids:
        return []
    missing: list[str] = []
    for cid in coop_ids:
        num = _coop_num(cid)
        if not any(num in str(h.get("source") or "") for h in hits):
            missing.append(cid)
    return missing


def per_coop_fallback_queries(coop_id: str) -> list[str]:
    if coop_id.endswith("22162") or "22162" in coop_id:
        return [
            f"{coop_id} SKUNK Pipeline Expand FI FFB DoD getBrotherFeature",
        ]
    if coop_id.endswith("22163") or "22163" in coop_id:
        return [
            f"{coop_id} AI-POD DoD Deployment 目标与原则 FAN POD PSI",
        ]
    return [f"{coop_id} plan scope goals"]


def effective_top_k(question: str, base_top_k: int, *, multi_coop_multiplier: int = 2, cap: int = 16) -> int:
    """Widen retrieval when several COOP tickets are named in one question."""
    n = len(_coop_ids(question))
    if n >= 2:
        return min(cap, max(base_top_k, base_top_k * multi_coop_multiplier))
    return base_top_k

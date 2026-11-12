def _coop_num(coop_id: str) -> str:
    return coop_id.split("-", 1)[-1] if "-" in coop_id else coop_id


def select_citation_hits(
    hits: list[dict],
    *,
    cite_k: int,
    same_source_as_top: bool,
    coop_ids: list[str] | None = None,
) -> list[dict]:
    if not hits or cite_k <= 0:
        return []

    if coop_ids and len(coop_ids) >= 2:
        picked: list[dict] = []
        used_sources: set[str] = set()
        for cid in coop_ids:
            num = _coop_num(cid)
            for h in hits:
                src = str(h.get("source") or "")
                if num not in src or src in used_sources:
                    continue
                picked.append(h)
                used_sources.add(src)
                break
        if picked:
            return picked

    pool = hits
    if same_source_as_top:
        top_source = str(hits[0].get("source") or "")
        pool = [h for h in hits if str(h.get("source") or "") == top_source]
    return pool[:cite_k]


def format_citations(hits: list[dict]) -> str:
    lines = ["", "---", "引用来源:"]
    seen: set[tuple[str, str]] = set()
    for h in hits:
        src = str(h.get("source") or "")
        heading = str(h.get("heading") or "")
        key = (src, heading)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- [来源: {src}#{heading}]")
    return "\n".join(lines)

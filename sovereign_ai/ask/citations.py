def select_citation_hits(
    hits: list[dict],
    *,
    cite_k: int,
    same_source_as_top: bool,
) -> list[dict]:
    if not hits or cite_k <= 0:
        return []
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

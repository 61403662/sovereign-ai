from sovereign_ai.ask.citations import format_citations, select_citation_hits


def test_select_citation_hits_same_source_only():
    hits = [
        {"source": "data/raw/a.md", "heading": "H1", "text": "1"},
        {"source": "data/raw/b.md", "heading": "H2", "text": "2"},
        {"source": "data/raw/a.md", "heading": "H3", "text": "3"},
    ]
    selected = select_citation_hits(hits, cite_k=5, same_source_as_top=True)
    assert len(selected) == 2
    assert all(h["source"] == "data/raw/a.md" for h in selected)

    one = select_citation_hits(hits, cite_k=1, same_source_as_top=True)
    assert len(one) == 1
    assert one[0]["heading"] == "H1"


def test_format_citations_dedupes_heading():
    hits = [
        {"source": "data/raw/a.md", "heading": "Same", "text": "x"},
        {"source": "data/raw/a.md", "heading": "Same", "text": "y"},
    ]
    out = format_citations(hits)
    assert out.count("Same") == 1

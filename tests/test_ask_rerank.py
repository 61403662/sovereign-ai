from sovereign_ai.ask.rerank import (
    effective_top_k,
    ensure_coop_coverage,
    merge_hits,
    missing_coop_ids,
    per_coop_fallback_queries,
    rerank_hits,
    supplemental_embed_queries,
    _question_intent,
)


def test_rerank_backend_question_promotes_backend_plan():
    hits = [
        {
            "heading": "Scope",
            "text": "COOP > Scope\n\n只覆盖 SKUNK 展开",
            "distance": 0.2,
        },
        {
            "heading": "Backend Plan",
            "text": "COOP > Backend Plan\n\nGET /dodItem/getBrotherFeature",
            "distance": 0.25,
        },
    ]
    out = rerank_hits("COOP-22162的后端开发计划是啥？", hits)
    assert out[0]["heading"] == "Backend Plan"


def test_rerank_goals_promotes_objectives_section():
    hits = [
        {
            "heading": "子计划导航",
            "text": "COOP > 子计划导航\n\n链接列表",
            "source": "data/raw/master.plan.md",
            "distance": 0.15,
        },
        {
            "heading": "目标与原则",
            "text": "COOP-22163 > 目标与原则\n\nFAN Project 同步",
            "source": "data/raw/coop-22163.plan.md",
            "distance": 0.22,
        },
    ]
    out = rerank_hits("COOP-22163 的总体目标是什么？", hits)
    assert out[0]["heading"] == "目标与原则"


def test_rerank_coop_id_boosts_matching_file():
    hits = [
        {
            "heading": "Scope",
            "text": "x",
            "source": "data/raw/coop-22163.plan.md",
            "distance": 0.1,
        },
        {
            "heading": "Scope",
            "text": "y",
            "source": "data/raw/coop-22162.plan.md",
            "distance": 0.18,
        },
    ]
    out = rerank_hits("COOP-22162 管什么", hits)
    assert "22162" in out[0]["source"]


def test_goals_intent_from_section_phrase():
    from sovereign_ai.ask.rerank import _question_intent

    assert "goals" in _question_intent("COOP-22163 目标与原则一节说了什么？")


def test_explicit_section_boost_promotes_objectives():
    hits = [
        {
            "heading": "子计划导航",
            "text": "nav",
            "source": "x.md",
            "distance": 0.1,
        },
        {
            "heading": "目标与原则",
            "text": "COOP > 目标与原则\n\nFAN",
            "source": "y.md",
            "distance": 0.25,
        },
    ]
    out = rerank_hits("COOP-22163 目标与原则一节说了什么？", hits)
    assert out[0]["heading"] == "目标与原则"


def test_supplemental_queries_for_scope_compare_multi_coop():
    qs = supplemental_embed_queries("COOP-22162 和 COOP-22163 分别管什么？")
    assert "goals" not in _question_intent("COOP-22162 和 COOP-22163 分别管什么？")
    assert "scope_compare" in _question_intent("COOP-22162 和 COOP-22163 分别管什么？")
    assert any("SKUNK" in q and "22162" in q for q in qs)
    assert any("22163" in q for q in qs)


def test_rerank_scope_compare_promotes_scope_and_objectives():
    hits = [
        {
            "heading": "子计划导航",
            "text": "nav",
            "source": "data/raw/coop-22163.plan.md",
            "distance": 0.1,
        },
        {
            "heading": "Scope",
            "text": "COOP-22162 > Scope\n\nSKUNK 展开",
            "source": "data/raw/coop-22162.plan.md",
            "distance": 0.22,
        },
        {
            "heading": "目标与原则",
            "text": "COOP-22163 > 目标与原则\n\nPOD PSI",
            "source": "data/raw/coop-22163.plan.md",
            "distance": 0.24,
        },
    ]
    out = rerank_hits("COOP-22162 和 COOP-22163 分别管什么？", hits)
    assert out[0]["heading"] in ("Scope", "目标与原则")
    assert out[1]["heading"] in ("Scope", "目标与原则")


def test_ensure_coop_coverage_puts_each_coop_first():
    hits = [
        {"source": "data/raw/coop-22163.plan.md", "heading": "目标与原则", "text": "a"},
        {"source": "data/raw/coop-22163.plan.md", "heading": "子计划导航", "text": "b"},
        {"source": "data/raw/coop-22162.plan.md", "heading": "Scope", "text": "c"},
        {"source": "data/raw/coop-22162.plan.md", "heading": "Backend Plan", "text": "d"},
    ]
    out = ensure_coop_coverage(hits, ["COOP-22162", "COOP-22163"], max_context=8, min_per_coop=1)
    assert "22162" in out[0]["source"]
    assert "22163" in out[1]["source"]


def test_missing_coop_ids_detects_absent_file():
    hits = [{"source": "data/raw/coop-22163_x.plan.md", "heading": "H", "text": "t"}]
    assert missing_coop_ids(hits, ["COOP-22162", "COOP-22163"]) == ["COOP-22162"]


def test_per_coop_fallback_queries():
    assert "SKUNK" in per_coop_fallback_queries("COOP-22162")[0]
    assert "目标与原则" in per_coop_fallback_queries("COOP-22163")[0]


def test_merge_hits_dedupes():
    a = [{"source": "a.md", "heading": "H", "text": "x", "distance": 0.1}]
    b = [{"source": "a.md", "heading": "H", "text": "x", "distance": 0.2}]
    merged = merge_hits(a, b)
    assert len(merged) == 1


def test_effective_top_k_doubles_for_multi_coop():
    assert effective_top_k("COOP-22162 和 COOP-22163", 8) == 16


def test_rerank_no_intent_still_applies_coop_boost():
    hits = [
        {"heading": "A", "text": "a", "source": "a.md", "distance": 0.1},
        {"heading": "B", "text": "b", "source": "b.md", "distance": 0.2},
    ]
    out = rerank_hits("COOP-22162", hits)
    assert out[0]["heading"] == "A"

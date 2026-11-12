from sovereign_ai.ask.rerank import effective_top_k, rerank_hits


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


def test_effective_top_k_doubles_for_multi_coop():
    assert effective_top_k("COOP-22162 和 COOP-22163", 8) == 16


def test_rerank_no_intent_still_applies_coop_boost():
    hits = [
        {"heading": "A", "text": "a", "source": "a.md", "distance": 0.1},
        {"heading": "B", "text": "b", "source": "b.md", "distance": 0.2},
    ]
    out = rerank_hits("COOP-22162", hits)
    assert out[0]["heading"] == "A"

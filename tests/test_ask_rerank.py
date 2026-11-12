from sovereign_ai.ask.rerank import rerank_hits


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


def test_rerank_no_intent_keeps_order():
    hits = [
        {"heading": "A", "text": "a", "distance": 0.1},
        {"heading": "B", "text": "b", "distance": 0.2},
    ]
    out = rerank_hits("这个 ticket 的 overview", hits)
    assert out[0]["heading"] == "A"

from sovereign_ai.eval.grading import QaCase, grade_case


def _case(**kwargs) -> QaCase:
    defaults = {
        "line_no": 1,
        "question": "q",
        "expected_contains": [],
        "expected_source": None,
    }
    defaults.update(kwargs)
    return QaCase(**defaults)


def test_grade_passes_contains_and_source():
    c = _case(
        expected_contains=["5", "抽检"],
        expected_source="data/samples/incoming-inspection-sample.md",
    )
    result = {
        "ok": True,
        "answer": "每批尺寸抽检至少 5 件。",
        "citations": [{"source": "data/raw/incoming-inspection-sample.md", "heading": "尺寸"}],
    }
    v = grade_case(c, result)
    assert v.passed
    assert v.detail == "ok"


def test_grade_fails_missing_substring():
    c = _case(expected_contains=["火星"])
    result = {"ok": True, "answer": "上下文未包含相关信息。", "citations": []}
    v = grade_case(c, result)
    assert not v.passed
    assert "missing expected" in v.detail


def test_grade_fails_wrong_source():
    c = _case(expected_contains=[], expected_source="data/raw/foo.md")
    result = {
        "ok": True,
        "answer": "ok",
        "citations": [{"source": "other.md", "heading": ""}],
    }
    v = grade_case(c, result)
    assert not v.passed
    assert "do not include" in v.detail


def test_grade_ask_error():
    c = _case()
    v = grade_case(c, {"ok": False, "error": "chroma empty", "answer": "", "citations": []})
    assert not v.passed
    assert "chroma empty" in v.detail
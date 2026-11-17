from sovereign_ai.eval.grading import QaCase, grade_case


def _case(**kwargs) -> QaCase:
    defaults = {
        "line_no": 1,
        "question": "q",
        "expected_contains": [],
        "expected_source": None,
        "expected_route": None,
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


def test_grade_sql_route():
    c = _case(expected_contains=["26.7"], expected_route="sql")
    result = {"ok": True, "route": "sql", "answer": "合计 26.7 CNY", "citations": []}
    assert grade_case(c, result).passed


def test_grade_route_mismatch():
    c = _case(expected_route="sql")
    result = {"ok": True, "route": "rag", "answer": "x", "citations": []}
    v = grade_case(c, result)
    assert not v.passed
    assert "route" in v.detail


def test_grade_contains_any_one_match():
    c = QaCase(
        line_no=7,
        question="q",
        expected_contains=[],
        expected_source=None,
        expected_contains_any=["未包含", "无法", "没有"],
    )
    v = grade_case(c, {"ok": True, "answer": "上下文未包含相关信息。", "citations": []})
    assert v.passed
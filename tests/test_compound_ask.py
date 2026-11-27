from sovereign_ai.ask.compound import should_compound
from sovereign_ai.ask.runner import ask_question
from sovereign_ai.bom.db import init_database
from sovereign_ai.paths import repo_root


def test_should_compound_requires_marker():
    root = repo_root()
    init_database(root, reset=True)
    assert not should_compound("XF-120检验时材料费多少钱？", root)
    assert should_compound(
        "扇叶划痕能否让步接收？同时 XF-120 材料费多少钱？", root
    )


def test_ask_compound_route_and_keywords():
    root = repo_root()
    init_database(root, reset=True)
    q = "扇叶划痕能否让步接收？同时做一台 XF-120 材料费多少钱？"
    result = ask_question(q)
    assert result["ok"]
    assert result.get("route") == "compound"
    assert "26.7" in result["answer"]
    assert "【文档与规程】" in result["answer"]
    assert "【BOM 与价钱】" in result["answer"]
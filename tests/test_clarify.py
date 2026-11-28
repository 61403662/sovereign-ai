from sovereign_ai.ask.clarify import should_clarify
from sovereign_ai.bom.db import init_database
from sovereign_ai.paths import repo_root


def test_clarify_ambiguous_dual_intent():
    root = repo_root()
    init_database(root, reset=True)
    q = "扇叶划痕能否让步接收？做一台 XF-120 材料费多少钱？"
    assert should_clarify(q, root)


def test_no_clarify_price_wins_10():
    root = repo_root()
    init_database(root, reset=True)
    assert not should_clarify("XF-120检验时材料费多少钱？", root)


def test_no_clarify_compound_marker():
    root = repo_root()
    init_database(root, reset=True)
    q = "扇叶划痕能否让步接收？同时做一台 XF-120 材料费多少钱？"
    assert not should_clarify(q, root)
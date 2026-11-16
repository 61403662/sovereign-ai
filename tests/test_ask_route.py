from sovereign_ai.ask.route import route_label, should_use_bom
from sovereign_ai.bom.db import init_database
from sovereign_ai.paths import repo_root


def test_route_sql_vs_rag():
    root = repo_root()
    init_database(root, reset=True)
    assert should_use_bom("XF-120 的 BOM 有哪些料？", root)
    assert route_label("做一台 XF-120 材料费多少钱？", root) == "sql"
    assert route_label("每批尺寸抽检至少几件？", root) == "rag"
    assert route_label("XF-120 装配工艺螺栓扭矩多少？", root) == "rag"


def test_bom_without_db_not_sql():
    assert route_label("做一台 XF-120 材料费多少钱？", root="/nonexistent-path") == "rag"
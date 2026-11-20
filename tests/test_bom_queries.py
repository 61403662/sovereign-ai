import sqlite3

from sovereign_ai.bom.db import init_database
from sovereign_ai.bom.queries import estimate_material_cost, extract_model_code, list_bom, list_fan_models
from sovereign_ai.bom.router import BomIntent, classify_bom_question
from sovereign_ai.bom.runner import answer_bom_question
from sovereign_ai.paths import repo_root


def test_init_and_list_bom(tmp_path, monkeypatch):
    # Use temp copy of schema/seed via monkeypatch repo root - actually init needs real repo files
    root = repo_root()
    db_file = root / "storage" / "sqlite" / "fan_bom.db"
    if db_file.is_file():
        db_file.unlink()
    init_database(root, reset=True)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    rows = list_bom(conn, "XF-120")
    conn.close()
    assert len(rows) == 5
    assert extract_model_code("XF-120 的 BOM") == "XF-120"


def test_estimate_cost_matches_sql():
    root = repo_root()
    init_database(root, reset=True)
    conn = sqlite3.connect(root / "storage" / "sqlite" / "fan_bom.db")
    conn.row_factory = sqlite3.Row
    result = estimate_material_cost(conn, "XF-120", as_of="2026-01-01")
    conn.close()
    assert result["ok"]
  # 2.8*1 + 18.5*1 + 1.2*1 + 0.05*4 + 4.0*1 = 26.7
    assert result["total"] == 26.7


def test_list_fan_models():
    root = repo_root()
    init_database(root, reset=True)
    conn = sqlite3.connect(root / "storage" / "sqlite" / "fan_bom.db")
    conn.row_factory = sqlite3.Row
    models = list_fan_models(conn)
    conn.close()
    codes = {m["model_code"] for m in models}
    assert codes == {"XF-120", "XF-200"}


def test_classify_and_answer():
    root = repo_root()
    init_database(root, reset=True)
    assert classify_bom_question("做一台 XF-120 材料费多少钱") == BomIntent.ESTIMATE_COST
    r = answer_bom_question("XF-120 的 BOM 有哪些料？")
    assert r["ok"]
    assert "M-BLADE-ABS" in r["answer"]
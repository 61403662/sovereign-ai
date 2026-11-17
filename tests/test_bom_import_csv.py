import sqlite3

from sovereign_ai.bom.db import db_path, init_database
from sovereign_ai.bom.import_csv import import_csv_directory
from sovereign_ai.bom.queries import estimate_material_cost
from sovereign_ai.paths import repo_root


def _seed_tmp_repo(tmp_path, monkeypatch):
    real = repo_root()
    monkeypatch.setattr("sovereign_ai.bom.import_csv.repo_root", lambda: tmp_path)
    monkeypatch.setattr("sovereign_ai.bom.db.repo_root", lambda: tmp_path)

    (tmp_path / "schema").mkdir(parents=True)
    (tmp_path / "schema" / "fan_bom.sql").write_text(
        (real / "schema" / "fan_bom.sql").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def test_csv_import_matches_seed_cost(tmp_path, monkeypatch):
    _seed_tmp_repo(tmp_path, monkeypatch)
    import_csv_directory(repo_root() / "data" / "samples" / "fan" / "csv", root=tmp_path, reset=True)

    conn = sqlite3.connect(db_path(tmp_path))
    conn.row_factory = sqlite3.Row
    try:
        n = conn.execute("SELECT COUNT(*) FROM bom_line WHERE model_code='XF-120'").fetchone()[0]
        assert n == 5
        result = estimate_material_cost(conn, "XF-120", as_of="2026-01-01")
    finally:
        conn.close()
    assert result["ok"]
    assert result["total"] == 26.7


def test_init_database_still_works_after_schema_split(tmp_path, monkeypatch):
    real = repo_root()
    monkeypatch.setattr("sovereign_ai.bom.db.repo_root", lambda: tmp_path)
    (tmp_path / "schema").mkdir(parents=True)
    (tmp_path / "data" / "samples" / "fan").mkdir(parents=True)
    (tmp_path / "schema" / "fan_bom.sql").write_text(
        (real / "schema" / "fan_bom.sql").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "data" / "samples" / "fan" / "seed.example.sql").write_text(
        (real / "data" / "samples" / "fan" / "seed.example.sql").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    init_database(tmp_path, reset=True)
    assert db_path(tmp_path).is_file()
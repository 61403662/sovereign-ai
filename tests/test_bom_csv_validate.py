import pytest

from sovereign_ai.bom.import_csv import (
    private_csv_ready,
    resolve_csv_dir,
    validate_csv_headers,
)
from sovereign_ai.paths import repo_root


def test_validate_headers_ok_on_sample():
    d = repo_root() / "data" / "samples" / "fan" / "csv"
    validate_csv_headers(d / "fan_model.csv", "fan_model")
    validate_csv_headers(d / "bom_line.csv", "bom_line")


def test_validate_headers_missing_column(tmp_path):
    bad = tmp_path / "fan_model.csv"
    bad.write_text("model_code,name\nXF-1,x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        validate_csv_headers(bad, "fan_model")


def test_resolve_csv_dir_env(monkeypatch, tmp_path):
    monkeypatch.setattr("sovereign_ai.bom.import_csv.repo_root", lambda: tmp_path)
    monkeypatch.setenv("SOVEREIGN_BOM_CSV_DIR", str(tmp_path / "custom"))
    assert resolve_csv_dir() == tmp_path / "custom"


def test_private_csv_ready_false(tmp_path, monkeypatch):
    monkeypatch.setattr("sovereign_ai.bom.import_csv.repo_root", lambda: tmp_path)
    assert not private_csv_ready(tmp_path)
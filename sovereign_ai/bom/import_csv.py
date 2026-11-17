"""Load fictional fan BOM tables from CSV (Phase 2 — enterprise-style exports)."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Any

from sovereign_ai.bom.db import connect, db_path, init_schema
from sovereign_ai.paths import repo_root

_TABLE_LOAD_ORDER: list[tuple[str, str]] = [
    ("fan_model", "fan_model.csv"),
    ("material", "material.csv"),
    ("supplier", "supplier.csv"),
    ("bom_line", "bom_line.csv"),
    ("supplier_offer", "supplier_offer.csv"),
]


def _null_if_blank(value: str | None) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    return None if text == "" else text


def _insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in columns)
    col_sql = ", ".join(columns)
    sql = f"INSERT OR REPLACE INTO {table} ({col_sql}) VALUES ({placeholders})"
    values = [tuple(row[c] for c in columns) for row in rows]
    conn.executemany(sql, values)
    return len(values)


_NUMERIC_COLUMNS = {
    "bom_line": {"qty_per_unit"},
    "supplier_offer": {"unit_price"},
}


def load_csv_table(conn: sqlite3.Connection, table: str, csv_file: Path) -> int:
    with csv_file.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, Any]] = []
        numeric = _NUMERIC_COLUMNS.get(table, set())
        for raw in reader:
            row = {k: _null_if_blank(v) for k, v in raw.items() if k}
            for key in numeric:
                if key in row and row[key] is not None:
                    row[key] = float(row[key])
            rows.append(row)
    return _insert_rows(conn, table, rows)


def default_csv_dir(root: Path | None = None) -> Path:
    root = root or repo_root()
    return root / "data" / "samples" / "fan" / "csv"


def import_csv_directory(
    csv_dir: Path | str | None = None,
    *,
    root: Path | None = None,
    reset: bool = False,
) -> Path:
    """Apply schema and load all sample CSVs (same fictional data as seed.example.sql)."""
    root = root or repo_root()
    csv_dir = Path(csv_dir) if csv_dir is not None else default_csv_dir(root)
    if not csv_dir.is_dir():
        raise FileNotFoundError(f"CSV directory not found: {csv_dir}")

    path = init_schema(root, reset=reset)
    conn = connect(root)
    try:
        for table, filename in _TABLE_LOAD_ORDER:
            n = load_csv_table(conn, table, csv_dir / filename)
            if n == 0:
                raise ValueError(f"no rows in {filename}")
        conn.commit()
    finally:
        conn.close()
    return path


def import_csv_directory_verbose(csv_dir: Path | str | None = None, *, reset: bool = False) -> int:
    path = import_csv_directory(csv_dir, reset=reset)
    print(f"Imported CSV → {path}")
    return 0
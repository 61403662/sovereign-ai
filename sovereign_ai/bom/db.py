from __future__ import annotations

import sqlite3
from pathlib import Path

from sovereign_ai.paths import repo_root


def db_path(root: Path | str | None = None) -> Path:
    if root is None:
        root = repo_root()
    else:
        root = Path(root)
    return root / "storage" / "sqlite" / "fan_bom.db"


def connect(root: Path | str | None = None) -> sqlite3.Connection:
    path = db_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database(root: Path | str | None = None, *, reset: bool = False) -> Path:
    root = Path(root) if root is not None else repo_root()
    path = db_path(root)
    if reset and path.is_file():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = (root / "schema" / "fan_bom.sql").read_text(encoding="utf-8")
    seed = (root / "data" / "samples" / "fan" / "seed.example.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(path)
    try:
        conn.executescript(schema)
        conn.executescript(seed)
        conn.commit()
    finally:
        conn.close()
    return path


def database_ready(root: Path | str | None = None) -> bool:
    path = db_path(root)
    if not path.is_file():
        return False
    conn = connect(root)
    try:
        row = conn.execute("SELECT COUNT(*) FROM fan_model").fetchone()
        return bool(row and row[0] > 0)
    finally:
        conn.close()
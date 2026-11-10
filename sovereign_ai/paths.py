from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    """Find repository root by markers (config/, sovereign_ai/)."""
    cur = (start or Path.cwd()).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "config" / "rag.yaml").is_file() and (parent / "sovereign_ai").is_dir():
            return parent
    raise FileNotFoundError("Could not locate sovereign-ai repo root (need config/rag.yaml)")

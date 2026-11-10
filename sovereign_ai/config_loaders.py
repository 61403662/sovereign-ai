from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_models_config(root: Path) -> dict[str, Any]:
    local = root / "config" / "models.yaml"
    example = root / "config" / "models.example.yaml"
    path = local if local.is_file() else example
    if not path.is_file():
        raise FileNotFoundError("Missing config/models.yaml and models.example.yaml")
    return load_yaml(path)


def load_rag_config(root: Path) -> dict[str, Any]:
    path = root / "config" / "rag.yaml"
    if not path.is_file():
        raise FileNotFoundError("Missing config/rag.yaml")
    return load_yaml(path)

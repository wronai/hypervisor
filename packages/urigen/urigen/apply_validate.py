from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from urigen.models import repo_root


def _load_schema(repo: Path, schema_ref: str) -> dict[str, Any]:
    path = repo / schema_ref.replace("schemas/", "schemas/")
    if not path.is_file():
        path = repo / "schemas" / Path(schema_ref).name
    return json.loads(path.read_text(encoding="utf-8"))


def validate_apply_artifact(data: dict[str, Any], schema_name: str, *, repo: Path) -> list[str]:
    schema_path = f"schemas/{schema_name}"
    try:
        schema = _load_schema(repo, schema_path)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return [f"schema load failed: {exc}"]
    validator = Draft202012Validator(schema)
    return [f"{'.'.join(str(part) for part in error.path)}: {error.message}" for error in validator.iter_errors(data)]

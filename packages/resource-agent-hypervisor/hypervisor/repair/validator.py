from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


def schema_path(repo_root: Path, relative: str) -> Path:
    return repo_root / relative


def load_schema(repo_root: Path, relative: str) -> dict[str, Any]:
    return json.loads(schema_path(repo_root, relative).read_text(encoding="utf-8"))


def validate_artifact(data: dict[str, Any], repo_root: Path, schema_relative: str) -> list[str]:
    schema = load_schema(repo_root, schema_relative)
    validator = Draft202012Validator(schema)
    return [
        f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
        for error in validator.iter_errors(data)
    ]


def validate_incident_dict(data: dict[str, Any], repo_root: Path) -> list[str]:
    from hypervisor.repair.models import INCIDENT_SCHEMA

    return validate_artifact(data, repo_root, INCIDENT_SCHEMA)


def validate_repair_plan_dict(data: dict[str, Any], repo_root: Path) -> list[str]:
    from hypervisor.repair.models import REPAIR_PLAN_SCHEMA

    return validate_artifact(data, repo_root, REPAIR_PLAN_SCHEMA)


def read_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return payload

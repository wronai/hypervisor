from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from urigen.models import repo_root


def _check_yaml_file(path: Path, repo: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"path": str(path), "ok": False, "errors": ["root must be mapping"]}
    errors: list[str] = []
    warnings: list[str] = []
    if not payload.get("$schema"):
        warnings.append("missing $schema")
    if not payload.get("apiVersion"):
        warnings.append("missing apiVersion")
    if not payload.get("kind"):
        warnings.append("missing kind")
    uri = payload.get("uri")
    if isinstance(uri, dict):
        if not uri.get("self"):
            warnings.append("missing uri.self")
    else:
        warnings.append("missing uri block")
    return {
        "path": _repo_relative(path, repo),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def _repo_relative(path: Path, repo: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def schema_check_ecosystem(path: str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    repo = repo_root(root)
    base = Path(path)
    if base.is_file():
        base = base.parent
    results = [_check_yaml_file(yaml_path, repo) for yaml_path in sorted(base.rglob("*.yaml"))]
    warned = [item for item in results if item.get("warnings")]
    return {
        "ok": True,
        "checked": len(results),
        "warnings": len(warned),
        "results": results,
    }

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from hypervisor.paths import find_repo_root


def repair_cases_dir(repo_root: Path | None = None) -> Path:
    return (repo_root or find_repo_root()) / "knowledge" / "repair_cases"


def list_repair_cases(repo_root: Path | None = None) -> list[Path]:
    root = repair_cases_dir(repo_root)
    if not root.is_dir():
        return []
    return sorted(root.glob("*.yaml"))


def load_repair_case(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain YAML mapping")
    return payload


def find_matching_case(
    classification: dict[str, Any],
    inspection: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any] | None:
    families = set(classification.get("family") or [])
    readiness = inspection.get("readiness") or {}
    for path in list_repair_cases(repo_root):
        case_doc = load_repair_case(path)
        case = case_doc.get("case") or case_doc
        case_families = set(case.get("family") or [])
        if not families.intersection(case_families):
            continue
        symptoms = case_doc.get("symptoms") or case.get("symptoms") or []
        if "dynamic_port_selected" in symptoms and not readiness.get("effective_port"):
            continue
        if "runtime_status_running" in symptoms and readiness.get("process") != "running":
            continue
        if "health_failed" in symptoms and readiness.get("health") == "ok":
            continue
        return {**case_doc, "_path": str(path)}
    return None

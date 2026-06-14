from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import yaml


def repo_root_from_here() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file() and (parent / "packages").is_dir():
            return parent
    raise RuntimeError("repo root not found")


def load_boundary_rules(path: Path | None = None) -> dict[str, Any]:
    root = repo_root_from_here()
    rules_path = path or root / "docs" / "PACKAGE_BOUNDARIES.yaml"
    data = yaml.safe_load(rules_path.read_text(encoding="utf-8")) or {}
    return data.get("packages") or {}


def _module_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
                for alias in node.names:
                    imports.add(f"{node.module}.{alias.name}")
    return imports


def _matches_forbidden(import_name: str, forbidden: str) -> bool:
    return import_name == forbidden or import_name.startswith(f"{forbidden}.")


def _allowed(import_name: str, allowed_prefixes: list[str]) -> bool:
    return any(import_name == prefix or import_name.startswith(f"{prefix}.") for prefix in allowed_prefixes)


def scan_package_boundaries(rules: dict[str, Any] | None = None) -> list[str]:
    root = repo_root_from_here()
    rules = rules or load_boundary_rules()
    violations: list[str] = []

    for package_name, spec in rules.items():
        if spec.get("optional") and not (root / spec["root"]).exists():
            continue
        package_root = root / spec["root"]
        if not package_root.is_dir():
            violations.append(f"{package_name}: missing package root {spec['root']}")
            continue
        forbidden = list(spec.get("forbidden") or [])
        allowed_prefixes = list(spec.get("allowed_import_prefixes") or [])
        allowed_path_prefixes = list(spec.get("allowed_path_prefixes") or [])
        for path in sorted(package_root.rglob("*.py")):
            if path.name == "__init__.py" and path.stat().st_size < 5:
                continue
            rel_to_package = path.relative_to(package_root).as_posix()
            skip_forbidden = any(
                rel_to_package.startswith(prefix) for prefix in allowed_path_prefixes
            )
            imports = _module_imports(path)
            rel = path.relative_to(root)
            for import_name in sorted(imports):
                if skip_forbidden:
                    continue
                if _allowed(import_name, allowed_prefixes):
                    continue
                for rule in forbidden:
                    if _matches_forbidden(import_name, rule):
                        violations.append(f"{rel}: forbidden import '{import_name}' (rule: {rule})")
    return violations

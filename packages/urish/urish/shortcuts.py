from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from uri3.paths import find_repo_root


def shortcuts_path(root: Path | None = None) -> Path:
    repo = root or find_repo_root()
    return repo / "config" / "cli_shortcuts.uri.yaml"


def load_shortcuts(root: Path | None = None) -> dict[str, str]:
    path = shortcuts_path(root)
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        return {}
    shortcuts = payload.get("shortcuts") or {}
    resolved: dict[str, str] = {}
    for name, value in shortcuts.items():
        if isinstance(value, str):
            resolved[str(name)] = value
        elif isinstance(value, dict) and value.get("uri"):
            resolved[str(name)] = str(value["uri"])
    scan = (payload.get("shortcuts") or {}).get("scan") if isinstance(payload.get("shortcuts"), dict) else {}
    if isinstance(scan, dict):
        for name, uri in scan.items():
            resolved.setdefault(str(name), str(uri))
    return resolved


def resolve_target(name_or_uri: str, *, root: Path | None = None) -> str:
    if "://" in name_or_uri:
        return name_or_uri
    shortcuts = load_shortcuts(root)
    if name_or_uri not in shortcuts:
        available = ", ".join(sorted(shortcuts)) or "(none)"
        raise ValueError(f"Unknown shortcut {name_or_uri!r}. Available: {available}")
    return shortcuts[name_or_uri]

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from uri3.config.uri_yaml import unwrap_uri_yaml_document
from uri3.paths import find_repo_root


def shortcuts_path(root: Path | None = None) -> Path:
    repo = root or find_repo_root()
    return repo / "config" / "cli_shortcuts.uri.yaml"


def load_shortcut_specs(root: Path | None = None) -> dict[str, dict[str, Any]]:
    path = shortcuts_path(root)
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        return {}
    payload = unwrap_uri_yaml_document(payload)
    shortcuts = payload.get("shortcuts") or {}
    resolved: dict[str, dict[str, Any]] = {}
    for name, value in shortcuts.items():
        if isinstance(value, str):
            resolved[str(name)] = {"uri": value, "payload": {}, "description": ""}
        elif isinstance(value, dict):
            if value.get("uri"):
                payload_value = value.get("payload") or {}
                resolved[str(name)] = {
                    "uri": str(value["uri"]),
                    "payload": payload_value if isinstance(payload_value, dict) else {},
                    "description": str(value.get("description") or ""),
                }
            else:
                for sub_name, sub_uri in value.items():
                    if isinstance(sub_uri, str):
                        resolved[f"{name}.{sub_name}"] = {
                            "uri": sub_uri,
                            "payload": {},
                            "description": "",
                        }
    return resolved


def load_shortcuts(root: Path | None = None) -> dict[str, str]:
    return {name: spec["uri"] for name, spec in load_shortcut_specs(root).items()}


def resolve_shortcut(name_or_uri: str, *, root: Path | None = None) -> dict[str, Any]:
    if "://" in name_or_uri:
        return {"uri": name_or_uri, "payload": {}, "shortcut": None}
    shortcuts = load_shortcut_specs(root)
    if name_or_uri not in shortcuts:
        available = ", ".join(sorted(shortcuts)) or "(none)"
        raise ValueError(f"Unknown shortcut {name_or_uri!r}. Available: {available}")
    spec = shortcuts[name_or_uri]
    return {
        "uri": spec["uri"],
        "payload": dict(spec.get("payload") or {}),
        "shortcut": name_or_uri,
        "description": spec.get("description") or "",
    }


def resolve_target(name_or_uri: str, *, root: Path | None = None) -> str:
    return str(resolve_shortcut(name_or_uri, root=root)["uri"])

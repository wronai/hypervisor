from __future__ import annotations

from pathlib import Path
from typing import Any

from .loader import load_manifest

_BACKEND_REQUIRED_FIELDS: dict[str, tuple[str, str]] = {
    "python": ("target", "python backend requires backend.target"),
    "shell": ("command", "shell backend requires backend.command"),
    "http": ("url", "http backend requires backend.url"),
    "https": ("url", "https backend requires backend.url"),
    "stdio": ("command", "stdio backend requires backend.command"),
    "sse": ("url", "sse backend requires backend.url"),
    "ws": ("url", "ws backend requires backend.url"),
    "docker": ("target", "docker backend requires backend.target"),
    "ssh": ("target", "ssh backend requires backend.target"),
    "mcp": ("target", "mcp backend requires backend.target"),
    "a2a": ("target", "a2a backend requires backend.target"),
    "uri_flow": ("flow", "uri_flow backend requires backend.flow"),
    "uri_graph": ("graph", "uri_graph backend requires backend.graph"),
}


def _validate_backend(manifest, errors: list[str], warnings: list[str]) -> None:
    backend = manifest.backend
    required = _BACKEND_REQUIRED_FIELDS.get(backend.type)
    if required:
        field, message = required
        if not getattr(backend, field, None):
            errors.append(message)
    if backend.type == "uri2ops" and manifest.capability.scheme not in {
        "browser",
        "dom",
        "screen",
        "input",
        "android",
        "pcwin",
    }:
        warnings.append(
            "uri2ops backend is intended for operator schemes "
            "(browser/dom/screen/input/android/pcwin)"
        )


def validate_manifest(path: str | Path) -> dict[str, Any]:
    manifest = load_manifest(path)
    warnings: list[str] = []
    errors: list[str] = []
    if manifest.policy.get("requires_approval") is None and manifest.capability.kind == "command":
        warnings.append("command capability should define policy.requires_approval")
    _validate_backend(manifest, errors, warnings)
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "capability": manifest.capability.id,
    }

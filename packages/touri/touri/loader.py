from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import BackendRef, CapabilityManifest, CapabilityRef


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_manifest(path: str | Path) -> CapabilityManifest:
    p = Path(path)
    data = _read_yaml(p)
    cap = data.get("capability") or {}
    backend = data.get("backend") or {}
    if not cap.get("id") or not cap.get("scheme") or not cap.get("uri_template"):
        raise ValueError(f"Invalid capability block in {p}")
    if not backend.get("type"):
        raise ValueError(f"Invalid backend block in {p}")
    backend_extra = {k: v for k, v in backend.items() if k not in {"type", "target", "command", "method", "url", "operation", "flow", "graph"}}
    return CapabilityManifest(
        version=int(data.get("version", 1)),
        capability=CapabilityRef(
            id=str(cap["id"]),
            scheme=str(cap["scheme"]),
            uri_template=str(cap["uri_template"]),
            operation=str(cap.get("operation", "call")),
            kind=str(cap.get("kind", "query")),
            description=str(cap.get("description", "")),
        ),
        backend=BackendRef(
            type=str(backend["type"]),
            target=backend.get("target"),
            command=backend.get("command"),
            method=backend.get("method"),
            url=backend.get("url"),
            operation=backend.get("operation"),
            flow=backend.get("flow"),
            graph=backend.get("graph"),
            extra=backend_extra,
        ),
        input=data.get("input") or {},
        output=data.get("output") or {},
        policy=data.get("policy") or {},
        events=data.get("events") or {},
        data_quality=data.get("data_quality") or {},
        fallbacks=list(data.get("fallbacks") or []),
    )


def iter_manifest_paths(root: str | Path):
    r = Path(root)
    if r.is_file():
        yield r
        return
    yield from sorted(r.rglob("*.uri.capability.yaml"))


def load_registry(root: str | Path) -> list[CapabilityManifest]:
    return [load_manifest(path) for path in iter_manifest_paths(root)]

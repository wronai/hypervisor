from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from uri3.config.uri_yaml import unwrap_uri_yaml_document
from uri3.resolvers.dispatch import RESOLVE_BY_SCHEME, RESOURCE_SCHEMES, scheme_from_uri
from uri3.resolvers.explain_verification import build_verification_hints, summarize_fallbacks

RESOLUTION_ORDER = ("uri3", "touri", "uri2ops", "hypervisor", "denied")
_CONFIG_NAME = "config/touri.uri.yaml"


def _find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for path in (current, *current.parents):
        if (path / "pyproject.toml").is_file() and (path / "examples").is_dir():
            return path
    return current


def load_touri_config(root: Path | None = None) -> dict[str, Any]:
    base = root or _find_repo_root()
    path = base / _CONFIG_NAME
    if not path.exists():
        return {
            "registry": {"path": "examples/20_touri_capabilities"},
            "resolution_order": list(RESOLUTION_ORDER),
        }
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return unwrap_uri_yaml_document(data) if isinstance(data, dict) else {}


def default_touri_registry(root: Path | None = None) -> Path:
    cfg = load_touri_config(root)
    rel = ((cfg.get("registry") or {}).get("path")) or "examples/20_touri_capabilities"
    base = root or _find_repo_root()
    env_override = os.getenv("TOURI_REGISTRY")
    if env_override:
        return Path(env_override)
    return base / rel


OPERATOR_SCHEMES = frozenset({"browser", "dom", "screen", "input", "android", "pcwin"})
_URI2RUN_BACKEND_TYPES = frozenset(
    {
        "python",
        "shell",
        "http",
        "https",
        "stdio",
        "sse",
        "ws",
        "docker",
        "ssh",
        "mcp",
        "a2a",
        "uri_flow",
        "uri_graph",
        "uri2ops",
    }
)


def runtime_transport_for_match(match: dict[str, Any]) -> str:
    registry = str(match.get("matched_registry") or "unknown")
    if registry == "uri2ops":
        return "uri2ops"
    if registry == "uri3":
        return "uri3:built-in"
    if registry == "hypervisor":
        return "hypervisor:lifecycle"
    if registry == "touri":
        backend_type = str((match.get("backend") or {}).get("type") or "unknown")
        if backend_type in _URI2RUN_BACKEND_TYPES:
            return f"uri2run:{backend_type}"
        return f"touri:{backend_type}"
    return "denied"


def _match_uri3(scheme: str, uri: str) -> dict[str, Any] | None:
    if scheme in OPERATOR_SCHEMES:
        return None
    if scheme in RESOLVE_BY_SCHEME or scheme in RESOURCE_SCHEMES:
        return {
            "matched_registry": "uri3",
            "scheme": scheme,
            "resolver": "built-in",
            "uri": uri,
            "verification": build_verification_hints(
                data_quality=None,
                fallbacks=None,
                matched_registry="uri3",
            ),
        }
    return None


def _match_touri(uri: str, registry_root: Path) -> dict[str, Any] | None:
    if not registry_root.exists():
        return None
    from touri.loader import load_registry
    from touri.matcher import match_uri

    registry = load_registry(registry_root)
    match = match_uri(uri, registry)
    if match is None:
        return None
    manifest = match.manifest
    backend = {
        "type": manifest.backend.type,
        "target": manifest.backend.target,
        "command": manifest.backend.command,
        "method": manifest.backend.method,
        "url": manifest.backend.url,
        "operation": manifest.backend.operation,
        "flow": manifest.backend.flow,
        "graph": manifest.backend.graph,
    }
    backend = {key: value for key, value in backend.items() if value}
    backend.update(manifest.backend.extra or {})
    return {
        "matched_registry": "touri",
        "uri": uri,
        "capability": manifest.capability.id,
        "scheme": manifest.capability.scheme,
        "operation": manifest.capability.operation,
        "kind": manifest.capability.kind,
        "backend": backend,
        "policy": manifest.policy,
        "data_quality": manifest.data_quality,
        "fallbacks": summarize_fallbacks(manifest.fallbacks),
        "params": match.params,
        "verification": build_verification_hints(
            data_quality=manifest.data_quality,
            fallbacks=manifest.fallbacks,
            matched_registry="touri",
        ),
    }


def _match_uri2ops(scheme: str, uri: str, root: Path | None) -> dict[str, Any] | None:
    try:
        from uri2ops.remote_registry.loader import resolve_operation_registry

        registry = resolve_operation_registry(root=root)
        operations = sorted({op for sch, op in registry.operations if sch == scheme})
        if not operations:
            return None
        return {
            "matched_registry": "uri2ops",
            "uri": uri,
            "scheme": scheme,
            "operations": operations,
            "note": "operation must be selected explicitly for uri2ops dispatch",
            "verification": build_verification_hints(
                data_quality=None,
                fallbacks=None,
                matched_registry="uri2ops",
            ),
        }
    except Exception:
        return None


def _match_hypervisor(scheme: str, uri: str) -> dict[str, Any] | None:
    if scheme != "hypervisor":
        return None
    parsed = urlparse(uri)
    parts = [part for part in parsed.path.split("/") if part]
    action = parts[-1] if parts else "unknown"
    deployment_id = (
        parts[1]
        if len(parts) >= 2 and parts[0] == "deployment"
        else parts[0]
        if parts
        else "unknown"
    )
    return {
        "matched_registry": "hypervisor",
        "uri": uri,
        "deployment_id": deployment_id,
        "action": action,
        "note": "lifecycle handled by hypervisor deployment registry",
        "verification": build_verification_hints(
            data_quality=None,
            fallbacks=None,
            matched_registry="hypervisor",
        ),
    }


def explain_uri(
    uri: str,
    *,
    registry_root: str | Path | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    repo_root = root or _find_repo_root()
    scheme = scheme_from_uri(uri)
    cfg = load_touri_config(repo_root)
    order = list(cfg.get("resolution_order") or RESOLUTION_ORDER)
    registry_path = Path(registry_root) if registry_root else default_touri_registry(repo_root)
    checks: list[dict[str, Any]] = []

    for step in order:
        if step == "uri3":
            match = _match_uri3(scheme, uri)
            checks.append({"registry": "uri3", "matched": match is not None})
            if match:
                match["runtime_transport"] = runtime_transport_for_match(match)
                return {"uri": uri, "resolution_order": order, "checks": checks, **match}
        elif step == "touri":
            match = _match_touri(uri, registry_path)
            checks.append(
                {
                    "registry": "touri",
                    "matched": match is not None,
                    "registry_path": str(registry_path),
                }
            )
            if match:
                match["runtime_transport"] = runtime_transport_for_match(match)
                return {"uri": uri, "resolution_order": order, "checks": checks, **match}
        elif step == "uri2ops":
            match = _match_uri2ops(scheme, uri, repo_root)
            checks.append({"registry": "uri2ops", "matched": match is not None})
            if match:
                match["runtime_transport"] = runtime_transport_for_match(match)
                return {"uri": uri, "resolution_order": order, "checks": checks, **match}
        elif step == "hypervisor":
            match = _match_hypervisor(scheme, uri)
            checks.append({"registry": "hypervisor", "matched": match is not None})
            if match:
                match["runtime_transport"] = runtime_transport_for_match(match)
                return {"uri": uri, "resolution_order": order, "checks": checks, **match}
        elif step == "denied":
            checks.append({"registry": "denied", "matched": True})
            break

    return {
        "uri": uri,
        "matched_registry": None,
        "resolution": "denied",
        "resolution_order": order,
        "checks": checks,
    }

from __future__ import annotations

from typing import Any

import httpx

from uri2ops.server.runtime_profiles import (
    export_environments_payload,
    operator_profile,
    validate_runtime_registry,
)
from uri3.paths import find_repo_root


def list_environments(
    *,
    root=None,
    operator: str = "",
    live: bool = False,
    base_url: str = "",
) -> dict[str, Any]:
    repo = root or find_repo_root()
    if live or operator or base_url:
        return _fetch_live_environments(operator=operator, base_url=base_url)
    payload = export_environments_payload(root=str(repo))
    errors = validate_runtime_registry(root=str(repo))
    return {
        "ok": not errors,
        "source": "config/runtime_environments.yaml",
        "errors": errors,
        "data": payload,
        "result_type": "environments",
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded" if not errors else "failed",
    }


def validate_environments(*, root=None) -> dict[str, Any]:
    repo = root or find_repo_root()
    errors = validate_runtime_registry(root=str(repo))
    return {
        "ok": not errors,
        "source": "config/runtime_environments.yaml",
        "errors": errors,
        "result_type": "environments_validate",
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded" if not errors else "failed",
    }


def _fetch_live_environments(*, operator: str, base_url: str) -> dict[str, Any]:
    url = _resolve_environments_url(operator=operator, base_url=base_url)
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        body = response.json()
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "source": url,
            "error": str(exc),
            "result_type": "environments",
            "workflow_status": "failed",
            "execution_status": "failed",
            "service_result_status": "failed",
        }
    return {
        "ok": bool(body.get("ok", True)),
        "source": url,
        "data": body,
        "result_type": "environments",
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded" if body.get("ok", True) else "failed",
    }


def _resolve_environments_url(*, operator: str, base_url: str) -> str:
    if base_url:
        return f"{base_url.rstrip('/')}/environments"
    if not operator:
        raise ValueError("Provide --operator or --base-url for live environments fetch")
    profile = operator_profile(operator)
    if profile is None:
        raise ValueError(f"Unknown operator deployment: {operator!r}")
    endpoints = profile.get("endpoints") or {}
    if endpoints.get("environments"):
        return str(endpoints["environments"])
    health = str(endpoints.get("health") or "")
    if health.endswith("/health"):
        return f"{health[: -len('/health')]}/environments"
    port = profile.get("port")
    if port:
        return f"http://127.0.0.1:{port}/environments"
    raise ValueError(f"Cannot resolve environments URL for operator {operator!r}")

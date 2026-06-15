from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from uri2run import run_backend
from uri2run.cli import _backend_from_target
from uri3.paths import find_repo_root

_SYSTEM_URI_SCHEMES = frozenset(
    {
        "agent-factory",
        "health",
        "hypervisor",
        "view",
        "repair",
        "runtime",
        "schema",
        "contract",
        "file",
        "log",
        "html",
        "markdown",
    }
)
_TOURI_RUNTIME_BACKENDS = frozenset(
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


def _uri_path_parts(uri: str) -> list[str]:
    parsed = urlparse(uri)
    if parsed.netloc:
        combined = f"{parsed.netloc}/{parsed.path.lstrip('/')}"
    else:
        combined = parsed.path.lstrip("/")
    return [part for part in combined.split("/") if part]


def _is_dashboard_view_uri(target: str) -> bool:
    """Only dashboard process/incident/workflow views use the view:// system handler."""
    if urlparse(target).scheme != "view":
        return False
    parts = _uri_path_parts(target)
    if len(parts) >= 4 and parts[0] == "process" and parts[1] == "agent" and parts[3] == "latest":
        return True
    if len(parts) >= 3 and parts[0] == "incident" and parts[2] == "explain":
        return True
    return len(parts) >= 3 and parts[0] == "workflow" and parts[2] == "timeline"


def _misrouted_view_hint(target: str) -> str | None:
    parsed = urlparse(target)
    if parsed.scheme != "view":
        return None
    parts = _uri_path_parts(target)
    if not parts:
        return None
    head = parts[0]
    if head in {"forecast", "weather", "maps"}:
        tail = "/".join(parts)
        return f"Did you mean weather://{tail}? view:// is for dashboard HTML views (e.g. view://process/agent/ID/latest)."
    return (
        "view:// is for dashboard views only: "
        "view://process/agent/{id}/latest, view://incident/{id}/explain, "
        "view://workflow/{id}/timeline. For weather HTML use weather://forecast/{place}/{days}/html."
    )


def _is_system_uri(target: str) -> bool:
    scheme = urlparse(target).scheme
    if scheme == "view":
        return _is_dashboard_view_uri(target)
    if scheme in _SYSTEM_URI_SCHEMES:
        return True
    return scheme == "resource" and target.startswith("resource://dashboard")


def _call_system_uri(
    target: str,
    payload: dict[str, Any],
    *,
    dry_run: bool,
    approve: bool,
) -> dict[str, Any]:
    from hypervisor_dashboard_agent.uri_client import call_system_uri

    try:
        body = call_system_uri(
            target,
            root=find_repo_root(strict=False),
            approved=approve,
            dry_run=dry_run,
            payload=payload,
        )
    except ValueError as exc:
        hint = _misrouted_view_hint(target)
        detail = str(exc)
        if hint:
            detail = f"{detail}. {hint}"
        return {
            "ok": False,
            "workflow_status": "failed",
            "execution_status": "failed",
            "service_result_status": "failed",
            "result_type": "error",
            "error": detail,
            "meta": {"runtime": "urish", "transport": "hypervisor:system_uri", "target": target},
        }
    ok = body.get("ok")
    if ok is None:
        ok = (
            body.get("service_status") not in {"failed", "unhealthy"}
            and body.get("result_type") != "error"
        )
    return {
        "ok": bool(ok),
        "workflow_status": "completed" if ok else "failed",
        "execution_status": "completed" if ok else "failed",
        "service_result_status": "succeeded" if ok else "failed",
        "result_type": body.get("result_type", "system_uri"),
        "data": body,
        "meta": {"runtime": "urish", "transport": "hypervisor:system_uri", "target": target},
    }


def _operation_from_uri(target: str, operations: list[str] | None = None) -> str:
    parsed = urlparse(target)
    parts = [part for part in parsed.path.split("/") if part]
    if parsed.scheme == "robot" and "mission" in parts and parts[-1:] == ["start"]:
        return "mission_start"
    if parts:
        candidate = parts[-1]
        if not operations or candidate in operations:
            return candidate
    return operations[0] if operations else "call"


def _backend_from_explain(target: str, explain: dict[str, Any]) -> dict[str, Any] | None:
    matched = str(explain.get("matched_registry") or "")
    if matched == "touri":
        backend = dict(explain.get("backend") or {})
        backend_type = str(backend.get("type") or "")
        if backend_type in _TOURI_RUNTIME_BACKENDS:
            return backend
        return {
            "type": "touri",
            "target": target,
            "registry": _registry_path_from_explain(explain),
        }
    if matched == "uri2ops":
        parsed = urlparse(target)
        operations = [str(item) for item in explain.get("operations") or []]
        return {
            "type": "uri2ops",
            "uri": target,
            "scheme": parsed.scheme,
            "operation": _operation_from_uri(target, operations),
        }
    return None


def _registry_path_from_explain(explain: dict[str, Any]) -> str:
    for check in explain.get("checks") or []:
        if isinstance(check, dict) and check.get("registry") == "touri":
            path = check.get("registry_path")
            if path:
                return str(path)
    return str(find_repo_root(strict=False) / "examples" / "20_touri_capabilities")


def call_uri(
    target: str,
    payload: dict[str, Any],
    *,
    backend_type: str = "",
    timeout: float = 30.0,
    dry_run: bool = False,
    policy_options: Any | None = None,
    context_policy: str | None = None,
) -> dict[str, Any]:
    if policy_options is not None:
        from urish.policy import evaluate_policy

        allowed, reason, force_dry_run = evaluate_policy(
            target,
            options=policy_options,
            context_policy=context_policy,
        )
        if not allowed:
            return {
                "ok": False,
                "policy_blocked": True,
                "workflow_status": "blocked",
                "execution_status": "blocked",
                "service_result_status": "failed",
                "result_type": "policy",
                "error": reason,
                "meta": {"runtime": "urish", "transport": "policy", "target": target},
            }
        if force_dry_run:
            dry_run = True

    if _is_system_uri(target):
        return _call_system_uri(
            target,
            payload,
            dry_run=dry_run,
            approve=bool(policy_options.approve) if policy_options else False,
        )

    if dry_run:
        from urish.backends.explain import explain_target

        plan = explain_target(target)
        return {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "plan",
            "data": {"target": target, "payload": payload, "explain": plan},
            "meta": {"runtime": "urish", "transport": "dry-run", "target": target},
        }
    context = {
        "timeout": timeout,
        "root": str(find_repo_root(strict=False)),
        "uri": target,
        "scheme": urlparse(target).scheme,
    }
    if backend_type:
        backend = _backend_from_target(target, backend_type=backend_type)
    else:
        from urish.backends.explain import explain_target

        explain = explain_target(target)
        backend = _backend_from_explain(target, explain)
        if backend is None:
            error = f"No executable backend for URI: {target}"
            hint = _misrouted_view_hint(target)
            if hint:
                error = f"{error}. {hint}"
            return {
                "ok": False,
                "workflow_status": "failed",
                "execution_status": "failed",
                "service_result_status": "failed",
                "result_type": "resolution",
                "error": error,
                "data": {"explain": explain},
                "meta": {"runtime": "urish", "transport": "resolution", "target": target},
            }
        context.update(
            {
                "capability": explain.get("capability"),
                "operation": backend.get("operation") or explain.get("operation"),
            }
        )
    result = run_backend(backend, payload, context)
    body = result.to_dict()
    body.setdefault("meta", {})
    body["meta"]["runtime"] = body["meta"].get("runtime") or "uri2run"
    return body

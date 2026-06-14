from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from hypervisor.deployment_registry.loader import load_deployment_registry
from hypervisor.deployment_registry.runtime_state import load_runtime_state
from hypervisor.deployment_registry.supervisor import inspect_agent
from hypervisor.paths import find_repo_root
from hypervisor.repair.supervisor import diagnose_agent, repair_apply

from hypervisor_dashboard_agent.models import ViewEnvelope
from hypervisor_dashboard_agent.view_builder import build_process_view, render_process_html


@dataclass(frozen=True)
class _SystemUriRequest:
    uri: str
    repo: Path
    approved: bool
    dry_run: bool
    payload: dict[str, Any] | None
    scheme: str
    parts: list[str]


_SystemUriHandler = Callable[[_SystemUriRequest], dict[str, Any]]


def _repo_root(root: Path | None = None) -> Path:
    return root or find_repo_root()


def _uri_path_parts(uri: str) -> list[str]:
    parsed = urlparse(uri)
    if parsed.netloc:
        combined = f"{parsed.netloc}/{parsed.path.lstrip('/')}"
    else:
        combined = parsed.path.lstrip("/")
    return [part for part in combined.split("/") if part]


def list_agent_deployments(*, root: Path | None = None) -> list[dict[str, Any]]:
    registry = load_deployment_registry(root=_repo_root(root))
    items: list[dict[str, Any]] = []
    for deployment in registry.deployments:
        items.append(
            {
                "id": deployment.id,
                "agent_ref": deployment.agent_ref,
                "target_uri": deployment.target_uri,
                "status": deployment.status,
                "health_uri": deployment.health_uri,
                "view_uri": f"view://process/agent/{deployment.id}/latest",
            }
        )
    return items


def resolve_view_uri(view_uri: str, *, root: Path | None = None) -> ViewEnvelope:
    parsed = urlparse(view_uri)
    if parsed.scheme != "view":
        raise ValueError(f"unsupported view URI scheme: {view_uri}")
    parts = _uri_path_parts(view_uri)
    if len(parts) >= 4 and parts[0] == "process" and parts[1] == "agent" and parts[3] == "latest":
        agent_id = parts[2]
        model = build_process_view(agent_id, root=_repo_root(root))
        html = render_process_html(model)
        return ViewEnvelope(
            view_uri=view_uri,
            content_type="text/html",
            title=model.title,
            data=model.to_dict(),
            html=html,
        )
    if len(parts) >= 3 and parts[0] == "incident" and parts[2] == "explain":
        incident_id = parts[1]
        return ViewEnvelope(
            view_uri=view_uri,
            content_type="application/json",
            title=f"Incident {incident_id}",
            data={"incident_id": incident_id, "status": "planned"},
        )
    raise ValueError(f"unsupported view URI: {view_uri}")


def _normalize_view_uri(uri: str) -> str | None:
    parsed = urlparse(uri)
    parts = _uri_path_parts(uri)
    if parsed.scheme == "view":
        return uri
    if parsed.scheme == "resource" and parts and parts[0] == "dashboard":
        tail = parts[1:]
        if tail[:2] == ["repair", "agent"] and len(tail) >= 4 and tail[3] == "diagnosis":
            return f"repair://agent/{tail[2]}/diagnose"
        return "view://" + "/".join(tail)
    return None


def _handle_view_uri(
    uri: str,
    *,
    repo: Path,
    approved: bool,
    dry_run: bool,
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    normalized = _normalize_view_uri(uri)
    if normalized and normalized.startswith("repair://"):
        return call_system_uri(normalized, root=repo, approved=approved, dry_run=dry_run, payload=payload)
    if normalized:
        return resolve_view_uri(normalized, root=repo).to_dict()
    raise ValueError(f"unsupported dashboard resource URI: {uri}")


def _handle_runtime_uri(parts: list[str], *, repo: Path) -> dict[str, Any]:
    agent_id = parts[1]
    state = load_runtime_state(agent_id, repo) or {}
    return {"result_type": "runtime_state", "agent_id": agent_id, "state": state}


def _handle_health_uri(parts: list[str], *, repo: Path) -> dict[str, Any]:
    agent_id = parts[1]
    inspection = inspect_agent(agent_id, root=repo)
    return {
        "result_type": "health",
        "agent_id": agent_id,
        "ok": inspection.get("health", {}).get("ok"),
        "health": inspection.get("health"),
        "service_status": inspection.get("service_status"),
    }


def _handle_repair_uri(
    parts: list[str],
    *,
    repo: Path,
    approved: bool,
    dry_run: bool,
) -> dict[str, Any]:
    agent_id = parts[1]
    action = parts[2]
    if action == "diagnose":
        return diagnose_agent(agent_id, root=repo)
    if action == "apply":
        if dry_run:
            diagnosis = diagnose_agent(agent_id, root=repo)
            return {
                "result_type": "repair",
                "dry_run": True,
                "diagnosis": diagnosis,
                "repair_plan": diagnosis.get("repair_plan"),
            }
        return repair_apply(agent_id, root=repo, approved=approved, safe=True)
    raise ValueError(f"unsupported repair action: {action}")


def _handle_log_uri(uri: str, *, repo: Path) -> dict[str, Any]:
    from uri3.logs.reader import read_logs_result

    entries = read_logs_result(uri, root=repo)
    return {"result_type": "logs", "uri": uri, "entries": entries}


def _is_view_request(request: _SystemUriRequest) -> bool:
    return request.scheme == "view" or (
        request.scheme == "resource" and bool(request.parts) and request.parts[0] == "dashboard"
    )


def _is_runtime_request(request: _SystemUriRequest) -> bool:
    return (
        request.scheme == "runtime"
        and len(request.parts) >= 3
        and request.parts[0] == "agent"
        and request.parts[2] == "state"
    )


def _is_health_request(request: _SystemUriRequest) -> bool:
    return request.scheme == "health" and len(request.parts) >= 2 and request.parts[0] == "agent"


def _is_repair_request(request: _SystemUriRequest) -> bool:
    return request.scheme == "repair" and len(request.parts) >= 3 and request.parts[0] == "agent"


def _view_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_view_uri(
        request.uri,
        repo=request.repo,
        approved=request.approved,
        dry_run=request.dry_run,
        payload=request.payload,
    )


def _runtime_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_runtime_uri(request.parts, repo=request.repo)


def _health_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_health_uri(request.parts, repo=request.repo)


def _repair_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_repair_uri(
        request.parts,
        repo=request.repo,
        approved=request.approved,
        dry_run=request.dry_run,
    )


def _log_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_log_uri(request.uri, repo=request.repo)


_SYSTEM_URI_DISPATCH: tuple[tuple[Callable[[_SystemUriRequest], bool], _SystemUriHandler], ...] = (
    (_is_view_request, _view_request),
    (_is_runtime_request, _runtime_request),
    (_is_health_request, _health_request),
    (_is_repair_request, _repair_request),
    (lambda request: request.scheme == "log", _log_request),
)


def _select_system_uri_handler(request: _SystemUriRequest) -> _SystemUriHandler | None:
    for matches, handler in _SYSTEM_URI_DISPATCH:
        if matches(request):
            return handler
    return None


def call_system_uri(
    uri: str,
    *,
    root: Path | None = None,
    approved: bool = False,
    dry_run: bool = False,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo = _repo_root(root)
    parsed = urlparse(uri)
    request = _SystemUriRequest(
        uri=uri,
        repo=repo,
        approved=approved,
        dry_run=dry_run,
        payload=payload,
        scheme=parsed.scheme,
        parts=_uri_path_parts(uri),
    )
    handler = _select_system_uri_handler(request)
    if handler:
        return handler(request)

    if dry_run:
        return {
            "ok": True,
            "result_type": "dry_run",
            "uri": uri,
            "payload": payload or {},
            "status": "preview",
            "service_result_status": "preview",
            "workflow_status": "planned",
        }

    raise ValueError(f"unsupported or unimplemented URI: {uri}")

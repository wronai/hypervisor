from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import yaml
from hypervisor.deployment_registry.loader import load_deployment_registry
from hypervisor.deployment_registry.runtime_state import load_runtime_state
from hypervisor.deployment_registry.supervisor import inspect_agent
from hypervisor.paths import find_repo_root
from hypervisor.repair.supervisor import diagnose_agent, repair_apply, supervise_with_repair

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
    artifact_root: Path | None = None


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


def uri_implies_dry_run(uri: str) -> bool:
    """True when the URI path ends with a dry-run segment (e.g. workflow://…/dry-run)."""
    parts = _uri_path_parts(uri)
    return bool(parts) and parts[-1] == "dry-run"


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
        return call_system_uri(
            normalized, root=repo, approved=approved, dry_run=dry_run, payload=payload
        )
    if normalized:
        view = resolve_view_uri(normalized, root=repo).to_dict()
        return {
            "ok": True,
            "workflow_status": "completed",
            "service_result_status": "succeeded",
            **view,
        }
    raise ValueError(f"unsupported dashboard resource URI: {uri}")


def _handle_runtime_uri(parts: list[str], *, repo: Path) -> dict[str, Any]:
    agent_id = parts[1]
    state = load_runtime_state(agent_id, repo) or {}
    return {
        "ok": True,
        "result_type": "runtime_state",
        "workflow_status": "completed",
        "service_result_status": "succeeded",
        "agent_id": agent_id,
        "state": state,
    }


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


def _contract_path_for_agent(agent_id: str, *, repo: Path) -> Path | None:
    registry = load_deployment_registry(root=repo)
    deployment = registry.by_id(agent_id)
    if deployment is None:
        return None
    contract = deployment.metadata.get("contract")
    if contract:
        return repo / str(contract)
    if deployment.target_uri.startswith("local://agents/generated/"):
        package = deployment.target_uri.rsplit("/", 1)[-1]
        return repo / "contracts" / "agents" / f"{package}.yaml"
    return None


def _schema_refs_from_capabilities(capabilities: list[dict[str, Any]]) -> dict[str, list[str]]:
    input_refs: list[str] = []
    output_refs: list[str] = []
    for capability in capabilities:
        input_schema = capability.get("input_schema")
        output_schema = capability.get("output_schema")
        if input_schema:
            input_refs.append(str(input_schema))
        if output_schema:
            output_refs.append(str(output_schema))
    return {
        "input": sorted(set(input_refs)),
        "output": sorted(set(output_refs)),
    }


def _read_contract(path: Path | None) -> tuple[str | None, dict[str, Any] | None]:
    if path is None:
        return None, None
    contract_uri = f"file://{path.resolve().as_posix()}"
    if not path.is_file():
        return contract_uri, None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return contract_uri, data if isinstance(data, dict) else None


def _handle_schema_uri(parts: list[str], *, repo: Path) -> dict[str, Any]:
    if len(parts) < 2 or parts[0] != "agent":
        raise ValueError("schema:// supports schema://agent/{deployment_id}")
    agent_id = parts[1]
    registry = load_deployment_registry(root=repo)
    deployment = registry.by_id(agent_id)
    if deployment is None:
        return {
            "ok": False,
            "result_type": "agent_schema",
            "workflow_status": "completed_with_service_error",
            "service_result_status": "failed",
            "agent_id": agent_id,
            "error": f"Deployment not found: {agent_id}",
        }

    inspection = inspect_agent(agent_id, root=repo)
    card_probe = inspection.get("card") or {}
    card_payload = card_probe.get("payload") if isinstance(card_probe, dict) else None
    card_payload = card_payload if isinstance(card_payload, dict) else None
    contract_uri, contract = _read_contract(_contract_path_for_agent(agent_id, repo=repo))
    contract_capabilities = (contract or {}).get("capabilities") or []
    runtime_capabilities = (card_payload or {}).get("capabilities") or []
    capabilities = runtime_capabilities or contract_capabilities
    capabilities = [item for item in capabilities if isinstance(item, dict)]

    effective_health_uri = inspection.get("effective_health_uri") or deployment.health_uri
    card_uri = card_probe.get("uri") if isinstance(card_probe, dict) else None
    card_uri = card_uri or deployment.card_uri
    return {
        "ok": bool(card_payload or contract),
        "result_type": "agent_schema",
        "workflow_status": "completed",
        "service_result_status": "succeeded" if card_payload or contract else "failed",
        "agent_id": agent_id,
        "agent_ref": deployment.agent_ref,
        "deployment_id": deployment.id,
        "target_uri": deployment.target_uri,
        "health_uri": effective_health_uri,
        "card_uri": card_uri,
        "contract_uri": contract_uri,
        "card": card_payload,
        "contract": contract,
        "capabilities": capabilities,
        "schemas": _schema_refs_from_capabilities(capabilities),
        "related_uris": {
            "health": f"health://agent/{agent_id}",
            "view": f"view://process/agent/{agent_id}/latest",
            "runtime": f"runtime://agent/{agent_id}/state",
            "schema": f"schema://agent/{agent_id}",
            "contract": _contract_uri_for_schema(agent_id, contract_uri, repo=repo),
            "card": card_uri,
        },
    }


def _contract_uri_for_schema(agent_id: str, file_uri: str | None, *, repo: Path) -> str | None:
    from hypervisor.contract_registry.uri_resolver import resolve_contract_path

    path = resolve_contract_path(agent_id, repo)
    if path is not None:
        agent = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        agent_name = str((agent.get("agent") or {}).get("name") or agent_id)
        return f"contract://agent/{agent_name}"
    if file_uri and file_uri.startswith("file://"):
        stem = Path(file_uri.removeprefix("file://")).stem
        return f"contract://agents/{stem}"
    return None


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
                "ok": True,
                "result_type": "repair",
                "uri": f"repair://agent/{agent_id}/apply",
                "dry_run": True,
                "workflow_status": "planned",
                "service_result_status": "preview",
                "diagnosis": diagnosis,
                "repair_plan": diagnosis.get("repair_plan"),
            }
        return repair_apply(agent_id, root=repo, approved=approved, safe=True)
    if action == "auto":
        if dry_run:
            diagnosis = diagnose_agent(agent_id, root=repo)
            return {
                "ok": True,
                "result_type": "repair",
                "uri": f"repair://agent/{agent_id}/auto",
                "dry_run": True,
                "workflow_status": "planned",
                "service_result_status": "preview",
                "agent_id": agent_id,
                "diagnosis": diagnosis,
                "repair_plan": diagnosis.get("repair_plan"),
                "planned_action": "supervise_with_repair",
            }
        return supervise_with_repair(
            agent_id,
            root=repo,
            repair="auto",
            learn=False,
        )
    raise ValueError(f"unsupported repair action: {action}")


def _query_params(uri: str) -> dict[str, str]:
    parsed = urlparse(uri)
    return {
        key: values[-1]
        for key, values in parse_qs(parsed.query, keep_blank_values=True).items()
        if values
    }


def _bool_param(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).lower() in {"1", "true", "yes", "y", "on"}


def _int_param(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    return int(value)


def _handle_agent_factory_uri(request: _SystemUriRequest) -> dict[str, Any]:
    if len(request.parts) < 2 or request.parts[0] != "generate":
        raise ValueError(f"unsupported agent factory URI: {request.uri}")
    from urish.backends.agent_factory import generate_agent_from_prompt

    params = _query_params(request.uri)
    payload = request.payload or {}
    agent_id = request.parts[1]
    prompt = str(payload.get("prompt") or params.get("prompt") or f"create agent {agent_id}")
    overwrite = _bool_param(payload.get("overwrite", params.get("overwrite")), default=False)
    port = _int_param(payload.get("port", params.get("port")))
    result = generate_agent_from_prompt(
        prompt,
        name=agent_id,
        port=port,
        dry_run=request.dry_run,
        approve=request.approved,
        overwrite=overwrite,
        root=request.repo,
    )
    result.setdefault("uri", request.uri)
    return result


def _handle_hypervisor_agent_uri(request: _SystemUriRequest) -> dict[str, Any]:
    if len(request.parts) < 3 or request.parts[0] != "agent":
        raise ValueError(f"unsupported hypervisor URI: {request.uri}")
    from hypervisor.deployment_registry.runner import run_agent

    deployment_id = request.parts[1]
    action = request.parts[2]
    if action != "run":
        raise ValueError(f"unsupported hypervisor agent action: {action}")
    if request.dry_run:
        try:
            return run_agent(deployment_id, root=request.repo, dry_run=True, detach=True)
        except Exception as exc:
            return {
                "ok": True,
                "result_type": "lifecycle_plan",
                "workflow_status": "planned",
                "service_result_status": "preview",
                "uri": request.uri,
                "deployment_id": deployment_id,
                "pending_dependency": "deployment registry entry",
                "note": str(exc),
            }
    return run_agent(
        deployment_id,
        root=request.repo,
        detach=True,
        wait_healthy=True,
        if_running="reuse",
    )


def _handle_log_uri(uri: str, *, repo: Path) -> dict[str, Any]:
    from uri3.logs.reader import read_logs_result

    entries = read_logs_result(uri, root=repo)
    return {
        "ok": True,
        "result_type": "logs",
        "workflow_status": "completed",
        "service_result_status": "succeeded",
        "uri": uri,
        "entries": entries,
    }


def _is_presentation_request(request: _SystemUriRequest) -> bool:
    return request.scheme in {"html", "markdown"}


def _html_request(request: _SystemUriRequest) -> dict[str, Any]:
    from hypervisor_dashboard_agent.presentation import resolve_html_presentation

    return resolve_html_presentation(request.uri, root=request.repo)


def _markdown_request(request: _SystemUriRequest) -> dict[str, Any]:
    from hypervisor_dashboard_agent.presentation import resolve_markdown_presentation

    return resolve_markdown_presentation(request.uri, root=request.repo)


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


def _is_contract_request(request: _SystemUriRequest) -> bool:
    return request.scheme == "contract"


def _contract_request(request: _SystemUriRequest) -> dict[str, Any]:
    from hypervisor.contract_registry.uri_resolver import handle_contract_uri

    return handle_contract_uri(request.uri, request.repo)


def _is_schema_request(request: _SystemUriRequest) -> bool:
    return request.scheme == "schema" and len(request.parts) >= 2 and request.parts[0] == "agent"


def _is_repair_request(request: _SystemUriRequest) -> bool:
    return request.scheme == "repair" and len(request.parts) >= 3 and request.parts[0] == "agent"


def _is_agent_factory_request(request: _SystemUriRequest) -> bool:
    return request.scheme == "agent-factory"


def _is_hypervisor_agent_request(request: _SystemUriRequest) -> bool:
    return (
        request.scheme == "hypervisor"
        and len(request.parts) >= 3
        and request.parts[0] == "agent"
    )


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


def _schema_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_schema_uri(request.parts, repo=request.repo)


def _repair_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_repair_uri(
        request.parts,
        repo=request.repo,
        approved=request.approved,
        dry_run=request.dry_run,
    )


def _agent_factory_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_agent_factory_uri(request)


def _hypervisor_agent_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_hypervisor_agent_uri(request)


def _log_request(request: _SystemUriRequest) -> dict[str, Any]:
    return _handle_log_uri(request.uri, repo=request.repo)


def _file_request(request: _SystemUriRequest) -> dict[str, Any]:
    from uri3.resolvers.resolve_core import resolve

    resolved = resolve(request.uri)
    return {
        "ok": True,
        "result_type": "file",
        "workflow_status": "completed",
        "service_result_status": "succeeded",
        "uri": request.uri,
        "data": resolved.target,
    }


def _is_touri_run_request(request: _SystemUriRequest) -> bool:
    return request.scheme in {"workflow", "flow", "cron"}


def _touri_run_request(request: _SystemUriRequest) -> dict[str, Any]:
    from urish.backends.run import run_target

    effective_dry_run = request.dry_run or uri_implies_dry_run(request.uri)
    approve = request.approved and not effective_dry_run
    return run_target(
        request.uri,
        approve=approve,
        dry_run=effective_dry_run,
        adapter="mock",
        payload=request.payload,
        artifact_root=request.artifact_root or request.repo,
    )


def _is_http_request(request: _SystemUriRequest) -> bool:
    return request.scheme in {"http", "https"}


_OPERATOR_SCHEMES = frozenset(
    {"browser", "dom", "screen", "input", "android", "pcwin", "robot", "device"}
)


def _infer_operator_operation(parts: list[str]) -> str:
    if not parts:
        return "call"
    if parts[-1] == "dry-run" and len(parts) > 1:
        return parts[-2]
    if "mission" in parts and parts[-1] == "start":
        return "mission_start"
    return parts[-1]


def _is_operator_request(request: _SystemUriRequest) -> bool:
    return request.scheme in _OPERATOR_SCHEMES


def _operator_request(request: _SystemUriRequest) -> dict[str, Any]:
    from uri2run.transports.uri2ops_transport import run_uri2ops

    effective_dry_run = request.dry_run or uri_implies_dry_run(request.uri)
    if effective_dry_run:
        from urish.backends.explain import explain_target

        return {
            "ok": True,
            "result_type": "plan",
            "workflow_status": "planned",
            "service_result_status": "preview",
            "uri": request.uri,
            "dry_run": True,
            "explain": explain_target(request.uri),
        }

    operation = _infer_operator_operation(request.parts)
    payload = dict(request.payload or {})
    payload.setdefault("adapter", "mock")
    if request.scheme == "browser" and operation == "open" and "url" not in payload:
        payload.setdefault("url", "https://supplier-portal.example.local/reports/monthly")
    result = run_uri2ops(
        request.uri,
        request.scheme,
        operation,
        payload,
        {
            "root": str(request.repo),
            "dry_run": False,
            "approve": request.approved,
        },
    )
    body = result.to_dict()
    body.setdefault("result_type", "operator")
    body.setdefault("uri", request.uri)
    return body


def _http_request(request: _SystemUriRequest) -> dict[str, Any]:
    import httpx

    try:
        response = httpx.get(request.uri, timeout=15.0, follow_redirects=True)
    except httpx.HTTPError as exc:
        return {
            "ok": False,
            "result_type": "http",
            "workflow_status": "completed_with_service_error",
            "service_result_status": "failed",
            "uri": request.uri,
            "error": str(exc),
        }
    payload: Any
    json_ok = False
    try:
        payload = response.json()
        json_ok = isinstance(payload, dict)
    except Exception:
        payload = response.text[:2000]
    return {
        "ok": response.is_success,
        "result_type": "http",
        "workflow_status": "completed",
        "service_result_status": "succeeded" if response.is_success else "failed",
        "uri": request.uri,
        "status_code": response.status_code,
        "json_ok": json_ok,
        "payload": payload,
    }


def _presentation_request(request: _SystemUriRequest) -> dict[str, Any]:
    if request.scheme == "html":
        return _html_request(request)
    return _markdown_request(request)


_SYSTEM_URI_DISPATCH: tuple[tuple[Callable[[_SystemUriRequest], bool], _SystemUriHandler], ...] = (
    (_is_presentation_request, _presentation_request),
    (_is_view_request, _view_request),
    (_is_runtime_request, _runtime_request),
    (_is_health_request, _health_request),
    (_is_schema_request, _schema_request),
    (_is_contract_request, _contract_request),
    (_is_repair_request, _repair_request),
    (_is_agent_factory_request, _agent_factory_request),
    (_is_hypervisor_agent_request, _hypervisor_agent_request),
    (lambda request: request.scheme == "log", _log_request),
    (lambda request: request.scheme == "file", _file_request),
    (_is_touri_run_request, _touri_run_request),
    (_is_operator_request, _operator_request),
    (_is_http_request, _http_request),
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
    artifact_root: Path | None = None,
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
        artifact_root=artifact_root,
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

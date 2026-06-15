from __future__ import annotations

from typing import Any

from uri2flow import expand_flow
from uri3.results import ServiceResult

from uri2run.result import error_result
from uri2run.transports.paths import resolve_path
from uri2run.transports.workflow_transport import run_workflow_from_graph_dict


def run_uri_flow(
    flow_path: str,
    payload: dict[str, Any],
    context: dict[str, Any],
    *,
    backend_extra: dict[str, Any] | None = None,
) -> ServiceResult:
    path = resolve_path(flow_path, context)
    if not path.is_file():
        return error_result("FLOW_NOT_FOUND", f"Flow file not found: {path}")

    try:
        graph = expand_flow(path)
    except Exception as exc:
        return error_result("FLOW_EXPAND_FAILED", str(exc))

    return run_workflow_from_graph_dict(
        graph,
        source_key="flow",
        source_path=path,
        payload=payload,
        context=context,
        backend_extra=backend_extra,
        transport="uri_flow",
        invalid_code="FLOW_INVALID",
    )


def run_flow_transport(
    backend: dict[str, Any],
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    flow = backend.get("flow")
    if not flow:
        return error_result("BACKEND_INVALID", "uri_flow backend missing flow")
    return run_uri_flow(str(flow), payload, context, backend_extra=backend)

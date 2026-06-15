from __future__ import annotations

from typing import Any

import yaml
from uri3.results import ServiceResult

from uri2run.result import error_result
from uri2run.transports.paths import resolve_path
from uri2run.transports.workflow_transport import run_workflow_from_graph_dict


def _load_graph(path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected workflow graph mapping in {path}")
    return data


def run_uri_graph(
    graph_path: str,
    payload: dict[str, Any],
    context: dict[str, Any],
    *,
    backend_extra: dict[str, Any] | None = None,
) -> ServiceResult:
    path = resolve_path(graph_path, context)
    if not path.is_file():
        return error_result("GRAPH_NOT_FOUND", f"Graph file not found: {path}")

    try:
        graph = _load_graph(path)
    except Exception as exc:
        return error_result("GRAPH_LOAD_FAILED", str(exc))

    return run_workflow_from_graph_dict(
        graph,
        source_key="graph",
        source_path=path,
        payload=payload,
        context=context,
        backend_extra=backend_extra,
        transport="uri_graph",
        invalid_code="GRAPH_INVALID",
    )


def run_graph_transport(
    backend: dict[str, Any],
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    graph = backend.get("graph")
    if not graph:
        return error_result("BACKEND_INVALID", "uri_graph backend missing graph")
    return run_uri_graph(str(graph), payload, context, backend_extra=backend)

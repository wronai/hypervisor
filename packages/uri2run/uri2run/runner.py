from __future__ import annotations

from collections.abc import Callable
from typing import Any

from uri2run.result import error_result
from uri2run.transports import run_http, run_mock, run_python, run_shell
from uri2run.transports import run_uri2ops, run_uri_flow, run_uri_graph
from uri3.results import ServiceResult


def unsupported_backend(backend_type: str) -> ServiceResult:
    return error_result(
        "BACKEND_UNSUPPORTED",
        f"Backend type not implemented yet: {backend_type}",
        result_type="unsupported_backend",
    )


def _backend_target(backend: dict[str, Any], key: str, detail: str) -> str | ServiceResult:
    value = backend.get(key)
    if value:
        return str(value)
    return error_result("BACKEND_INVALID", detail)


def _run_python(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = _backend_target(backend, "target", "python backend missing target")
    if isinstance(target, ServiceResult):
        return target
    return run_python(target, payload, context)


def _run_shell(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    command = _backend_target(backend, "command", "shell backend missing command")
    if isinstance(command, ServiceResult):
        return command
    return run_shell(command, payload, context)


def _run_http(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "http backend missing target/url")
    return run_http(str(target), payload, context)


def _run_flow(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    flow = _backend_target(backend, "flow", "uri_flow backend missing flow")
    if isinstance(flow, ServiceResult):
        return flow
    return run_uri_flow(flow, payload, context, backend_extra=backend)


def _run_graph(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    graph = _backend_target(backend, "graph", "uri_graph backend missing graph")
    if isinstance(graph, ServiceResult):
        return graph
    return run_uri_graph(graph, payload, context, backend_extra=backend)


def _run_uri2ops(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    scheme = str(context.get("scheme") or backend.get("scheme") or "")
    operation = str(backend.get("operation") or context.get("operation") or "call")
    uri = str(context.get("uri") or backend.get("uri") or "")
    if not uri or not scheme:
        return error_result("BACKEND_INVALID", "uri2ops backend missing uri/scheme context")
    return run_uri2ops(uri, scheme, operation, payload, context, backend_extra=backend)


_BACKEND_HANDLERS: dict[
    str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], ServiceResult]
] = {
    "python": _run_python,
    "shell": _run_shell,
    "http": _run_http,
    "https": _run_http,
    "mock": lambda _backend, payload, context: run_mock(payload, context),
    "uri_flow": _run_flow,
    "uri_graph": _run_graph,
    "uri2ops": _run_uri2ops,
}


def run_backend(
    backend: dict[str, Any],
    payload: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> ServiceResult:
    backend_type = str(backend.get("type") or "")
    handler = _BACKEND_HANDLERS.get(backend_type)
    if handler is None:
        return unsupported_backend(backend_type)
    return handler(dict(backend), dict(payload or {}), dict(context or {}))


def run_target(
    target: str,
    payload: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> ServiceResult:
    if target.startswith("python://"):
        return run_backend({"type": "python", "target": target}, payload, context)
    if target.startswith("shell://"):
        return run_backend({"type": "shell", "command": target.removeprefix("shell://")}, payload, context)
    if target.startswith(("http://", "https://")):
        return run_backend({"type": "http", "target": target}, payload, context)
    return unsupported_backend(target.split(":", 1)[0] if ":" in target else target)

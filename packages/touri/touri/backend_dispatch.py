from __future__ import annotations

from collections.abc import Callable
from typing import Any

from uri2run import run_backend

from touri.backends import call_mock_backend
from touri.models import ServiceResult, service_result
from touri.runtime_adapter import backend_to_dict

_URI2RUN_TYPES = frozenset(
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
    }
)


def invalid_backend(code: str, detail: str) -> ServiceResult:
    return service_result(ok=False, result_type="error", errors=[{"code": code, "detail": detail}])


def unsupported_backend(backend_type: str, *, fallback: bool = False) -> ServiceResult:
    detail = (
        f"fallback backend not implemented: {backend_type}"
        if fallback
        else f"Backend type not implemented yet: {backend_type}"
    )
    error = {"detail": detail}
    if fallback:
        error["code"] = "FALLBACK_BACKEND_UNSUPPORTED"
    return service_result(
        ok=False,
        result_type="unsupported_backend",
        errors=[error],
    )


def backend_error(detail: str) -> ServiceResult:
    return service_result(ok=False, result_type="error", errors=[{"detail": detail}])


def _dispatch_uri2run(
    backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]
) -> ServiceResult:
    return run_backend(backend, payload, context)


def _call_python_backend(
    backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]
) -> ServiceResult:
    target = backend.get("target")
    if not target:
        return invalid_backend("FALLBACK_BACKEND_INVALID", "python fallback missing target")
    return _dispatch_uri2run({**backend, "type": "python", "target": str(target)}, payload, context)


def _call_shell_backend(
    backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]
) -> ServiceResult:
    command = backend.get("command")
    if not command:
        return invalid_backend("FALLBACK_BACKEND_INVALID", "shell fallback missing command")
    return _dispatch_uri2run(
        {**backend, "type": "shell", "command": str(command)}, payload, context
    )


def _call_uri_flow_backend(
    backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]
) -> ServiceResult:
    flow = backend.get("flow")
    if not flow:
        return invalid_backend("FALLBACK_BACKEND_INVALID", "uri_flow fallback missing flow")
    return _dispatch_uri2run({**backend, "type": "uri_flow", "flow": str(flow)}, payload, context)


def _call_uri_graph_backend(
    backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]
) -> ServiceResult:
    graph = backend.get("graph")
    if not graph:
        return invalid_backend("FALLBACK_BACKEND_INVALID", "uri_graph fallback missing graph")
    return _dispatch_uri2run(
        {**backend, "type": "uri_graph", "graph": str(graph)}, payload, context
    )


def _call_uri2ops_fallback(
    backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]
) -> ServiceResult:
    scheme = str(context.get("scheme") or "")
    operation = str(backend.get("operation") or context.get("operation") or "call")
    uri = str(context.get("uri") or "")
    if not uri or not scheme:
        return invalid_backend(
            "FALLBACK_BACKEND_INVALID", "uri2ops fallback missing uri/scheme context"
        )
    from touri.backends import call_uri2ops_backend

    return call_uri2ops_backend(uri, scheme, operation, payload, context, backend_extra=backend)


_BACKEND_HANDLERS: dict[
    str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], ServiceResult]
] = {
    "python": _call_python_backend,
    "shell": _call_shell_backend,
    "http": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "https": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "stdio": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "sse": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "ws": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "docker": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "ssh": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "mcp": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "a2a": lambda backend, payload, context: _dispatch_uri2run(backend, payload, context),
    "mock": lambda _backend, payload, context: call_mock_backend(payload, context),
    "uri_flow": _call_uri_flow_backend,
    "uri_graph": _call_uri_graph_backend,
    "uri2ops": _call_uri2ops_fallback,
}


def call_backend(
    backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]
) -> ServiceResult:
    backend_type = str(backend.get("type") or "")
    if backend_type in _URI2RUN_TYPES:
        return _dispatch_uri2run(backend, payload, context)
    handler = _BACKEND_HANDLERS.get(backend_type)
    if handler is None:
        return unsupported_backend(backend_type, fallback=True)
    return handler(backend, payload, context)


def _call_primary_python(backend, _manifest, _uri, final_payload, ctx) -> ServiceResult:
    if not backend.target:
        return backend_error("python backend missing target")
    return run_backend(backend_to_dict(backend), final_payload, ctx)


def _call_primary_shell(backend, _manifest, _uri, final_payload, ctx) -> ServiceResult:
    if not backend.command:
        return backend_error("shell backend missing command")
    return run_backend(backend_to_dict(backend), final_payload, ctx)


def _call_primary_http(backend, _manifest, _uri, final_payload, ctx) -> ServiceResult:
    if not backend.url:
        return backend_error("http backend missing url")
    return run_backend(backend_to_dict(backend), final_payload, ctx)


def _call_primary_mock(_backend, _manifest, _uri, final_payload, ctx) -> ServiceResult:
    from touri.backends import call_mock_backend

    return call_mock_backend(final_payload, ctx)


def _call_primary_uri_flow(backend, _manifest, _uri, final_payload, ctx) -> ServiceResult:
    if not backend.flow:
        return backend_error("uri_flow backend missing flow")
    return run_backend(backend_to_dict(backend), final_payload, ctx)


def _call_primary_uri_graph(backend, _manifest, _uri, final_payload, ctx) -> ServiceResult:
    if not backend.graph:
        return backend_error("uri_graph backend missing graph")
    return run_backend(backend_to_dict(backend), final_payload, ctx)


def _call_primary_uri2ops(backend, manifest, uri, final_payload, ctx) -> ServiceResult:
    from touri.backends import call_uri2ops_backend

    return call_uri2ops_backend(
        uri,
        manifest.capability.scheme,
        backend.operation or manifest.capability.operation,
        final_payload,
        ctx,
        backend_extra=backend.extra,
    )


_PRIMARY_BACKEND_HANDLERS: dict[str, Callable[..., ServiceResult]] = {
    "python": _call_primary_python,
    "shell": _call_primary_shell,
    "http": _call_primary_http,
    "mock": _call_primary_mock,
    "uri_flow": _call_primary_uri_flow,
    "uri_graph": _call_primary_uri_graph,
    "uri2ops": _call_primary_uri2ops,
}


def call_primary_backend(
    manifest, uri: str, final_payload: dict[str, Any], ctx: dict[str, Any]
) -> ServiceResult:
    backend = manifest.backend
    handler = _PRIMARY_BACKEND_HANDLERS.get(backend.type)
    if handler is None:
        return unsupported_backend(backend.type)
    return handler(backend, manifest, uri, final_payload, ctx)

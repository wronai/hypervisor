from __future__ import annotations

import time
from collections.abc import Callable
from importlib import import_module
from typing import Any

from uri3.results import ServiceResult

from uri2run.result import error_result
from uri2run.transports import (
    run_a2a,
    run_docker,
    run_http,
    run_mcp,
    run_mock,
    run_python,
    run_shell,
    run_sse,
    run_ssh,
    run_stdio,
    run_uri2ops,
    run_uri_flow,
    run_uri_graph,
    run_ws,
)


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
    command = backend.get("command") or backend.get("target")
    if not command:
        return error_result("BACKEND_INVALID", "shell backend missing command")
    return run_shell(str(command), {**backend, **payload}, context)


def _run_http(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "http backend missing target/url")
    http_payload = dict(payload)
    for key in (
        "method",
        "timeout",
        "json",
        "params",
        "headers",
        "data",
        "body",
        "content",
        "retries",
    ):
        if key in backend and key not in http_payload:
            http_payload[key] = backend[key]
    return run_http(str(target), http_payload, context)


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


def _run_stdio(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    command = backend.get("command") or backend.get("target")
    if not command:
        return error_result("BACKEND_INVALID", "stdio backend missing command")
    return run_stdio(str(command), payload, context)


def _run_sse(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "sse backend missing target/url")
    return run_sse(str(target), payload, context)


def _run_ws(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "ws backend missing target/url")
    return run_ws(str(target), payload, context)


def _run_docker(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "docker backend missing target/url")
    return run_docker(str(target), payload, context)


def _run_ssh(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "ssh backend missing target/url")
    return run_ssh(str(target), payload, context)


def _run_mcp(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "mcp backend missing target/url")
    return run_mcp(str(target), payload, context)


def _run_a2a(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "a2a backend missing target/url")
    return run_a2a(str(target), payload, context)


def _run_touri(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]):
    target = backend.get("target") or backend.get("voice_uri")
    registry = backend.get("registry")
    if not target or not registry:
        return error_result("BACKEND_INVALID", "touri backend missing target/registry")
    executor = import_module("touri.executor")
    return executor.call_uri(str(target), str(registry), payload=payload, context=context)


def _run_voice_unresolved(
    backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]
):
    del payload, context
    message = str(backend.get("error") or "voice URI could not be resolved")
    return error_result("VOICE_URI_UNRESOLVED", message, result_type="voice")


_BACKEND_HANDLERS: dict[
    str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], ServiceResult]
] = {
    "python": _run_python,
    "shell": _run_shell,
    "http": _run_http,
    "https": _run_http,
    "stdio": _run_stdio,
    "sse": _run_sse,
    "ws": _run_ws,
    "docker": _run_docker,
    "ssh": _run_ssh,
    "mcp": _run_mcp,
    "a2a": _run_a2a,
    "touri": _run_touri,
    "voice_unresolved": _run_voice_unresolved,
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
    """Execute one backend spec through the matching uri2run transport."""
    started = time.monotonic()
    backend_body = dict(backend)
    backend_type = str(backend_body.get("type") or "")
    handler = _BACKEND_HANDLERS.get(backend_type)
    if handler is None:
        return _stamp_runtime_meta(
            unsupported_backend(backend_type),
            transport=backend_type,
            backend=backend_body,
            duration_ms=int((time.monotonic() - started) * 1000),
        )
    result = handler(backend_body, dict(payload or {}), dict(context or {}))
    return _stamp_runtime_meta(
        result,
        transport=backend_type,
        backend=backend_body,
        duration_ms=int((time.monotonic() - started) * 1000),
    )


def _stamp_runtime_meta(
    result: ServiceResult,
    *,
    transport: str,
    backend: dict[str, Any],
    duration_ms: int,
) -> ServiceResult:
    target = (
        backend.get("voice_uri")
        or backend.get("target")
        or backend.get("url")
        or backend.get("command")
        or backend.get("flow")
        or backend.get("graph")
    )
    result.meta.setdefault("runtime", "uri2run")
    result.meta.setdefault("transport", transport)
    result.meta.setdefault("duration_ms", duration_ms)
    if target:
        result.meta.setdefault("target", str(target))
    return result.finalize()


def run_target(
    target: str,
    payload: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> ServiceResult:
    """Execute a concrete runtime URI target."""
    if target.startswith("python://"):
        return run_backend({"type": "python", "target": target}, payload, context)
    if target.startswith("shell://"):
        return run_backend(
            {"type": "shell", "command": target.removeprefix("shell://")}, payload, context
        )
    if target.startswith(("http://", "https://")):
        return run_backend({"type": "http", "target": target}, payload, context)
    if target.startswith("stdio://"):
        return run_backend(
            {"type": "stdio", "command": target.removeprefix("stdio://")}, payload, context
        )
    if target.startswith("sse://"):
        return run_backend({"type": "sse", "url": target}, payload, context)
    if target.startswith("ws://") or target.startswith("wss://"):
        return run_backend({"type": "ws", "url": target}, payload, context)
    if target.startswith("docker://"):
        return run_backend({"type": "docker", "target": target}, payload, context)
    if target.startswith("ssh://"):
        return run_backend({"type": "ssh", "target": target}, payload, context)
    if target.startswith("mcp://"):
        return run_backend({"type": "mcp", "target": target}, payload, context)
    if target.startswith("a2a://"):
        return run_backend({"type": "a2a", "target": target}, payload, context)
    from uri2run.voice_resolver import resolve_voice_backend

    voice_backend = resolve_voice_backend(target)
    if voice_backend is not None:
        return run_backend(voice_backend, payload, context)
    return unsupported_backend(target.split(":", 1)[0] if ":" in target else target)

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from uri2ops.operation_registry.dispatcher import dispatch
from uri2ops.operation_registry.uri_mapping import registry_operation, registry_scheme
from uri3.results import ServiceResult

from uri2run.result import error_result, result_from_output

_OPERATOR_SCHEMES = frozenset(
    {"browser", "dom", "screen", "input", "android", "pcwin", "robot", "device"}
)


def _resolve_root(context: dict[str, Any]) -> Path:
    root = context.get("root")
    if root:
        return Path(root)
    from uri3.config.repo_root import find_repo_root

    return find_repo_root()


def _build_runtime_context(
    uri: str,
    payload: dict[str, Any],
    context: dict[str, Any],
    extra: dict[str, Any],
) -> dict[str, Any]:
    return {
        "adapter": str(payload.get("adapter", extra.get("adapter", "auto"))),
        "root": str(_resolve_root(context)),
        "task_id": str(context.get("capability") or "uri2run"),
        "run_id": str(context.get("run_id") or "uri2run-call"),
        "session": dict(context.get("session") or payload.get("session") or {}),
    }


def run_uri2ops(
    uri: str,
    scheme: str,
    operation: str,
    payload: dict[str, Any],
    context: dict[str, Any],
    *,
    backend_extra: dict[str, Any] | None = None,
) -> ServiceResult:
    extra = backend_extra or {}
    if scheme not in _OPERATOR_SCHEMES:
        return error_result(
            "URI2OPS_SCHEME_UNSUPPORTED", f"scheme not supported by uri2ops: {scheme}"
        )

    registry_scheme_name = registry_scheme(scheme)
    registry_operation_name = registry_operation(scheme, str(extra.get("operation") or operation))
    dispatch_payload = dict(payload)
    dispatch_payload.setdefault("target_uri", uri)
    dispatch_payload.setdefault(
        "step_id", context.get("capability") or urlparse(uri).path.strip("/") or "step"
    )
    runtime_context = _build_runtime_context(uri, payload, context, extra)
    environment = (
        extra.get("environment")
        or context.get("environment")
        or payload.get("environment")
    )

    try:
        if environment:
            from uri2ops.operator.environments.router import dispatch_with_environment

            output = dispatch_with_environment(
                registry_scheme_name,
                registry_operation_name,
                dispatch_payload,
                runtime_context,
                environment=str(environment),
                control_arguments={**extra, **context},
            )
        else:
            output = dispatch(
                registry_scheme_name,
                registry_operation_name,
                dispatch_payload,
                runtime_context,
            )
    except Exception as exc:
        return error_result("URI2OPS_DISPATCH_FAILED", str(exc))

    return result_from_output(output)


def run_uri2ops_transport(
    backend: dict[str, Any],
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    scheme = str(context.get("scheme") or backend.get("scheme") or "")
    operation = str(backend.get("operation") or context.get("operation") or "call")
    uri = str(context.get("uri") or backend.get("uri") or "")
    if not uri or not scheme:
        return error_result("BACKEND_INVALID", "uri2ops backend missing uri/scheme context")
    return run_uri2ops(uri, scheme, operation, payload, context, backend_extra=backend)

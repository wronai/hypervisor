from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from uri2ops.operation_registry.dispatcher import dispatch
from uri2run.result import error_result, result_from_output
from uri3.results import ServiceResult

_OPERATOR_SCHEMES = frozenset({"browser", "dom", "screen", "input", "android", "pcwin"})
_OPERATION_MAP: dict[tuple[str, str], str] = {
    ("browser", "read"): "extract_dom",
    ("browser", "extract"): "extract_dom",
    ("dom", "read"): "extract_dom",
    ("dom", "extract"): "extract_dom",
    ("dom", "extract_dom"): "extract_dom",
    ("browser", "capture"): "screenshot",
    ("browser", "screenshot"): "screenshot",
    ("screen", "capture"): "observe",
    ("screen", "screenshot"): "observe",
    ("input", "call"): "type",
    ("input", "type"): "type",
}


def _registry_scheme(scheme: str) -> str:
    if scheme == "dom":
        return "browser"
    return scheme


def _registry_operation(scheme: str, operation: str) -> str:
    return _OPERATION_MAP.get((scheme, operation), operation)


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
        "adapter": str(payload.get("adapter", extra.get("adapter", "mock"))),
        "root": str(_resolve_root(context)),
        "task_id": str(context.get("capability") or "uri2run"),
        "run_id": str(context.get("run_id") or "uri2run-call"),
        "session": dict(context.get("session") or {}),
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
        return error_result("URI2OPS_SCHEME_UNSUPPORTED", f"scheme not supported by uri2ops: {scheme}")

    registry_scheme = _registry_scheme(scheme)
    registry_operation = _registry_operation(scheme, str(extra.get("operation") or operation))
    dispatch_payload = dict(payload)
    dispatch_payload.setdefault("target_uri", uri)
    dispatch_payload.setdefault(
        "step_id", context.get("capability") or urlparse(uri).path.strip("/") or "step"
    )
    runtime_context = _build_runtime_context(uri, payload, context, extra)

    try:
        output = dispatch(registry_scheme, registry_operation, dispatch_payload, runtime_context)
    except Exception as exc:
        return error_result("URI2OPS_DISPATCH_FAILED", str(exc))

    return result_from_output(output)

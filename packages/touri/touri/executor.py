from __future__ import annotations

from typing import Any

from .backends import call_mock_backend, call_python_backend, call_shell_backend
from .data_quality import apply_data_quality
from .loader import load_registry
from .matcher import require_match
from .models import ServiceResult, service_result


def _payload_from_params(params: dict[str, str], payload: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = dict(params)
    if payload:
        merged.update(payload)
    return merged


def _error_codes(result: ServiceResult) -> list[str]:
    codes: list[str] = []
    for item in result.errors:
        code = getattr(item, "code", None) or (item.get("code") if isinstance(item, dict) else None)
        if code:
            codes.append(str(code))
    return codes


def _fallback_matches(when: str | None, result: ServiceResult) -> bool:
    if not when or when in {"any", "*"}:
        return not result.ok
    return when in _error_codes(result)


def _call_backend(backend: dict[str, Any], payload: dict[str, Any], context: dict[str, Any]) -> ServiceResult:
    backend_type = str(backend.get("type") or "")
    if backend_type == "python":
        target = backend.get("target")
        if not target:
            return service_result(ok=False, result_type="error", errors=[{"code": "FALLBACK_BACKEND_INVALID", "detail": "python fallback missing target"}])
        return call_python_backend(str(target), payload, context)
    if backend_type == "shell":
        command = backend.get("command")
        if not command:
            return service_result(ok=False, result_type="error", errors=[{"code": "FALLBACK_BACKEND_INVALID", "detail": "shell fallback missing command"}])
        return call_shell_backend(str(command), payload, context)
    if backend_type == "mock":
        return call_mock_backend(payload, context)
    return service_result(
        ok=False,
        result_type="unsupported_backend",
        errors=[{"code": "FALLBACK_BACKEND_UNSUPPORTED", "detail": f"fallback backend not implemented: {backend_type}"}],
    )


def _apply_fallbacks(
    manifest,
    result: ServiceResult,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    if result.ok or not manifest.fallbacks:
        return result
    for entry in manifest.fallbacks:
        if not isinstance(entry, dict):
            continue
        when = entry.get("when")
        backend = entry.get("backend")
        if not isinstance(backend, dict) or not _fallback_matches(str(when) if when else None, result):
            continue
        fallback_result = _call_backend(backend, payload, context)
        fallback_result.meta = {**fallback_result.meta, "fallback_from": manifest.capability.id, "fallback_when": when}
        if fallback_result.ok:
            fallback_result.warnings.append(f"fallback applied for {when or 'any'}")
            return apply_data_quality(manifest, fallback_result, payload, context)
    return result


def call_uri(uri: str, registry_root: str, payload: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> ServiceResult:
    registry = load_registry(registry_root)
    match = require_match(uri, registry)
    manifest = match.manifest
    ctx = dict(context or {})
    ctx.update({"uri": uri, "capability": manifest.capability.id})
    final_payload = _payload_from_params(match.params, payload)
    backend = manifest.backend
    if backend.type == "python":
        if not backend.target:
            return service_result(ok=False, result_type="error", errors=[{"detail": "python backend missing target"}])
        result = call_python_backend(backend.target, final_payload, ctx)
    elif backend.type == "shell":
        if not backend.command:
            return service_result(ok=False, result_type="error", errors=[{"detail": "shell backend missing command"}])
        result = call_shell_backend(backend.command, final_payload, ctx)
    elif backend.type == "mock":
        result = call_mock_backend(final_payload, ctx)
    else:
        result = service_result(
            ok=False,
            result_type="unsupported_backend",
            errors=[{"detail": f"Backend type not implemented yet: {backend.type}"}],
        )
    result.uri = uri
    result.capability = manifest.capability.id
    result.backend = backend.type
    result = apply_data_quality(manifest, result, final_payload, ctx)
    result = _apply_fallbacks(manifest, result, final_payload, ctx)
    return result

from __future__ import annotations

import importlib
from typing import Any

from touri.models import ServiceResult, service_result
from uri3.results import ErrorEnvelope, normalize_error


def _split_python_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("python://"):
        raise ValueError(f"Expected python:// URI, got {uri}")
    ref = uri.removeprefix("python://")
    if ":" not in ref:
        raise ValueError("python backend target must be python://module:function")
    module, func = ref.split(":", 1)
    return module, func


def call_python_backend(target: str, payload: dict[str, Any], context: dict[str, Any]) -> ServiceResult:
    module_name, func_name = _split_python_uri(target)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    result = func(payload, context) if callable(func) else func
    if isinstance(result, ServiceResult):
        return result.finalize()
    if isinstance(result, dict) and "ok" in result:
        errors = [normalize_error(item) for item in result.get("errors") or []]
        return service_result(
            ok=bool(result.get("ok")),
            result_type=str(result.get("result_type", "data")),
            data=result.get("data", result),
            artifact_uri=result.get("artifact_uri"),
            warnings=list(result.get("warnings") or []),
            errors=errors,
            meta=dict(result.get("meta") or {}),
            workflow_status=result.get("workflow_status"),
            execution_status=result.get("execution_status"),
            service_result_status=result.get("service_result_status"),
        )
    return service_result(ok=True, result_type="data", data=result)

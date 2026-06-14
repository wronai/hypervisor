from __future__ import annotations

from typing import Any

from uri3.results import ServiceResult, normalize_error, service_result


def result_from_output(output: Any, *, default_result_type: str = "data") -> ServiceResult:
    if isinstance(output, ServiceResult):
        return output.finalize()
    if isinstance(output, dict) and "ok" in output:
        return service_result(
            ok=bool(output.get("ok")),
            result_type=str(output.get("result_type", default_result_type)),
            data=output.get("data", output),
            artifact_uri=output.get("artifact_uri"),
            warnings=list(output.get("warnings") or []),
            errors=[normalize_error(item) for item in output.get("errors") or []],
            meta=dict(output.get("meta") or {}),
            workflow_status=output.get("workflow_status"),
            execution_status=output.get("execution_status"),
            service_result_status=output.get("service_result_status"),
        )
    return service_result(ok=True, result_type=default_result_type, data=output)


def error_result(code: str, detail: str, *, result_type: str = "error") -> ServiceResult:
    return service_result(ok=False, result_type=result_type, errors=[{"code": code, "detail": detail}])

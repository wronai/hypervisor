from __future__ import annotations

from typing import Any

from uri3.results import service_result


def always_pass(payload: dict[str, Any], context: dict[str, Any] | None = None):
    return service_result(ok=True, result_type="validation", meta={"validator": "always_pass"})


def reject_low_confidence(payload: dict[str, Any], context: dict[str, Any] | None = None):
    result = payload.get("result") or {}
    confidence = (result.get("meta") or {}).get("confidence", 1.0)
    if float(confidence) < 0.75:
        return service_result(
            ok=False,
            result_type="validation",
            meta={"failure_code": "PRICE_RESULT_NOT_RELEVANT", "detail": "confidence too low", "confidence": confidence},
        )
    return service_result(ok=True, result_type="validation", meta={"confidence": confidence})


def low_confidence_backend(payload: dict[str, Any], context: dict[str, Any] | None = None):
    return service_result(ok=True, result_type="data", data={"item": payload.get("name")}, meta={"confidence": 0.2})

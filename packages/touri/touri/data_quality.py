from __future__ import annotations

from typing import Any

from uri3.results import ErrorEnvelope

from .backends.python_backend import call_python_backend
from .models import ServiceResult


def apply_data_quality(
    manifest,
    result: ServiceResult,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    dq = manifest.data_quality or {}
    if not dq or not result.ok:
        return result.finalize()

    source = f"touri://capability/{manifest.capability.id}"
    failure_code = str(dq.get("failure_code") or "DATA_QUALITY_FAILED")
    min_confidence = dq.get("min_confidence")
    refresh_statuses = False

    for validator_uri in dq.get("validators") or []:
        validation = call_python_backend(
            str(validator_uri),
            {"result": result.to_dict(), "payload": payload},
            context,
        )
        if not validation.ok:
            detail = (
                validation.errors[0].detail
                if validation.errors
                else validation.meta.get("detail") or "validation failed"
            )
            result.ok = False
            refresh_statuses = True
            result.result_type = "error"
            result.errors.append(
                ErrorEnvelope(
                    code=str(validation.meta.get("failure_code") or failure_code),
                    source=source,
                    recoverable=bool(dq.get("recoverable", True)),
                    detail=str(detail),
                    data_quality=dict(validation.meta.get("data_quality") or {}),
                )
            )
            return result.finalize(refresh_statuses=refresh_statuses)

    confidence = result.meta.get("confidence")
    if min_confidence is not None and confidence is not None:
        try:
            if float(confidence) < float(min_confidence):
                result.ok = False
                refresh_statuses = True
                result.result_type = "error"
                result.errors.append(
                    ErrorEnvelope(
                        code=failure_code,
                        source=source,
                        recoverable=bool(dq.get("recoverable", True)),
                        detail=f"confidence {confidence} below min_confidence {min_confidence}",
                        data_quality={"confidence": confidence, "min_confidence": min_confidence},
                    )
                )
        except (TypeError, ValueError):
            result.warnings.append(f"invalid confidence value: {confidence!r}")

    if dq.get("relevance_required") and result.data is None:
        result.ok = False
        refresh_statuses = True
        result.errors.append(
            ErrorEnvelope(
                code=failure_code,
                source=source,
                recoverable=True,
                detail="relevance_required but result data is empty",
            )
        )

    return result.finalize(refresh_statuses=refresh_statuses)

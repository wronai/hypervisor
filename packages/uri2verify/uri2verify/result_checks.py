from __future__ import annotations

from typing import Any

from uri3.results import ServiceResult

DATA_QUALITY_PASSED = "passed"
DATA_QUALITY_FAILED = "failed"
DATA_QUALITY_SKIPPED = "skipped"

VERIFICATION_PASSED = "passed"
VERIFICATION_FAILED = "failed"
VERIFICATION_SKIPPED = "skipped"


def _has_data_quality_source(result: ServiceResult) -> bool:
    return any(
        error.source.startswith("uri2verify") or "data_quality" in error.source
        for error in result.errors
    )


def _has_data_quality_payload(result: ServiceResult) -> bool:
    return any(getattr(error, "data_quality", None) for error in result.errors)


def data_quality_status_from_result(result: ServiceResult, *, checked: bool) -> str:
    if not checked:
        return DATA_QUALITY_SKIPPED
    if result.ok:
        return DATA_QUALITY_PASSED
    if _has_data_quality_source(result) or _has_data_quality_payload(result):
        return DATA_QUALITY_FAILED
    return DATA_QUALITY_SKIPPED


def verification_status_from_result(
    result: ServiceResult,
    *,
    data_quality_status: str,
) -> str:
    if data_quality_status == DATA_QUALITY_FAILED:
        return VERIFICATION_FAILED
    if result.ok:
        return VERIFICATION_PASSED
    if result.service_result_status == "failed":
        return VERIFICATION_FAILED
    return VERIFICATION_SKIPPED


def apply_verification_statuses(
    result: ServiceResult,
    *,
    data_quality_checked: bool,
) -> ServiceResult:
    dq_status = data_quality_status_from_result(result, checked=data_quality_checked)
    result.meta["data_quality_status"] = dq_status
    result.meta["verification_status"] = verification_status_from_result(
        result,
        data_quality_status=dq_status,
    )
    return result


def enrich_result_dict(payload: dict[str, Any]) -> dict[str, Any]:
    """Ensure verification fields appear in serialized results when present in meta."""
    meta = payload.get("meta") or {}
    if "data_quality_status" in meta:
        payload["data_quality_status"] = meta["data_quality_status"]
    if "verification_status" in meta:
        payload["verification_status"] = meta["verification_status"]
    return payload


def technical_vs_business_ok(payload: dict[str, Any]) -> dict[str, bool]:
    """Split tellm-style ambiguity: execution may complete while service/verification fails."""
    execution_ok = payload.get("execution_status") == "completed"
    service_ok = payload.get("service_result_status") == "succeeded"
    verification_ok = payload.get("verification_status", VERIFICATION_SKIPPED) in {
        VERIFICATION_PASSED,
        VERIFICATION_SKIPPED,
    }
    return {
        "execution_ok": execution_ok,
        "service_ok": service_ok,
        "verification_ok": verification_ok,
        "business_ok": bool(payload.get("ok")) and service_ok and verification_ok,
    }

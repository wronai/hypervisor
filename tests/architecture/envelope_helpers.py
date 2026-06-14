from __future__ import annotations

from typing import Any

REQUIRED_ENVELOPE_FIELDS = frozenset(
    {
        "ok",
        "execution_status",
        "service_result_status",
        "result_type",
        "errors",
        "warnings",
        "meta",
    }
)


def normalize_service_result(payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(payload)
    body.setdefault("errors", [])
    body.setdefault("warnings", [])
    body.setdefault("meta", {})
    if "data" not in body:
        body["data"] = None
    return body


def assert_service_result_shape(payload: dict[str, Any]) -> None:
    body = normalize_service_result(payload)
    missing = REQUIRED_ENVELOPE_FIELDS - set(body)
    assert not missing, f"missing envelope fields: {sorted(missing)}"
    assert isinstance(body["errors"], list)
    assert isinstance(body["warnings"], list)
    assert isinstance(body["meta"], dict)


def assert_workflow_result_shape(payload: dict[str, Any]) -> None:
    required = {"ok", "workflow_status", "execution_status", "service_result_status"}
    missing = required - set(payload)
    assert not missing, f"missing workflow fields: {sorted(missing)}"

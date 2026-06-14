from __future__ import annotations

from typing import Any

from .statuses import (
    EXECUTION_COMPLETED,
    EXECUTION_FAILED,
    SERVICE_FAILED,
    SERVICE_SUCCEEDED,
    WORKFLOW_COMPLETED,
    WORKFLOW_COMPLETED_WITH_SERVICE_ERROR,
    WORKFLOW_FAILED,
    derive_statuses,
)


def step_execution_status(*, status: str, dry_run: bool = False) -> str:
    if status in {"blocked", "skipped"}:
        return status
    if status == "failed":
        return EXECUTION_FAILED
    return EXECUTION_COMPLETED


def step_service_result_status(*, ok: bool, status: str) -> str:
    if status == "skipped" and ok:
        return SERVICE_SUCCEEDED
    if ok:
        return SERVICE_SUCCEEDED
    return SERVICE_FAILED


def workflow_aggregate_statuses(
    *,
    ok: bool,
    steps: list[dict[str, Any]],
    pending_approval: list[str] | None = None,
    dry_run: bool = False,
) -> tuple[str, str, str]:
    del dry_run
    if pending_approval:
        return WORKFLOW_FAILED, EXECUTION_FAILED, SERVICE_FAILED
    service_failed = any(
        step.get("service_result_status") == SERVICE_FAILED or (not step.get("ok", True) and step.get("status") not in {"skipped"})
        for step in steps
    )
    execution_failed = any(step.get("execution_status") == EXECUTION_FAILED for step in steps)
    if ok and not service_failed:
        return WORKFLOW_COMPLETED, EXECUTION_COMPLETED, SERVICE_SUCCEEDED
    if execution_failed or pending_approval:
        workflow_status = WORKFLOW_FAILED
    elif service_failed:
        workflow_status = WORKFLOW_COMPLETED_WITH_SERVICE_ERROR
    else:
        workflow_status = WORKFLOW_COMPLETED if ok else WORKFLOW_FAILED
    execution_status = EXECUTION_FAILED if execution_failed else EXECUTION_COMPLETED
    service_result_status = SERVICE_FAILED if service_failed or not ok else SERVICE_SUCCEEDED
    return workflow_status, execution_status, service_result_status


def enrich_step_dict(step: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    status = str(step.get("status") or "completed")
    ok = bool(step.get("ok", True))
    execution_status = step_execution_status(status=status, dry_run=dry_run)
    service_result_status = step_service_result_status(ok=ok, status=status)
    payload = dict(step)
    payload["execution_status"] = execution_status
    payload["service_result_status"] = service_result_status
    result = dict(payload.get("result") or {})
    if result:
        workflow_status, _, _ = derive_statuses(ok and service_result_status == SERVICE_SUCCEEDED)
        result.setdefault("workflow_status", workflow_status)
        result.setdefault("execution_status", execution_status)
        result.setdefault("service_result_status", service_result_status)
        payload["result"] = result
    return payload


def enrich_workflow_dict(payload: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    body = dict(payload)
    steps = [enrich_step_dict(step, dry_run=dry_run) for step in body.get("steps") or []]
    body["steps"] = steps
    workflow_result = dict(body.get("workflow_result") or {})
    wf_status, ex_status, svc_status = workflow_aggregate_statuses(
        ok=bool(workflow_result.get("ok", False)),
        steps=steps,
        pending_approval=list(workflow_result.get("pending_approval") or []),
        dry_run=dry_run,
    )
    workflow_result["workflow_status"] = wf_status
    workflow_result["execution_status"] = ex_status
    workflow_result["service_result_status"] = svc_status
    body["workflow_result"] = workflow_result
    return body

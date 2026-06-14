from __future__ import annotations

from typing import Any

from uri2run.cli import _backend_from_target
from uri2run import run_backend


def call_uri(
    target: str,
    payload: dict[str, Any],
    *,
    backend_type: str = "",
    timeout: float = 30.0,
    dry_run: bool = False,
) -> dict[str, Any]:
    if dry_run:
        from urish.backends.explain import explain_target

        plan = explain_target(target)
        return {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "plan",
            "data": {"target": target, "payload": payload, "explain": plan},
            "meta": {"runtime": "urish", "transport": "dry-run", "target": target},
        }
    backend = _backend_from_target(target, backend_type=backend_type)
    result = run_backend(backend, payload, {"timeout": timeout})
    body = result.to_dict()
    body.setdefault("meta", {})
    body["meta"]["runtime"] = body["meta"].get("runtime") or "uri2run"
    return body

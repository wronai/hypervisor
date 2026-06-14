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
    policy_options: Any | None = None,
    context_policy: str | None = None,
) -> dict[str, Any]:
    if policy_options is not None:
        from urish.policy import evaluate_policy

        allowed, reason, force_dry_run = evaluate_policy(
            target,
            options=policy_options,
            context_policy=context_policy,
        )
        if not allowed:
            return {
                "ok": False,
                "policy_blocked": True,
                "workflow_status": "blocked",
                "execution_status": "blocked",
                "service_result_status": "failed",
                "result_type": "policy",
                "error": reason,
                "meta": {"runtime": "urish", "transport": "policy", "target": target},
            }
        if force_dry_run:
            dry_run = True

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

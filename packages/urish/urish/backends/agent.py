from __future__ import annotations

from typing import Any


def agent_action(action: str, selector: str, **kwargs: Any) -> dict[str, Any]:
    from hypervisor.deployment_registry.runner import (
        agent_status,
        inspect_agent,
        restart_agent,
        run_agent,
        stop_agent,
        supervise_agent,
    )
    from hypervisor.repair.supervisor import diagnose_agent, repair_apply

    dispatch = {
        "status": agent_status,
        "inspect": inspect_agent,
        "health": inspect_agent,
        "run": run_agent,
        "stop": stop_agent,
        "restart": restart_agent,
        "supervise": supervise_agent,
        "diagnose": diagnose_agent,
        "repair": repair_apply,
    }
    handler = dispatch.get(action)
    if handler is None:
        return {"ok": False, "not_found": True, "error": f"unknown agent action: {action}"}
    if action == "run":
        return handler(selector, detach=kwargs.get("detach", True), **kwargs)
    if action == "repair":
        return handler(selector, safe=kwargs.get("safe", True), approved=kwargs.get("approve", False))
    if action == "supervise":
        return handler(selector, repair=kwargs.get("repair", "auto"), **kwargs)
    return handler(selector, **kwargs)

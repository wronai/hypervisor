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
        run_kwargs = dict(kwargs)
        run_kwargs.setdefault("detach", True)
        return handler(selector, **run_kwargs)
    if action == "repair":
        repair_kwargs = dict(kwargs)
        repair_kwargs.setdefault("safe", True)
        repair_kwargs.setdefault("approved", repair_kwargs.pop("approve", False))
        return handler(selector, **repair_kwargs)
    if action == "supervise":
        supervise_kwargs = dict(kwargs)
        supervise_kwargs.setdefault("repair", "auto")
        return handler(selector, **supervise_kwargs)
    return handler(selector, **kwargs)

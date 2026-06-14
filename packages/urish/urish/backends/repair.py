from __future__ import annotations

from pathlib import Path
from typing import Any

from uri3.paths import find_repo_root


def repair_diagnose(selector: str, *, timeout: float = 2.0, log_limit: int = 20) -> dict[str, Any]:
    from hypervisor.repair.supervisor import diagnose_agent

    payload = diagnose_agent(selector, timeout=timeout, log_limit=log_limit)
    return _wrap(payload, action="diagnose", target=selector)


def repair_apply(
    selector: str,
    *,
    safe: bool = True,
    approve: bool = False,
    playbook: str | None = None,
) -> dict[str, Any]:
    from hypervisor.repair.supervisor import repair_apply as _repair_apply

    payload = _repair_apply(selector, safe=safe, approved=approve, playbook=playbook)
    return _wrap(payload, action="apply", target=selector)


def repair_learn(incident_path: str, *, sandbox: bool = True, root: Path | None = None) -> dict[str, Any]:
    from hypervisor.repair.supervisor import learn_from_incident

    path = Path(incident_path)
    if not path.is_absolute():
        path = (root or find_repo_root()) / incident_path
    payload = learn_from_incident(str(path), run_sandbox=sandbox)
    return _wrap(payload, action="learn", target=str(path))


def _wrap(payload: dict[str, Any], *, action: str, target: str) -> dict[str, Any]:
    ok = bool(payload.get("ok", True))
    return {
        "ok": ok,
        "workflow_status": "completed" if ok else "failed",
        "execution_status": "completed" if ok else "failed",
        "service_result_status": "succeeded" if ok else "failed",
        "result_type": "repair",
        "data": payload,
        "meta": {"runtime": "urish", "transport": "repair", "action": action, "target": target},
    }

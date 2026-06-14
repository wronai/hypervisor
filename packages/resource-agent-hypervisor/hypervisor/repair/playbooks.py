from __future__ import annotations

from pathlib import Path
from typing import Any

from hypervisor.deployment_registry.health_uri import command_port_from_runtime
from hypervisor.deployment_registry.lifecycle import restart_agent, run_agent, stop_agent
from hypervisor.deployment_registry.port_utils import find_free_port, port_from_http_uri
from hypervisor.deployment_registry.runtime_state import clear_runtime_state, load_runtime_state
from hypervisor.deployment_registry.supervisor import inspect_agent
from hypervisor.paths import find_repo_root


def _repo_root(root: str | Path | None) -> Path:
    return Path(root) if root is not None else find_repo_root()


def apply_playbook(
    playbook: str,
    *,
    selector: str,
    root: str | Path | None = None,
    approved: bool = False,
) -> dict[str, Any]:
    repo = _repo_root(root)
    if playbook == "sync_health_uri":
        return run_agent(selector, root=repo, detach=True, if_running="reuse")
    if playbook == "restart_agent":
        return restart_agent(selector, root=repo, detach=True)
    if playbook == "clear_stale_runtime":
        stop_agent(selector, root=repo)
        deployment_id = selector if "." in selector else f"{selector}.local"
        clear_runtime_state(deployment_id, repo)
        return {"ok": True, "playbook": playbook, "status": "cleared"}
    if playbook == "rebind_port":
        state = load_runtime_state(selector, repo) or {}
        plan = {"command_string": state.get("command", "")}
        current_port = command_port_from_runtime(state, plan) or port_from_http_uri(
            str(state.get("health_uri") or "")
        )
        rebound = find_free_port(int(current_port or 8101))
        return restart_agent(selector, root=repo, detach=True, port=rebound)
    if playbook in {"verify_effective_port", "read_logs", "check_process"}:
        return inspect_agent(selector, root=repo)
    if playbook in {"regenerate_agent", "modify_deployment_registry", "register_repair_capability"}:
        if not approved:
            return {
                "ok": False,
                "playbook": playbook,
                "status": "blocked",
                "reason": "requires approval",
            }
        return {"ok": False, "playbook": playbook, "status": "not_implemented"}
    return {"ok": False, "playbook": playbook, "status": "unknown_playbook"}


def apply_playbook_sequence(
    playbooks: list[str],
    *,
    selector: str,
    root: str | Path | None = None,
    approved: bool = False,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for playbook in playbooks:
        results.append(apply_playbook(playbook, selector=selector, root=root, approved=approved))
    return results

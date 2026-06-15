from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from uri3.paths import find_repo_root


def repo_root() -> Path:
    return find_repo_root(strict=False)


def _resolve_deployment(deployment_id: str, *, root: Path | None = None):
    from hypervisor.deployment_registry.selector import resolve_deployment

    return resolve_deployment(deployment_id, root=root or repo_root())


def plan_remote_deploy(deployment_id: str, *, root: Path | None = None) -> dict[str, Any]:
    from hypervisor.deployment_registry.remote_runner import build_ssh_deploy_plan

    deployment = _resolve_deployment(deployment_id, root=root)
    if not str(deployment.target_uri).startswith("ssh://"):
        raise ValueError(f"deployment is not SSH-backed: {deployment_id}")
    plan = build_ssh_deploy_plan(deployment, root=root or repo_root())
    return {"ok": True, "deployment_id": deployment_id, "plan": plan}


def apply_remote_deploy(deployment_id: str, *, root: Path | None = None) -> dict[str, Any]:
    from hypervisor.deployment_registry.remote_runner import apply_ssh_deploy_plan, build_ssh_deploy_plan

    base = root or repo_root()
    deployment = _resolve_deployment(deployment_id, root=base)
    plan = build_ssh_deploy_plan(deployment, root=base)
    result = apply_ssh_deploy_plan(plan)
    return {"ok": bool(result.get("ok")), "deployment_id": deployment_id, "deploy_result": result}


def verify_remote_agent(deployment_id: str, *, root: Path | None = None) -> dict[str, Any]:
    from hypervisor.deployment_registry.remote_runner import verify_remote_deployment

    base = root or repo_root()
    deployment = _resolve_deployment(deployment_id, root=base)
    payload = verify_remote_deployment(deployment, root=base)
    return {"ok": bool(payload.get("verified")), "deployment_id": deployment_id, "verify": payload}


def start_remote_agent(
    deployment_id: str,
    *,
    wait_healthy: bool = False,
    root: Path | None = None,
) -> dict[str, Any]:
    from hypervisor.deployment_registry.remote_runner import apply_ssh_run_plan, build_ssh_run_plan

    base = root or repo_root()
    deployment = _resolve_deployment(deployment_id, root=base)
    plan = build_ssh_run_plan(deployment, root=base)
    result = apply_ssh_run_plan(plan, wait_healthy=wait_healthy)
    return {"ok": bool(result.get("ok")), "deployment_id": deployment_id, "start": result}


def deploy_verify_start(
    deployment_id: str,
    *,
    wait_healthy: bool = True,
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or repo_root()
    out_dir = base / "output" / "analysis" / "remote-deploy"
    out_dir.mkdir(parents=True, exist_ok=True)
    deploy = apply_remote_deploy(deployment_id, root=base)
    verify = verify_remote_agent(deployment_id, root=base)
    start = start_remote_agent(deployment_id, wait_healthy=wait_healthy, root=base)
    payload = {
        "ok": deploy.get("ok") and verify.get("ok") and start.get("ok"),
        "deployment_id": deployment_id,
        "deploy": deploy,
        "verify": verify,
        "start": start,
    }
    jsonl = out_dir / "remote-deploy.jsonl"
    with jsonl.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    (out_dir / "remote-deploy-latest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload

from __future__ import annotations

from pathlib import Path
from typing import Any


def create_dashboard(
    name: str = "hypervisor-dashboard",
    *,
    prompt: str | None = None,
    plan_only: bool = False,
    dry_run: bool = False,
    sandbox: bool = False,
    approve: bool = False,
    open_browser: bool = False,
) -> dict[str, Any]:
    """Orchestrate dashboard-agent ecosystem workflow through urigen + hypervisor."""
    from urigen.apply import apply_ecosystem
    from urigen.generator import generate_ecosystem
    from urigen.io import write_yaml
    from urigen.proposal import plan_ecosystem
    from urigen.verify import verify_ecosystem

    from urish.backends.agent import agent_action

    eco_id = name
    source_prompt = prompt or (
        f"stwórz web UI agenta {eco_id} do pokazywania procesów hypervisora, "
        "incydentów, napraw i ticketów"
    )
    proposal_file = Path(f"output/proposals/{eco_id}.ecosystem.proposal.yaml")
    ecosystem_out = Path(f"output/ecosystems/{eco_id}")
    ecosystem_yaml = ecosystem_out / "ecosystem.yaml"

    steps: list[dict[str, Any]] = []
    proposal = plan_ecosystem(source_prompt, profile="dashboard-agent", ecosystem_id=eco_id)
    proposal_file.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(proposal_file, proposal)
    steps.append({"step": "plan", "ok": True, "path": str(proposal_file)})

    if plan_only or dry_run:
        return {
            "ok": True,
            "status": "planned",
            "ecosystem_id": eco_id,
            "proposal_path": str(proposal_file),
            "steps": steps,
            "next": [
                f"urish ecosystem generate {proposal_file} --out {ecosystem_out}",
                f"urish ecosystem verify {ecosystem_yaml}",
            ],
        }

    generated = generate_ecosystem(proposal_file, out=ecosystem_out)
    steps.append(
        {"step": "generate", "ok": generated.get("ok", False), "directory": str(ecosystem_out)}
    )
    if not generated.get("ok"):
        return {"ok": False, "status": "generate_failed", "steps": steps, "generated": generated}

    verification = verify_ecosystem(ecosystem_yaml, write_report=True)
    steps.append({"step": "verify", "ok": verification.get("ok", False)})
    if not verification.get("ok"):
        return {
            "ok": False,
            "status": "verify_failed",
            "steps": steps,
            "verification": verification,
        }

    planned = apply_ecosystem(ecosystem_yaml, plan_only=True)
    steps.append(
        {
            "step": "apply_plan",
            "ok": planned.get("ok", False),
            "plan_path": planned.get("plan_path"),
        }
    )

    if sandbox or not approve:
        return {
            "ok": True,
            "status": "ready_for_apply",
            "ecosystem_id": eco_id,
            "steps": steps,
            "apply_plan": planned,
            "next": [f"urish dashboard create {eco_id} --approve"],
        }

    applied = apply_ecosystem(ecosystem_yaml, approve=True)
    steps.append(
        {"step": "apply", "ok": applied.get("ok", False), "result_path": applied.get("result_path")}
    )
    if not applied.get("ok"):
        return {"ok": False, "status": "apply_failed", "steps": steps, "apply": applied}

    deployment_id = f"{eco_id}.local"
    run_result = agent_action(
        "run",
        deployment_id,
        wait_healthy=True,
        supervise_repair="auto",
        detach=True,
    )
    steps.append({"step": "run", "ok": run_result.get("ok", False), "deployment_id": deployment_id})

    browser_result = None
    if open_browser and run_result.get("ok"):
        from urish.backends.call import call_uri
        from urish.policy import PolicyOptions

        browser_result = call_uri(
            "browser://chrome/page/open",
            payload={"url": "http://localhost:8788/ui"},
            policy_options=PolicyOptions.from_flags(approve=True),
        )
        steps.append({"step": "open_browser", "ok": browser_result.get("ok", False)})

    return {
        "ok": bool(run_result.get("ok")),
        "status": "running" if run_result.get("ok") else "run_failed",
        "ecosystem_id": eco_id,
        "deployment_id": deployment_id,
        "steps": steps,
        "run": run_result,
        "browser": browser_result,
        "ui_url": "http://localhost:8788/ui",
    }

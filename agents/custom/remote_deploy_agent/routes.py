from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .agent_card import AGENT_CARD
from .deploy import (
    apply_remote_deploy,
    deploy_verify_start,
    plan_remote_deploy,
    repo_root,
    start_remote_agent,
    verify_remote_agent,
)

router = APIRouter()


class DeploymentRequest(BaseModel):
    deployment_id: str = Field(..., description="SSH deployment selector, e.g. weather-map-agent.ssh-dev")
    wait_healthy: bool = True


@router.get("/health")
def health() -> dict[str, object]:
    return {"ok": True, "agent": "remote-deploy-agent", "version": AGENT_CARD["version"]}


@router.get("/.well-known/agent-card.json")
def well_known_agent_card_json() -> dict[str, object]:
    return AGENT_CARD


@router.get("/capabilities")
def capabilities() -> dict[str, object]:
    return {"capabilities": AGENT_CARD["capabilities"]}


@router.post("/skills/plan_remote_deploy")
def skill_plan_remote_deploy(payload: DeploymentRequest) -> dict[str, object]:
    return plan_remote_deploy(payload.deployment_id, root=repo_root())


@router.post("/skills/apply_remote_deploy")
def skill_apply_remote_deploy(payload: DeploymentRequest) -> dict[str, object]:
    return apply_remote_deploy(payload.deployment_id, root=repo_root())


@router.post("/skills/verify_remote_agent")
def skill_verify_remote_agent(payload: DeploymentRequest) -> dict[str, object]:
    return verify_remote_agent(payload.deployment_id, root=repo_root())


@router.post("/skills/start_remote_agent")
def skill_start_remote_agent(payload: DeploymentRequest) -> dict[str, object]:
    return start_remote_agent(
        payload.deployment_id,
        wait_healthy=payload.wait_healthy,
        root=repo_root(),
    )


@router.post("/skills/deploy_verify_start")
def skill_deploy_verify_start(payload: DeploymentRequest) -> dict[str, object]:
    return deploy_verify_start(
        payload.deployment_id,
        wait_healthy=payload.wait_healthy,
        root=repo_root(),
    )

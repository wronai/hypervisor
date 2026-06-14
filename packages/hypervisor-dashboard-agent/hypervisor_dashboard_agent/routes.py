from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from hypervisor_dashboard_agent.agent_card import AGENT_CARD
from hypervisor_dashboard_agent.policy import decision_for_uri, preview_action
from hypervisor_dashboard_agent.uri_client import call_system_uri, list_agent_deployments, resolve_view_uri

router = APIRouter()
templates = Jinja2Templates(directory=str(__import__("hypervisor_dashboard_agent").__path__[0] + "/templates"))


class UriCallRequest(BaseModel):
    uri: str = Field(..., description="URI to execute through policy gate")
    approved: bool = False
    dry_run: bool = False
    readonly: bool = False
    policy: str = "dev"
    payload: dict[str, Any] = Field(default_factory=dict)


@router.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "agent": "hypervisor-dashboard",
        "version": AGENT_CARD["version"],
        "role": AGENT_CARD.get("role", []),
    }


@router.get("/capabilities")
def capabilities() -> dict[str, Any]:
    return {"capabilities": AGENT_CARD["capabilities"]}


@router.get("/.well-known/agent.json")
def well_known_agent_json() -> dict[str, Any]:
    return AGENT_CARD


@router.get("/.well-known/agent-card.json")
def well_known_agent_card_json() -> dict[str, Any]:
    return AGENT_CARD


@router.get("/ui")
def ui_root() -> RedirectResponse:
    return RedirectResponse(url="/ui/agents", status_code=302)


@router.get("/ui/agents", response_class=HTMLResponse)
def ui_agents(request: Request) -> HTMLResponse:
    agents = list_agent_deployments()
    return templates.TemplateResponse(
        request,
        "agents.html",
        {"agents": agents, "agent_card": AGENT_CARD},
    )


@router.get("/ui/agents/{agent_id}", response_class=HTMLResponse)
def ui_agent_detail(request: Request, agent_id: str) -> HTMLResponse:
    view_uri = f"view://process/agent/{agent_id}/latest"
    try:
        envelope = resolve_view_uri(view_uri)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return HTMLResponse(content=envelope.html or "")


@router.get("/api/view/process/agent/{agent_id}")
def api_process_view(agent_id: str) -> dict[str, Any]:
    view_uri = f"view://process/agent/{agent_id}/latest"
    try:
        return resolve_view_uri(view_uri).to_dict()
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/api/uri/preview")
def api_uri_preview(body: UriCallRequest) -> dict[str, Any]:
    return preview_action(body.uri, policy=body.policy)


@router.post("/api/uri/call")
def api_uri_call(body: UriCallRequest) -> dict[str, Any]:
    decision = decision_for_uri(
        body.uri,
        approved=body.approved,
        dry_run=body.dry_run,
        readonly=body.readonly,
        policy=body.policy,
    )
    if not decision.allowed:
        raise HTTPException(
            status_code=403,
            detail={
                "error": decision.reason or "action blocked by policy",
                "uri": body.uri,
                "requires_approval": decision.requires_approval,
                "preview": preview_action(body.uri, policy=body.policy),
            },
        )
    try:
        result = call_system_uri(
            body.uri,
            approved=body.approved,
            dry_run=decision.force_dry_run or body.dry_run,
            payload=body.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result.setdefault("policy", {})
    result["policy"] = {
        "dry_run": decision.force_dry_run or body.dry_run,
        "approved": body.approved,
        "policy": body.policy,
    }
    return result


@router.get("/api/agents")
def api_agents() -> dict[str, Any]:
    return {"agents": list_agent_deployments()}


@router.get("/api/events")
def api_events(limit: int = 20) -> dict[str, Any]:
    """Placeholder event stream — lists deployment view URIs as observable events."""
    agents = list_agent_deployments()[:limit]
    events = [
        {
            "type": "deployment.registered",
            "uri": item["view_uri"],
            "agent_id": item["id"],
            "status": item["status"],
        }
        for item in agents
    ]
    return {"events": events, "limit": limit}

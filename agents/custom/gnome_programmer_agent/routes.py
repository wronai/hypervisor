from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .agent_card import AGENT_CARD
from .programmer import observe_desktop, programmer_session, repo_root, type_on_desktop

router = APIRouter()


class OperatorRequest(BaseModel):
    operator_url: str = "http://localhost:8791"
    adapter: str = "mock"
    approve: bool = True
    run_label: str = "gnome-programmer"


class TypeRequest(OperatorRequest):
    text: str = Field(..., description="Text to type into focused GNOME window")


class SessionRequest(OperatorRequest):
    command_text: str = ""


@router.get("/health")
def health() -> dict[str, object]:
    return {"ok": True, "agent": "gnome-programmer-agent", "version": AGENT_CARD["version"]}


@router.get("/.well-known/agent-card.json")
def well_known_agent_card_json() -> dict[str, object]:
    return AGENT_CARD


@router.get("/capabilities")
def capabilities() -> dict[str, object]:
    return {"capabilities": AGENT_CARD["capabilities"]}


@router.post("/skills/observe_desktop")
def skill_observe_desktop(payload: OperatorRequest) -> dict[str, object]:
    return observe_desktop(
        operator_url=payload.operator_url,
        adapter=payload.adapter,
        approve=payload.approve,
        run_label=payload.run_label,
        root=repo_root(),
    )


@router.post("/skills/type_on_desktop")
def skill_type_on_desktop(payload: TypeRequest) -> dict[str, object]:
    return type_on_desktop(
        text=payload.text,
        operator_url=payload.operator_url,
        adapter=payload.adapter,
        approve=payload.approve,
        run_label=payload.run_label,
    )


@router.post("/skills/run_programmer_session")
def skill_run_programmer_session(payload: SessionRequest) -> dict[str, object]:
    return programmer_session(
        operator_url=payload.operator_url,
        adapter=payload.adapter,
        approve=payload.approve,
        command_text=payload.command_text,
        run_label=payload.run_label,
        root=repo_root(),
    )

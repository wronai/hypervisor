# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: /home/tom/github/wronai/hypervisor/contracts/agents/test_orders_agent.yaml
# Contract hash: sha256:9d461331e6fc19f635e3a1d67a8eb1bd9c774465ccfe4e804e2a180f089bc9c8

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from runtime_client.client import ResourceRuntimeClient

from .agent_card import AGENT_CARD

router = APIRouter()

RUNTIME_URL = os.getenv("RESOURCE_RUNTIME_URL", "http://localhost:8000")
client = ResourceRuntimeClient(base_url=RUNTIME_URL)


class CommandRequest(BaseModel):
    command: str = Field(..., description="Runtime command name")
    payload: dict[str, Any] = Field(default_factory=dict)


@router.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "agent": "orders-agent",
        "version": "0.1.0",
        "runtime_url": RUNTIME_URL,
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


@router.get("/resources/read")
def read_resource(uri: str = Query(...)) -> dict[str, Any]:
    allowed = [cap.get("uri") for cap in AGENT_CARD["capabilities"] if cap.get("type") == "resource_read"]
    if not _uri_allowed(uri, allowed):
        raise HTTPException(status_code=403, detail=f"URI not exposed by this agent: {uri}")
    return client.read_resource(uri)


@router.post("/commands")
def dispatch_command(request: CommandRequest) -> dict[str, Any]:
    allowed = [cap.get("command") for cap in AGENT_CARD["capabilities"] if cap.get("type") == "command"]
    if request.command not in allowed:
        raise HTTPException(status_code=403, detail=f"Command not exposed by this agent: {request.command}")
    return client.dispatch_command(request.command, request.payload)


@router.get("/skills/read_order")
def skill_read_order(order_id: str) -> dict[str, Any]:
    uri = "resource://orders/{order_id}".replace("{order_id}", order_id)
    return client.read_resource(uri)


@router.get("/skills/read_order_events")
def skill_read_order_events(order_id: str) -> dict[str, Any]:
    uri = "resource://orders/{order_id}/events".replace("{order_id}", order_id)
    return client.read_resource(uri)



def _uri_allowed(uri: str, templates: list[str | None]) -> bool:
    for template in templates:
        if not template:
            continue
        prefix = template.split("{")[0]
        if uri.startswith(prefix):
            return True
    return False

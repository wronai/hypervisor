# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: /mnt/data/resource_agent_hypervisor_v0_4/contracts/agents/weather_map_agent.yaml
# Contract hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485

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
        "agent": "weather-map-agent",
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


@router.get("/skills/read_weather_map")
def skill_read_weather_map(place: str, days: str) -> dict[str, Any]:
    uri = "resource://weather/maps/{place}/forecast/{days}".replace("{place}", place).replace("{days}", days)    return client.read_resource(uri)

@router.post("/skills/generate_weather_map")
def skill_generate_weather_map(payload: dict[str, Any]) -> dict[str, Any]:
    return client.dispatch_command("GenerateWeatherMap", payload)


def _uri_allowed(uri: str, templates: list[str | None]) -> bool:
    for template in templates:
        if not template:
            continue
        prefix = template.split("{")[0]
        if uri.startswith(prefix):
            return True
    return False
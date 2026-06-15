# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/screenshot_analysis_agent.yaml
# Contract hash: sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

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
        "agent": "screenshot-analysis-agent",
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
    allowed = [
        cap.get("uri")
        for cap in AGENT_CARD["capabilities"]
        if cap.get("type") == "resource_read"
    ]
    if not _uri_allowed(uri, allowed):
        raise HTTPException(status_code=403, detail=f"URI not exposed by this agent: {uri}")
    return _read_uri(uri)


@router.post("/commands")
def dispatch_command(request: CommandRequest) -> dict[str, Any]:
    allowed = [
        cap.get("command")
        for cap in AGENT_CARD["capabilities"]
        if cap.get("type") == "command"
    ]
    if request.command not in allowed:
        raise HTTPException(
            status_code=403,
            detail=f"Command not exposed by this agent: {request.command}",
        )
    command_uri = _command_uri(request.command)
    return _dispatch_command(request.command, request.payload, uri=command_uri)



@router.post("/skills/analyze_screenshot")
def skill_analyze_screenshot(payload: dict[str, Any]) -> dict[str, Any]:
    return _dispatch_command(
        "AnalyzeScreenshot",
        payload,
        uri="analysis://screenshots/analyze",
    )
@router.post("/skills/capture_and_analyze")
def skill_capture_and_analyze(payload: dict[str, Any]) -> dict[str, Any]:
    return _dispatch_command(
        "CaptureAndAnalyze",
        payload,
        uri="workflow://screenshots/capture-and-analyze",
    )
@router.post("/skills/scheduled_capture_analysis")
def skill_scheduled_capture_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    return _dispatch_command(
        "RunScheduledCaptureAnalysis",
        payload,
        uri="cron://screenshots/capture-analysis/every-5-min",
    )


def _uri_allowed(uri: str, templates: list[str | None]) -> bool:
    for template in templates:
        if not template:
            continue
        prefix = template.split("{")[0]
        if uri.startswith(prefix):
            return True
    return False


def _read_uri(uri: str) -> dict[str, Any]:
    scheme = urlparse(uri).scheme
    if scheme == "resource":
        return client.read_resource(uri)
    if scheme == "file":
        from uri3.resolvers.resolve_core import resolve

        resolved = resolve(uri)
        return {
            "ok": True,
            "uri": uri,
            "result_type": "file",
            "data": resolved.target,
        }
    from urish.backends.call import call_uri

    return call_uri(uri, {}, dry_run=False)


def _command_uri(command: str) -> str | None:
    for cap in AGENT_CARD["capabilities"]:
        if cap.get("type") == "command" and cap.get("command") == command:
            uri = cap.get("uri")
            return str(uri) if uri else None
    return None


def _dispatch_command(
    command: str,
    payload: dict[str, Any],
    *,
    uri: str | None = None,
) -> dict[str, Any]:
    if uri:
        from urish.backends.call import call_uri

        return call_uri(uri, payload, dry_run=bool(payload.get("dry_run", False)))
    return client.dispatch_command(command, payload)

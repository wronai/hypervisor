# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/hypervisor_dashboard_agent.yaml
# Contract hash: sha256:e4ec619a25955f0c7cfe29270e603cf7256c7840417f77ca63fd48173bda14b5

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
        "agent": "hypervisor-dashboard",
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


@router.get("/skills/process_view")
def skill_process_view(agent_id: str) -> dict[str, Any]:
    uri = "resource://dashboard/process/agent/{agent_id}/latest"
    uri = uri.replace("{agent_id}", agent_id)
    return _read_uri(uri)
@router.get("/skills/workflow_timeline")
def skill_workflow_timeline(workflow_id: str) -> dict[str, Any]:
    uri = "resource://dashboard/workflow/{workflow_id}/timeline"
    uri = uri.replace("{workflow_id}", workflow_id)
    return _read_uri(uri)
@router.get("/skills/incident_explain")
def skill_incident_explain(incident_id: str) -> dict[str, Any]:
    uri = "resource://dashboard/incident/{incident_id}/explain"
    uri = uri.replace("{incident_id}", incident_id)
    return _read_uri(uri)
@router.get("/skills/repair_diagnose")
def skill_repair_diagnose(agent_id: str) -> dict[str, Any]:
    uri = "resource://dashboard/repair/agent/{agent_id}/diagnosis"
    uri = uri.replace("{agent_id}", agent_id)
    return _read_uri(uri)

@router.post("/skills/repair_action")
def skill_repair_action(payload: dict[str, Any]) -> dict[str, Any]:
    return _dispatch_command(
        "ApplySafeRepair",
        payload,
        uri="repair://agent/{agent_id}/apply",
    )
@router.post("/skills/uri_call")
def skill_uri_call(payload: dict[str, Any]) -> dict[str, Any]:
    return _dispatch_command(
        "UriCall",
        payload,
        uri="hypervisor://dashboard/uri/call",
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

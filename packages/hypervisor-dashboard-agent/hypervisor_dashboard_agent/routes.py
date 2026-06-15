from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from hypervisor.paths import find_repo_root
from pydantic import BaseModel, Field

from hypervisor_dashboard_agent.agent_card import AGENT_CARD
from hypervisor_dashboard_agent.chat_format import (
    format_ask_markdown,
    format_uri_result_markdown,
)
from hypervisor_dashboard_agent.events_service import collect_system_events, filter_events_since
from hypervisor_dashboard_agent.monitor_webhook import write_monitor_webhook
from hypervisor_dashboard_agent.paths import repo_www_dir
from hypervisor_dashboard_agent.plan_runner import PlanRunOptions, run_planned_uris
from hypervisor_dashboard_agent.policy import decision_for_uri, preview_action
from hypervisor_dashboard_agent.uri_client import (
    call_system_uri,
    list_agent_deployments,
    resolve_view_uri,
    uri_implies_dry_run,
)

router = APIRouter()
templates = Jinja2Templates(
    directory=str(__import__("hypervisor_dashboard_agent").__path__[0] + "/templates")
)


class PlanRunRequest(BaseModel):
    planned_uris: list[str] = Field(..., min_length=1)
    approved: bool = False
    dry_run: bool = True
    policy: str = "dev"
    stop_on_error: bool = True
    auto_repair: bool = True
    retry_after_repair: bool = True
    speak_summary: bool = False


class VoiceSpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    voice: str = "mock"
    play: bool = True


class VoiceTranscribeRequest(BaseModel):
    audio_base64: str | None = None
    text: str | None = None
    language: str = "pl"
    mime_type: str | None = None
    engine: str = "auto"


class UriCallRequest(BaseModel):
    uri: str = Field(..., description="URI to execute through policy gate")
    approved: bool = False
    dry_run: bool = False
    readonly: bool = False
    policy: str = "dev"
    payload: dict[str, Any] = Field(default_factory=dict)


class AskRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Natural language prompt")
    dry_run: bool = True
    llm: bool = False


@router.get("/")
def root() -> RedirectResponse:
    if repo_www_dir():
        return RedirectResponse(url="/www/", status_code=302)
    return RedirectResponse(url="/ui/agents", status_code=302)


@router.get("/chat.html")
def chat_page_redirect() -> RedirectResponse:
    if repo_www_dir():
        return RedirectResponse(url="/www/chat.html", status_code=302)
    return RedirectResponse(url="/ui/agents", status_code=302)


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


@router.post("/api/ask")
def api_ask(body: AskRequest) -> dict[str, Any]:
    """Natural language → planned URIs and next steps (urish ask backend)."""
    from urish.backends.ask import ask_prompt

    envelope = ask_prompt(body.prompt, dry_run=body.dry_run, use_llm=body.llm)
    data = envelope.get("data")
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="ask backend returned invalid payload")
    markdown = format_ask_markdown(data)
    return {
        "ok": True,
        "message_markdown": markdown,
        "data": data,
        "envelope": envelope,
    }


@router.post("/api/uri/preview")
def api_uri_preview(body: UriCallRequest) -> dict[str, Any]:
    return preview_action(body.uri, policy=body.policy)


@router.post("/api/uri/call")
def api_uri_call(body: UriCallRequest) -> dict[str, Any]:
    implicit_dry_run = uri_implies_dry_run(body.uri)
    effective_dry_run = body.dry_run or implicit_dry_run
    decision = decision_for_uri(
        body.uri,
        approved=body.approved,
        dry_run=effective_dry_run,
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
            dry_run=decision.force_dry_run or effective_dry_run,
            payload=body.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - exercised through route tests
        result = {
            "ok": False,
            "result_type": "error",
            "uri": body.uri,
            "service_result_status": "failed",
            "workflow_status": "completed_with_service_error",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    result.setdefault("policy", {})
    result["policy"] = {
        "dry_run": decision.force_dry_run or effective_dry_run,
        "approved": body.approved,
        "policy": body.policy,
    }
    result["message_markdown"] = format_uri_result_markdown(result)
    if result.get("presentation_markdown"):
        result["message_markdown"] = result["presentation_markdown"]
    return result


@router.post("/api/plan/run")
def api_plan_run(body: PlanRunRequest) -> dict[str, Any]:
    """Execute a planned URI sequence with optional auto-repair and retry."""
    payload = run_planned_uris(
        PlanRunOptions(
            planned_uris=body.planned_uris,
            approved=body.approved,
            dry_run=body.dry_run,
            policy=body.policy,
            stop_on_error=body.stop_on_error,
            auto_repair=body.auto_repair,
            retry_after_repair=body.retry_after_repair,
        )
    )
    if body.speak_summary:
        payload["speech"] = _speak_plan_summary(payload)
    return payload


def _speak_plan_summary(payload: dict[str, Any]) -> dict[str, Any]:
    from uri2voice.tts import speak

    ok = bool(payload.get("ok"))
    count = int(payload.get("count") or 0)
    repairs = payload.get("repairs") or []
    text = (
        f"Plan zakończony. Kroki: {count}. Status: {'sukces' if ok else 'błąd'}."
        f" Naprawy automatyczne: {len(repairs)}."
    )
    envelope = speak({"text": text, "voice": "mock", "play": True})
    return {
        "ok": bool(envelope.get("ok")),
        "text": text,
        "artifact_uri": envelope.get("artifact_uri"),
        "playback": (envelope.get("data") or {}).get("playback"),
    }


@router.post("/api/voice/transcribe")
def api_voice_transcribe(body: VoiceTranscribeRequest) -> dict[str, Any]:
    payload = {
        "audio_base64": body.audio_base64,
        "text": body.text,
        "language": body.language,
        "mime_type": body.mime_type,
        "engine": body.engine,
    }
    if body.engine == "mock" or (body.text and not body.audio_base64):
        from uri2voice.stt import transcribe

        envelope = transcribe(payload)
    else:
        from uri2voice.stt_whisper import transcribe_whisper

        envelope = transcribe_whisper(payload)
    if not envelope.get("ok"):
        raise HTTPException(status_code=422, detail=envelope)
    return {
        "ok": True,
        "transcript": envelope.get("data") or {},
        "meta": envelope.get("meta") or {},
    }


@router.post("/api/voice/speak")
def api_voice_speak(body: VoiceSpeakRequest) -> dict[str, Any]:
    from uri2voice.tts import speak

    envelope = speak({"text": body.text, "voice": body.voice, "play": body.play})
    if not envelope.get("ok"):
        raise HTTPException(status_code=422, detail=envelope)
    return {
        "ok": True,
        "speech": envelope.get("data") or {},
        "artifact_uri": envelope.get("artifact_uri"),
        "meta": envelope.get("meta") or {},
    }


@router.get("/api/agents")
def api_agents() -> dict[str, Any]:
    return {"agents": list_agent_deployments()}


@router.get("/api/events")
def api_events(limit: int = 20, since: str | None = None) -> dict[str, Any]:
    """Unified event feed: incidents, monitor snapshots, agent health."""
    root = find_repo_root()
    events = collect_system_events(root=root, limit=max(1, min(limit, 100)))
    events = filter_events_since(events, since)
    return {
        "events": events,
        "limit": limit,
        "since": since,
        "source": "hypervisor.events",
    }


@router.post("/api/monitors/webhook")
async def api_monitor_webhook(request: Request) -> dict[str, Any]:
    """Ingest monitor/webhook JSON and surface it through /api/events + SSE."""
    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="request body must be JSON") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="request body must be a JSON object")
    root = find_repo_root()
    return write_monitor_webhook(payload, root=root)


@router.get("/api/events/stream")
async def api_events_stream(limit: int = 20, interval_s: float = 5.0) -> StreamingResponse:
    """SSE stream polling incidents, monitors, and agent health."""

    async def event_generator():
        root = find_repo_root()
        last_signature = ""
        poll_interval = max(2.0, min(interval_s, 30.0))
        while True:
            events = await asyncio.to_thread(
                collect_system_events,
                root=root,
                limit=max(1, min(limit, 100)),
            )
            signature = json.dumps(events, sort_keys=True, ensure_ascii=False)
            if signature != last_signature:
                payload = {"events": events, "source": "hypervisor.events.stream"}
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                last_signature = signature
            await asyncio.sleep(poll_interval)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

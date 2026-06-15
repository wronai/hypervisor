from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .agent_card import AGENT_CARD
from .analysis import analyze_artifact, capture_with_operator, repo_root

router = APIRouter()


class AnalyzeScreenshotRequest(BaseModel):
    artifact_uri: str = Field(..., description="artifact:// or file:// screenshot artifact")
    source_url: str | None = None
    run_label: str = "manual"


class CaptureAndAnalyzeRequest(BaseModel):
    operator_url: str = "http://localhost:8791"
    target_url: str = "http://localhost:8788/www/"
    adapter: str = "mock"
    approve: bool = True
    run_label: str = "agent-screenshot-analysis"


@router.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "agent": "screenshot-analysis-agent",
        "version": AGENT_CARD["version"],
    }


@router.get("/.well-known/agent-card.json")
def well_known_agent_card_json() -> dict[str, Any]:
    return AGENT_CARD


@router.get("/.well-known/agent.json")
def well_known_agent_json() -> dict[str, Any]:
    return AGENT_CARD


@router.get("/capabilities")
def capabilities() -> dict[str, Any]:
    return {"capabilities": AGENT_CARD["capabilities"]}


@router.post("/skills/analyze_screenshot")
def skill_analyze_screenshot(payload: AnalyzeScreenshotRequest) -> dict[str, Any]:
    return analyze_artifact(
        payload.artifact_uri,
        source_url=payload.source_url,
        run_label=payload.run_label,
        root=repo_root(),
    )


@router.post("/skills/capture_and_analyze")
def skill_capture_and_analyze(payload: CaptureAndAnalyzeRequest) -> dict[str, Any]:
    return capture_with_operator(
        operator_url=payload.operator_url,
        target_url=payload.target_url,
        adapter=payload.adapter,
        approve=payload.approve,
        run_label=payload.run_label,
        root=repo_root(),
    )


@router.post("/skills/run_scheduled_capture_analysis")
def skill_run_scheduled_capture_analysis(payload: CaptureAndAnalyzeRequest) -> dict[str, Any]:
    result = skill_capture_and_analyze(payload)
    result["schedule_uri"] = "cron://screenshots/capture-analysis/every-5-min"
    result["schedule"] = "*/5 * * * *"
    return result


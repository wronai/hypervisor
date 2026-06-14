"""
Taskinity API Bridge

Optional backend for the static www/ chat UI.

Run from repository root:

    pip install fastapi uvicorn
    python www/api-bridge/bridge.py

Then open:

    www/index.html

and set API URL to:

    http://localhost:8788

This bridge tries to call local CLI commands such as urish/hypervisor.
It is intentionally small and safe-by-default. Mutating commands should still
be guarded by policy/approval in the real backend.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="Taskinity API Bridge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UriCall(BaseModel):
    uri: str
    payload: dict[str, Any] = {}


class AskCall(BaseModel):
    prompt: str


def envelope(ok: bool, result_type: str, data: Any, **meta: Any) -> dict[str, Any]:
    return {
        "ok": ok,
        "workflow_status": "completed" if ok else "completed_with_service_error",
        "execution_status": "completed",
        "service_result_status": "succeeded" if ok else "failed",
        "result_type": result_type,
        "data": data,
        "meta": {
            "runtime": "taskinity-api-bridge",
            "transport": "http",
            **meta,
        },
    }


def run_cmd(args: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        parsed = None
        try:
            parsed = json.loads(proc.stdout)
        except Exception:
            parsed = None

        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "json": parsed,
        }
    except Exception as exc:
        return {
            "returncode": 999,
            "stdout": "",
            "stderr": str(exc),
            "json": None,
        }


@app.get("/health")
def health() -> dict[str, Any]:
    return envelope(True, "health", {"status": "ok", "service": "taskinity-api-bridge"})


@app.post("/api/uri/call")
def call_uri(body: UriCall) -> dict[str, Any]:
    uri = body.uri

    if uri.startswith("health://agent/"):
        agent_id = uri.removeprefix("health://agent/")
        result = run_cmd(["hypervisor", "agent-status", agent_id])
        if result["json"]:
            return result["json"]
        return envelope(result["returncode"] == 0, "agent_status", result, target=uri)

    if uri.startswith("repair://agent/") and uri.endswith("/diagnose"):
        agent_id = uri.removeprefix("repair://agent/").removesuffix("/diagnose")
        result = run_cmd(["urish", "repair", "diagnose", agent_id, "--json"])
        if result["json"]:
            return result["json"]
        return envelope(result["returncode"] == 0, "diagnosis", result, target=uri)

    if uri.startswith("repair://agent/") and uri.endswith("/apply"):
        agent_id = uri.removeprefix("repair://agent/").removesuffix("/apply")
        result = run_cmd(["urish", "repair", "apply", agent_id, "--dry-run", "--json"])
        if result["json"]:
            return result["json"]
        return envelope(result["returncode"] == 0, "repair_result", result, target=uri)

    if uri.startswith("view://process/agent/"):
        agent_id = uri.removeprefix("view://process/agent/").removesuffix("/latest")
        result = run_cmd(["hypervisor", "agent-status", agent_id])
        return envelope(
            result["returncode"] == 0,
            "process_view",
            {
                "uri": uri,
                "agent_id": agent_id,
                "what_happened": "API bridge pobrał status agenta przez hypervisor.",
                "why_it_matters": "Widok procesu łączy runtime, health i akcje naprawcze.",
                "raw": result,
            },
            target=uri,
        )

    # Generic fallback through urish call when available.
    result = run_cmd(["urish", "call", uri, "--payload", json.dumps(body.payload), "--json"])
    if result["json"]:
        return result["json"]
    return envelope(result["returncode"] == 0, "uri_call", result, target=uri)


@app.post("/api/nl/ask")
def ask(body: AskCall) -> dict[str, Any]:
    prompt = body.prompt.lower()
    agent = "weather-map-agent.local"

    # Very small deterministic NL mapper. Replace with urish ask / nl2uri if desired.
    if "diagnoz" in prompt:
        uri = f"repair://agent/{agent}/diagnose"
        intent = "diagnose_agent"
    elif "napraw" in prompt:
        uri = f"repair://agent/{agent}/apply"
        intent = "repair_agent"
    elif "health" in prompt or "sprawd" in prompt:
        uri = f"health://agent/{agent}"
        intent = "check_health"
    elif "ticket" in prompt:
        uri = "ticket://bug/from-incident/inc_20260614_001"
        intent = "create_ticket"
    elif "proposal" in prompt or "ewoluc" in prompt:
        uri = "evolution://proposal/from-ticket/PL-1"
        intent = "create_proposal"
    else:
        uri = f"view://process/agent/{agent}/latest"
        intent = "show_process"

    return envelope(True, "nl_plan", {
        "intent": intent,
        "uri": uri,
        "explanation": "Backend API zamienił polecenie naturalne na URI."
    }, prompt=body.prompt)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8788)

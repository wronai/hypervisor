# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_uri_smoke_agent.yaml
# Contract hash: sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="codex-uri-smoke-agent",
    version="0.1.0",
    description='Smoke-test agent for file and physical-operation URI provenance.',
)
app.include_router(router)

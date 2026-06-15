# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/schema_collab_agent.yaml
# Contract hash: sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="schema-collab-agent",
    version="0.1.0",
    description=('Generated from NL prompt: stworz nowego agenta schema-collab-agent, ktory czyta '
 'file:// README, sprawdza device://device/sensor-1/status i robot://robot/amr-1/state '
 'oraz ma komende cron monitor'),
)
app.include_router(router)

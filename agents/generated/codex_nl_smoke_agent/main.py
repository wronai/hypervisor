# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_nl_smoke_agent.yaml
# Contract hash: sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="codex-nl-smoke-agent",
    version="0.1.0",
    description=('Generated from NL prompt: stworz nowego agenta codex-nl-smoke-agent, ktory czyta '
 'file:// README, sprawdza device://device/sensor-1/status i ma komende cron monitor'),
)
app.include_router(router)

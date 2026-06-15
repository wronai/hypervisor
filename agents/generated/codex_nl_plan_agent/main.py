# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_nl_plan_agent.yaml
# Contract hash: sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="codex-nl-plan-agent",
    version="0.1.0",
    description=('Generated from NL prompt: stworz nowego agenta codex-nl-plan-agent, ktory czyta '
 'file:// README, sprawdza device://device/sensor-1/status i ma komende cron monitor'),
)
app.include_router(router)

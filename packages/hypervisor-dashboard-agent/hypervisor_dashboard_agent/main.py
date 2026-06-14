from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from hypervisor_dashboard_agent.agent_card import AGENT_CARD
from hypervisor_dashboard_agent.routes import router

_pkg_dir = Path(__file__).resolve().parent

app = FastAPI(
    title="hypervisor-dashboard",
    version=AGENT_CARD["version"],
    description=AGENT_CARD["description"],
)
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(_pkg_dir / "static")), name="static")

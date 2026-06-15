from __future__ import annotations

from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="remote-deploy-agent",
    version="0.1.0",
    description="Deploy, verify and start generated agents on remote SSH hosts.",
)
app.include_router(router)

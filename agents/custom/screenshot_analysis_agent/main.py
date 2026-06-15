from __future__ import annotations

from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="screenshot-analysis-agent",
    version="0.1.0",
    description="Analyze screenshot artifacts produced by desktop-operator.",
)
app.include_router(router)

from __future__ import annotations

from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="gnome-programmer-agent",
    version="0.1.0",
    description="Observe and interact with Ubuntu GNOME desktop through desktop-operator.",
)
app.include_router(router)

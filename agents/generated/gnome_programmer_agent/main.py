# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/gnome_programmer_agent.yaml
# Contract hash: sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="gnome-programmer-agent",
    version="0.1.0",
    description='Observe and interact with Ubuntu GNOME desktop through desktop-operator.',
)
app.include_router(router)

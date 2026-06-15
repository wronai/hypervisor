# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/weather_map_agent.yaml
# Contract hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="weather-map-agent",
    version="0.1.0",
    description='Generate forecast weather maps as HTML URL artifacts.',
)
app.include_router(router)

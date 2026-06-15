# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/screenshot_analysis_agent.yaml
# Contract hash: sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="screenshot-analysis-agent",
    version="0.1.0",
    description='Analyze screenshot artifacts captured by desktop-operator and persist observations.',
)
app.include_router(router)

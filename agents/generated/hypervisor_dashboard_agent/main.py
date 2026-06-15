# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/hypervisor_dashboard_agent.yaml
# Contract hash: sha256:e4ec619a25955f0c7cfe29270e603cf7256c7840417f77ca63fd48173bda14b5

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="hypervisor-dashboard",
    version="0.1.0",
    description='System observer/renderer agent — URI process dashboard with approval-gated actions.',
)
app.include_router(router)

# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/user_agent.yaml
# Contract hash: sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="user-agent",
    version="0.1.0",
    description='Thin generated agent for reading users and dispatching user commands.',
)
app.include_router(router)

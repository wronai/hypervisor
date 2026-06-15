# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/remote_deploy_agent.yaml
# Contract hash: sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="remote-deploy-agent",
    version="0.1.0",
    description='Deploy, verify and start generated agents on remote SSH hosts.',
)
app.include_router(router)

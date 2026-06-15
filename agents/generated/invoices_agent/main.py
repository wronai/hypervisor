# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/invoices_agent.yaml
# Contract hash: sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960

from __future__ import annotations

from fastapi import FastAPI

try:
    from .routes import router
except ImportError:  # standalone rsync package on remote host
    from routes import router

app = FastAPI(
    title="invoices-agent",
    version="0.1.0",
    description='Generated thin agent for invoices resources.',
)
app.include_router(router)

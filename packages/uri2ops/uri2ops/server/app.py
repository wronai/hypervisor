from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from uri2ops import __version__
from uri2ops.operation_registry.dispatcher import dispatch
from uri2ops.server.a2a_wrapper import build_agent_card
from uri2ops.server.mcp_wrapper import list_mcp_tools, mcp_tool_name_for_operation
from uri2ops.server.service import OperatorService


class TaskRequest(BaseModel):
    task: dict[str, Any]
    dry_run: bool = False
    approve: bool = False
    adapter: str = "mock"


class McpToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


def create_app(*, root: Path | None = None, base_url: str = "http://127.0.0.1:8791") -> FastAPI:
    service = OperatorService(root=root)
    app = FastAPI(title="uri2ops", version=__version__)

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "service": "uri2ops", "version": __version__}

    @app.get("/registry")
    def registry_export() -> dict[str, Any]:
        return service.registry_export()

    @app.get("/operations")
    def operations_list() -> dict[str, Any]:
        return {"operations": service.list_operations()}

    @app.get("/operations/{scheme}/{operation}")
    def operations_describe(scheme: str, operation: str) -> dict[str, Any]:
        try:
            return service.describe_operation(scheme, operation).to_dict()
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/registry/sources")
    def registry_sources() -> dict[str, Any]:
        return {"sources": service.list_registry_sources()}

    @app.post("/validate")
    def validate_task(body: TaskRequest) -> dict[str, Any]:
        errors = service.validate_task(body.task)
        return {"ok": not errors, "errors": errors}

    @app.post("/plan")
    def plan_task(body: TaskRequest) -> dict[str, Any]:
        errors = service.validate_task(body.task)
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        return {"task": body.task.get("task", {}).get("id"), "plan": service.plan_task(body.task)}

    @app.post("/run")
    def run_task(body: TaskRequest) -> dict[str, Any]:
        errors = service.validate_task(body.task)
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        return service.run_task(
            body.task,
            dry_run=body.dry_run,
            approve=body.approve,
            adapter=body.adapter,
        )

    @app.get("/.well-known/agent-card.json")
    def agent_card() -> dict[str, Any]:
        return build_agent_card(base_url, service.registry())

    @app.post("/a2a/tasks")
    def a2a_tasks(body: TaskRequest) -> dict[str, Any]:
        return run_task(body)

    @app.get("/mcp/tools")
    def mcp_tools() -> dict[str, Any]:
        return {"tools": list_mcp_tools(service.registry())}

    @app.post("/mcp/tools/call")
    def mcp_tools_call(body: McpToolCallRequest) -> dict[str, Any]:
        if body.name == "run_operator_task":
            task = body.arguments.get("task")
            if not isinstance(task, dict):
                raise HTTPException(status_code=400, detail="arguments.task must be an object")
            return service.run_task(
                task,
                dry_run=bool(body.arguments.get("dry_run")),
                approve=bool(body.arguments.get("approve")),
                adapter=str(body.arguments.get("adapter") or "mock"),
            )
        registry = service.registry()
        for spec in registry.list():
            if mcp_tool_name_for_operation(spec.scheme, spec.operation) != body.name:
                continue
            uri = str(body.arguments.get("uri") or f"{spec.scheme}://local/{spec.operation}")
            payload = dict(body.arguments.get("payload") or {})
            payload.setdefault("target_uri", uri)
            context = {
                "adapter": str(body.arguments.get("adapter") or "mock"),
                "task_id": "mcp-call",
                "run_id": body.name,
                "root": str(service.root),
                "session": {},
            }
            if spec.requires_policy and not body.arguments.get("approve"):
                raise HTTPException(status_code=403, detail=f"{body.name} requires approve=true")
            try:
                return dispatch(spec.scheme, spec.operation, payload, context)
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
        raise HTTPException(status_code=404, detail=f"Unknown MCP tool: {body.name}")

    return app

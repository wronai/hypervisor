from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlparse

from uri2ops.operation_registry.dispatcher import call_handler
from uri2ops.operator.adapters.browser_router import cleanup_browser_session
from uri2ops.remote_registry.loader import resolve_operation_registry
from uri3.graph.artifacts import write_artifact
from uri3.graph.execution_models import ExecutionContext
from uri3.graph.models import GraphNode

OPERATOR_SCHEMES = frozenset({"browser", "dom", "screen", "input"})

# Map uri3 workflow operations to uri2ops registry operations.
_OPERATION_MAP: dict[tuple[str, str], str] = {
    ("browser", "read"): "extract_dom",
    ("browser", "extract"): "extract_dom",
    ("dom", "read"): "extract_dom",
    ("dom", "extract"): "extract_dom",
    ("dom", "extract_dom"): "extract_dom",
    ("browser", "capture"): "screenshot",
    ("browser", "screenshot"): "screenshot",
    ("screen", "capture"): "observe",
    ("screen", "screenshot"): "observe",
    ("input", "call"): "type",
    ("input", "type"): "type",
}


def _use_legacy_browser_adapter() -> bool:
    return os.getenv("URI3_USE_LEGACY_BROWSER", "").lower() in {"1", "true", "yes"}


def _registry_scheme(scheme: str) -> str:
    if scheme == "dom":
        return "browser"
    return scheme


def _registry_operation(scheme: str, operation: str) -> str:
    return _OPERATION_MAP.get((scheme, operation), operation)


def _runtime_context(context: ExecutionContext) -> dict[str, Any]:
    state = context.adapter_state.setdefault("uri2ops", {})
    session = state.setdefault("session", {})
    return {
        "adapter": context.browser_mode,
        "root": str(context.root),
        "task_id": context.workflow_id,
        "run_id": context.run_id,
        "session": session,
    }


def _artifact_suffix(scheme: str, operation: str) -> str | None:
    if scheme == "browser" and operation == "open":
        return "open.json"
    if scheme in {"browser", "dom"} and operation in {"read", "extract", "extract_dom"}:
        return "dom.json"
    if scheme in {"browser", "screen"} and operation in {"screenshot", "capture"}:
        return "screenshot.png"
    if scheme == "screen" and operation == "observe":
        return "screenshot.png"
    return None


def _attach_workflow_artifact(
    node: GraphNode,
    context: ExecutionContext,
    payload: dict[str, Any],
) -> dict[str, Any]:
    scheme = urlparse(node.uri).scheme
    operation = _registry_operation(scheme, node.operation)
    suffix = _artifact_suffix(scheme, operation)
    if suffix is None:
        return payload

    if suffix.endswith(".json"):
        body = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        body = b"mock-screenshot\n"
    _, artifact_uri = write_artifact(context, node.id, suffix, body)
    return {**payload, "artifact_uri": artifact_uri}


class Uri2OpsAdapter:
    """Delegates operator schemes to uri2ops operation registry."""

    schemes = OPERATOR_SCHEMES

    def execute(self, node: GraphNode, context: ExecutionContext) -> dict[str, Any]:
        scheme = urlparse(node.uri).scheme
        registry_scheme = _registry_scheme(scheme)
        registry_operation = _registry_operation(scheme, node.operation)
        registry = resolve_operation_registry(root=context.root)
        spec = registry.require(registry_scheme, registry_operation)

        payload = dict(node.payload or {})
        payload.setdefault("target_uri", node.uri)
        payload.setdefault("step_id", node.id)

        runtime_context = _runtime_context(context)
        output = call_handler(spec, payload, runtime_context)
        if not bool(output.get("ok", True)):
            return output
        return _attach_workflow_artifact(node, context, output)


def cleanup_operator_adapters(context: ExecutionContext) -> None:
    uri2ops_state = context.adapter_state.get("uri2ops")
    if isinstance(uri2ops_state, dict):
        cleanup_browser_session(uri2ops_state)


def resolve_operator_adapter(context: ExecutionContext) -> str:
    if _use_legacy_browser_adapter():
        return "legacy"
    return "uri2ops"

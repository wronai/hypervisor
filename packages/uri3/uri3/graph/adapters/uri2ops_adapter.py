from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from uri2ops.operation_registry.dispatcher import call_handler
from uri2ops.operation_registry.uri_mapping import registry_operation, registry_scheme
from uri2ops.operator.adapters.browser_router import cleanup_browser_session
from uri2ops.remote_registry.loader import resolve_operation_registry

from uri3.graph.artifacts import mock_screenshot_png, write_artifact
from uri3.graph.execution_models import ExecutionContext
from uri3.graph.models import GraphNode

OPERATOR_SCHEMES = frozenset({"browser", "dom", "screen", "input"})


def _use_legacy_browser_adapter() -> bool:
    return os.getenv("URI3_USE_LEGACY_BROWSER", "").lower() in {"1", "true", "yes"}


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
    if scheme in {"browser", "screen"} and operation in {"screenshot", "capture", "capture_page"}:
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
    operation = registry_operation(scheme, node.operation)
    suffix = _artifact_suffix(scheme, operation)
    if suffix is None:
        return payload

    if suffix.endswith(".json"):
        body = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        # For screenshots we must emit *valid* PNG bytes so the artifact is a real image file.
        # If the underlying handler provided a real capture path, re-use its bytes.
        real_path = payload.get("path")
        if real_path:
            rp = Path(real_path)
            body = rp.read_bytes() if rp.exists() else mock_screenshot_png()
        else:
            body = mock_screenshot_png()
    _, artifact_uri = write_artifact(context, node.id, suffix, body)
    return {**payload, "artifact_uri": artifact_uri}


class Uri2OpsAdapter:
    """Delegates operator schemes to uri2ops operation registry."""

    schemes = OPERATOR_SCHEMES

    def execute(self, node: GraphNode, context: ExecutionContext) -> dict[str, Any]:
        scheme = urlparse(node.uri).scheme
        registry_scheme_name = registry_scheme(scheme)
        registry_operation_name = registry_operation(scheme, node.operation)
        registry = resolve_operation_registry(root=context.root)
        spec = registry.require(registry_scheme_name, registry_operation_name)

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

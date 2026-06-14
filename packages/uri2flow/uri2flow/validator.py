from __future__ import annotations

from pathlib import Path
from typing import Any

from uri3.graph.graph_validator import validate_workflow_graph

from .expander import expand_flow
from .parser import FlowParseError, load_flow, parse_flow


def validate_flow_document(data: dict[str, Any]) -> list[str]:
    """Validate compact flow structure. Returns non-fatal warnings."""
    try:
        flow = parse_flow(data)
    except FlowParseError as exc:
        raise ValueError(str(exc)) from exc

    warnings: list[str] = []
    seen_ids: set[str] = set()
    for index, step in enumerate(flow.steps):
        if not step.uri or "://" not in step.uri:
            raise ValueError(f"step {index + 1} has invalid URI: {step.uri!r}")
        if step.id:
            if step.id in seen_ids:
                raise ValueError(f"duplicate step id: {step.id}")
            seen_ids.add(step.id)
        for dep in step.after:
            if dep not in seen_ids:
                warnings.append(f"step {step.id or step.uri} references dependency not seen earlier: {dep}")
    return warnings


def validate_expanded_flow(data: dict[str, Any]) -> list[str]:
    """Validate compact flow and its expanded workflow graph."""
    warnings = validate_flow_document(data)
    graph_errors = validate_workflow_graph(expand_flow(data))
    if graph_errors:
        raise ValueError("; ".join(graph_errors[:5]))
    return warnings


def validate_flow(path: str | Path) -> list[str]:
    """Validate compact flow file. Returns warnings, raises on hard errors."""
    flow = load_flow(path)
    data = {
        "flow": {"id": flow.id, "description": flow.description},
        "do": [],
    }
    for step in flow.steps:
        if step.id or step.after or step.condition or step.payload:
            item: dict[str, Any] = {"uri": step.uri}
            if step.id:
                item["id"] = step.id
            if step.payload:
                item["with"] = step.payload
            if step.after:
                item["after"] = step.after[0] if len(step.after) == 1 else step.after
            if step.condition:
                item["if"] = step.condition
            data["do"].append(item)
        else:
            data["do"].append(step.uri)
    return validate_flow_document(data)

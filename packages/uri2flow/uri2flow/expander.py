from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import FlowDocument, FlowStep
from .parser import load_flow, parse_flow
from .resolver import default_operation_for_uri
from .utils import node_id_from_uri


def _node_from_step(step: FlowStep, previous_id: str | None, used: set[str]) -> dict[str, Any]:
    defaults = default_operation_for_uri(step.uri)
    node_id = step.id or node_id_from_uri(step.uri, used)
    depends_on = step.after or ([previous_id] if previous_id else [])
    node: dict[str, Any] = {
        "id": node_id,
        "uri": step.uri,
        "operation": step.operation or defaults.operation,
        "kind": step.kind or defaults.kind,
    }
    if step.payload:
        node["payload"] = step.payload
    if depends_on:
        node["depends_on"] = depends_on
    if step.condition:
        node["condition"] = {"if": step.condition} if isinstance(step.condition, str) else step.condition
    if defaults.requires_approval:
        node["requires_approval"] = True
    return node


def _edges_from_depends(nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    edges = []
    for node in nodes:
        for dep in node.get("depends_on", []) or []:
            edges.append({"from": dep, "to": node["id"], "type": "depends_on"})
    return edges


def expand_flow(flow: FlowDocument | dict[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(flow, (str, Path)):
        flow_doc = load_flow(flow)
    elif isinstance(flow, dict):
        flow_doc = parse_flow(flow)
    else:
        flow_doc = flow

    used: set[str] = set()
    nodes: list[dict[str, Any]] = []
    previous_id: str | None = None
    for step in flow_doc.steps:
        node = _node_from_step(step, previous_id, used)
        nodes.append(node)
        previous_id = node["id"]

    graph: dict[str, Any] = {
        "id": flow_doc.id,
        "version": 1,
        "kind": "workflow",
        "nodes": nodes,
        "edges": _edges_from_depends(nodes),
    }
    if flow_doc.description:
        graph["description"] = flow_doc.description

    return {
        "nl2uri": {
            "version": 1,
            "kind": "workflow_graph",
            "source": "compact_uri_flow",
            **({"source_prompt": flow_doc.source_prompt} if flow_doc.source_prompt else {}),
        },
        "graph": graph,
    }


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

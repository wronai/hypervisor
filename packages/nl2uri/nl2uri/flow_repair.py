from __future__ import annotations

import re
from typing import Any

from uri2flow.utils import node_id_from_uri, slugify
from uri2flow.validator import validate_expanded_flow
from uri3.graph.operation_registry import OPERATIONS_BY_SCHEME, scheme_from_uri


def _slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "flow"


def _supported_scheme(uri: str) -> bool:
    scheme = scheme_from_uri(uri)
    return bool(scheme) and scheme in OPERATIONS_BY_SCHEME


def _normalize_step_raw(raw: Any) -> str | dict[str, Any] | None:
    if isinstance(raw, str):
        value = raw.strip()
        return value if "://" in value else None
    if not isinstance(raw, dict):
        return None
    if "uri" in raw:
        return dict(raw)
    if len(raw) == 1:
        uri, payload = next(iter(raw.items()))
        uri = str(uri).strip()
        if "://" not in uri:
            return None
        if payload is None:
            return uri
        if isinstance(payload, dict):
            return {uri: payload}
        return None
    if isinstance(raw.get("step"), dict):
        return dict(raw["step"])
    return None


def _node_to_compact_step(node: dict[str, Any]) -> dict[str, Any]:
    step: dict[str, Any] = {"uri": str(node["uri"])}
    if node.get("id"):
        step["id"] = str(node["id"])
    payload = node.get("payload") or node.get("with") or {}
    if isinstance(payload, dict) and payload:
        step["with"] = dict(payload)
    depends_on = node.get("after") or node.get("depends_on")
    if depends_on:
        step["after"] = depends_on[0] if isinstance(depends_on, list) and len(depends_on) == 1 else depends_on
    condition = node.get("if") or node.get("condition")
    if isinstance(condition, dict):
        condition = condition.get("if")
    if condition:
        step["if"] = str(condition)
    return step


def _nodes_to_compact_steps(nodes: list[dict[str, Any]]) -> list[str | dict[str, Any]]:
    return [_node_to_compact_step(node) for node in nodes if isinstance(node, dict) and node.get("uri")]


def extract_flow_payload(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("LLM flow planner did not return a JSON object")
    body = {key: value for key, value in raw.items() if key != "nl2uri"}
    if "flow" in body and "do" in body:
        return {"flow": body["flow"], "do": body["do"]}
    if "do" in body:
        return {"flow": body.get("flow") or {}, "do": body["do"]}
    if "steps" in body:
        flow_meta = body.get("flow") if isinstance(body.get("flow"), dict) else {}
        if not flow_meta and isinstance(body.get("task"), dict):
            flow_meta = {
                "id": body["task"].get("id"),
                "description": body["task"].get("description"),
            }
        return {"flow": flow_meta, "do": body["steps"]}
    if "graph" in body and isinstance(body["graph"], dict):
        graph = body["graph"]
        nodes = graph.get("nodes") or []
        if isinstance(nodes, dict):
            nodes = [dict(value, id=node_id) for node_id, value in nodes.items()]
        return {
            "flow": {
                "id": graph.get("id"),
                "description": graph.get("description"),
            },
            "do": _nodes_to_compact_steps(list(nodes)),
        }
    if "nodes" in body:
        nodes = body["nodes"]
        if isinstance(nodes, dict):
            nodes = [dict(value, id=node_id) for node_id, value in nodes.items()]
        return {
            "flow": {"id": body.get("id"), "description": body.get("description")},
            "do": _nodes_to_compact_steps(list(nodes)),
        }
    raise ValueError("LLM response missing flow/do, steps, or graph nodes")


def sanitize_flow_step(raw: Any, *, warnings: list[str], index: int) -> str | dict[str, Any] | None:
    normalized = _normalize_step_raw(raw)
    if normalized is None:
        warnings.append(f"dropped step {index + 1}: invalid shape {raw!r}")
        return None
    if isinstance(normalized, str):
        if not _supported_scheme(normalized):
            warnings.append(f"dropped step {index + 1}: unsupported URI {normalized!r}")
            return None
        return normalized

    uri = str(normalized.get("uri") or "").strip()
    if not uri or "://" not in uri:
        warnings.append(f"dropped step {index + 1}: missing uri")
        return None
    if not _supported_scheme(uri):
        warnings.append(f"dropped step {index + 1}: unsupported scheme in {uri!r}")
        return None

    step: dict[str, Any] = {"uri": uri}
    if normalized.get("id"):
        step["id"] = str(normalized["id"])
    payload = normalized.get("with") or normalized.get("payload") or {}
    if isinstance(payload, dict) and payload:
        step["with"] = dict(payload)
    after = normalized.get("after") or normalized.get("depends_on")
    if after:
        step["after"] = after
    condition = normalized.get("if") or normalized.get("condition")
    if isinstance(condition, dict):
        condition = condition.get("if")
    if condition:
        step["if"] = str(condition)
    return step


def _needs_explicit_ids(steps: list[str | dict[str, Any]]) -> bool:
    return any(isinstance(step, dict) and (step.get("after") or step.get("if")) for step in steps)


def _ensure_step_ids(steps: list[str | dict[str, Any]], *, warnings: list[str]) -> list[str | dict[str, Any]]:
    if not _needs_explicit_ids(steps):
        return steps
    used: set[str] = set()
    normalized: list[str | dict[str, Any]] = []
    for step in steps:
        if isinstance(step, str):
            step_id = node_id_from_uri(step, used)
            normalized.append({"id": step_id, "uri": step})
            continue
        item = dict(step)
        if not item.get("id"):
            item["id"] = node_id_from_uri(str(item["uri"]), used)
            warnings.append(f"assigned id {item['id']!r} to step {item['uri']!r}")
        else:
            used.add(str(item["id"]))
        normalized.append(item)

    known_ids = {str(step["id"]) for step in normalized if isinstance(step, dict) and step.get("id")}
    for step in normalized:
        if not isinstance(step, dict) or not step.get("after"):
            continue
        after = step["after"]
        if isinstance(after, str):
            refs = [after]
        elif isinstance(after, list):
            refs = [str(item) for item in after]
        else:
            continue
        kept = [ref for ref in refs if ref in known_ids]
        dropped = set(refs) - set(kept)
        if dropped:
            warnings.append(f"{step.get('id', step['uri'])}: removed unknown after {sorted(dropped)!r}")
        if kept:
            step["after"] = kept[0] if len(kept) == 1 else kept
        else:
            del step["after"]
    return normalized


def repair_flow_body(raw: dict[str, Any], prompt: str) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    body = extract_flow_payload(raw)
    flow_meta = dict(body.get("flow") or {})
    if not isinstance(flow_meta, dict):
        flow_meta = {}
    flow_meta.setdefault("id", slugify(str(flow_meta.get("id") or _slug(prompt[:80]))))
    flow_meta.setdefault("description", prompt.strip())

    sanitized: list[str | dict[str, Any]] = []
    for index, item in enumerate(body.get("do") or []):
        step = sanitize_flow_step(item, warnings=warnings, index=index)
        if step is not None:
            sanitized.append(step)
    if not sanitized:
        raise ValueError("no valid flow steps remain after repair")

    sanitized = _ensure_step_ids(sanitized, warnings=warnings)
    return {"flow": flow_meta, "do": sanitized}, warnings


def validate_flow_document(data: dict[str, Any]) -> list[str]:
    from uri2flow.validator import validate_flow_document as _validate

    return _validate(data)


def validate_expanded_flow(data: dict[str, Any]) -> list[str]:
    from uri2flow.validator import validate_expanded_flow as _validate

    return _validate(data)


def repair_and_validate_flow(
    raw: dict[str, Any],
    prompt: str,
    *,
    nl2uri_wrapper: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    body, warnings = repair_flow_body(raw, prompt)
    payload = dict(nl2uri_wrapper or {})
    payload.update(body)
    flow_warnings = validate_expanded_flow(payload)
    return body, warnings + flow_warnings

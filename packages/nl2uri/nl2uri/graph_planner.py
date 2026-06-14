from __future__ import annotations

import re
from typing import Any

from nl2uri.domain_planner import plan_from_prompt
from nl2uri.output_classifier import classify_output_kind

DEFAULT_HEALTH = "http://localhost:8101/health"
DEFAULT_CARD = "http://localhost:8101/.well-known/agent-card.json"
WEATHER_AGENT = "weather-map-agent"
WEATHER_DEPLOYMENT = "weather-map-agent.local"


def _slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "task"


def _detect_agent_id(prompt: str) -> str:
    if re.search(r"pogod|weather", prompt, re.I):
        return WEATHER_AGENT
    match = re.search(r"agent[a]?[:\s]+([a-z0-9-]+)", prompt, re.I)
    if match:
        return match.group(1)
    return WEATHER_AGENT


def _detect_health_uri(prompt: str) -> str:
    match = re.search(r"https?://[^\s,]+", prompt)
    if match:
        return match.group(0).rstrip(".,)")
    if re.search(r"localhost:\d+", prompt, re.I):
        port = re.search(r"localhost:(\d+)", prompt, re.I)
        if port:
            return f"http://localhost:{port.group(1)}/health"
    return DEFAULT_HEALTH


def wrap_nl2uri_output(kind: str, prompt: str, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "nl2uri": {
            "version": 1,
            "kind": kind,
            "source_prompt": prompt,
        },
        **body,
    }


def plan_single(prompt: str, *, use_llm: bool = False) -> dict[str, Any]:
    del use_llm
    agent_id = _detect_agent_id(prompt)
    if re.search(r"\bstatus\b", prompt, re.I):
        uri = f"agent://{agent_id}/status"
        operation = "read"
    elif re.search(r"\bhealth\b", prompt, re.I):
        uri = _detect_health_uri(prompt)
        operation = "read"
    elif re.search(r"\bcard\b", prompt, re.I):
        uri = DEFAULT_CARD
        operation = "read"
    else:
        uri = f"agent://{agent_id}"
        operation = "read"
    return wrap_nl2uri_output("single_uri", prompt, {"uri": uri, "operation": operation})


def plan_list(prompt: str, *, use_llm: bool = False) -> dict[str, Any]:
    del use_llm
    health_uri = _detect_health_uri(prompt)
    card_uri = DEFAULT_CARD
    uris = [
        {"uri": health_uri, "operation": "read"},
        {"uri": card_uri, "operation": "read"},
    ]
    if re.search(r"\blog", prompt, re.I):
        uris.append({"uri": f"log://{WEATHER_DEPLOYMENT}?limit=100", "operation": "read"})
    return wrap_nl2uri_output("uri_list", prompt, {"uris": uris})


def plan_tree(prompt: str, *, use_llm: bool = False) -> dict[str, Any]:
    tree_data = plan_from_prompt(prompt, use_llm=use_llm)
    children: list[str] = []
    for group in ("inputs", "commands", "resources", "artifacts"):
        for item in (tree_data.get(group) or {}).values():
            uri = item.get("uri") or item.get("uri_template")
            if uri:
                children.append(uri)
    agent = tree_data.get("agent") or {}
    if agent.get("uri"):
        children.append(agent["uri"])
    if agent.get("card_uri"):
        children.append(agent["card_uri"])
    return wrap_nl2uri_output(
        "resource_tree",
        prompt,
        {
            "tree": {
                "root": tree_data.get("domain", {}).get("uri"),
                "children": children,
            },
            "uri_tree": tree_data,
        },
    )


def plan_task(prompt: str, *, use_llm: bool = False) -> dict[str, Any]:
    if use_llm:
        from nl2uri.graph_planner_llm import plan_graph_with_llm

        return plan_graph_with_llm(prompt, kind="task_graph")
    health_uri = _detect_health_uri(prompt)
    task_id = _slug(prompt[:80])
    steps = [
        {
            "id": "open_health",
            "uri": "browser://chrome/page/open",
            "operation": "open",
            "kind": "command",
            "payload": {"url": health_uri},
        },
        {
            "id": "extract_body",
            "uri": "dom://chrome/active/body",
            "operation": "read",
            "kind": "query",
            "depends_on": ["open_health"],
        },
        {
            "id": "verify_ok",
            "uri": "assertion://contains",
            "operation": "check",
            "kind": "assertion",
            "payload": {"actual_from": "extract_body.text", "expected": "ok"},
            "depends_on": ["extract_body"],
        },
    ]
    if re.search(r"screenshot", prompt, re.I):
        steps.append(
            {
                "id": "capture_screenshot",
                "uri": "screen://browser/active/screenshot",
                "operation": "capture",
                "kind": "query",
                "depends_on": ["verify_ok"],
                "produces": ["artifact://operator/screenshots/health-check.png"],
            }
        )
    return wrap_nl2uri_output(
        "task_graph",
        prompt,
        {
            "task": {
                "id": task_id,
                "description": prompt.strip(),
            },
            "steps": steps,
        },
    )


def plan_workflow_graph(prompt: str, *, use_llm: bool = False) -> dict[str, Any]:
    if use_llm:
        from nl2uri.graph_planner_llm import plan_graph_with_llm

        return plan_graph_with_llm(prompt, kind="workflow_graph")
    text = prompt.strip()
    graph_id = _slug(text[:80])
    nodes: list[dict[str, Any]] = []

    if re.search(r"\b(wygeneruj|generuj|stw[oó]rz)\b", text, re.I):
        nodes.extend(
            [
                {
                    "id": "generate_weather_domain",
                    "type": "domain_pack",
                    "uri": "domain://weather-map",
                    "operation": "generate",
                    "kind": "command",
                },
                {
                    "id": "generate_weather_agent",
                    "type": "agent",
                    "uri": f"agent://{WEATHER_AGENT}",
                    "operation": "generate",
                    "kind": "command",
                    "depends_on": ["generate_weather_domain"],
                },
            ]
        )

    if re.search(r"\b(uruchom|run)\b", text, re.I):
        nodes.append(
            {
                "id": "run_weather_agent",
                "type": "deployment",
                "uri": f"hypervisor://deployment/{WEATHER_DEPLOYMENT}/run",
                "operation": "run",
                "kind": "command",
                "depends_on": [nodes[-1]["id"]] if nodes else [],
            }
        )

    health_uri = _detect_health_uri(text)
    browser_dep = [nodes[-1]["id"]] if nodes else []
    nodes.extend(
        [
            {
                "id": "open_health",
                "type": "browser",
                "uri": "browser://chrome/page/open",
                "operation": "open",
                "kind": "command",
                "payload": {"url": health_uri},
                **({"depends_on": browser_dep} if browser_dep else {}),
            },
            {
                "id": "read_health_dom",
                "type": "browser",
                "uri": "dom://chrome/active/body",
                "operation": "read",
                "kind": "query",
                "depends_on": ["open_health"],
            },
            {
                "id": "verify_ok",
                "type": "assertion",
                "uri": "assertion://contains",
                "operation": "check",
                "kind": "assertion",
                "depends_on": ["read_health_dom"],
                "payload": {"actual_from": "read_health_dom.text", "expected": "ok"},
            },
        ]
    )

    if re.search(r"\b(restart|zrestartuj|nie dzia[lł]a)\b", text, re.I):
        nodes.extend(
            [
                {
                    "id": "health",
                    "uri": health_uri,
                    "operation": "query",
                    "kind": "query",
                    "depends_on": browser_dep or [],
                },
                {
                    "id": "card",
                    "uri": DEFAULT_CARD,
                    "operation": "query",
                    "kind": "query",
                    "depends_on": browser_dep or [],
                },
                {
                    "id": "logs",
                    "uri": f"log://{WEATHER_DEPLOYMENT}?limit=100",
                    "operation": "query",
                    "kind": "query",
                    "depends_on": ["health"],
                },
                {
                    "id": "restart",
                    "uri": f"hypervisor://deployment/{WEATHER_DEPLOYMENT}/restart",
                    "operation": "command",
                    "kind": "command",
                    "depends_on": ["health"],
                    "condition": {"if": "health.ok == false"},
                },
            ]
        )
    elif re.search(r"\blog", text, re.I):
        nodes.append(
            {
                "id": "read_logs_if_failed",
                "type": "log",
                "uri": f"log://{WEATHER_DEPLOYMENT}?limit=100",
                "operation": "read",
                "kind": "query",
                "depends_on": ["verify_ok"],
                "condition": {"if": "verify_ok.ok == false"},
            }
        )

    if not nodes:
        return plan_task(prompt, use_llm=use_llm)

    return wrap_nl2uri_output(
        "workflow_graph",
        prompt,
        {
            "graph": {
                "id": graph_id,
                "version": 1,
                "kind": "workflow",
                "description": text,
                "nodes": nodes,
            }
        },
    )


def plan_auto(prompt: str, *, use_llm: bool = False) -> dict[str, Any]:
    kind = classify_output_kind(prompt)
    return plan_by_kind(prompt, kind=kind, use_llm=use_llm)


def plan_by_kind(prompt: str, *, kind: str, use_llm: bool = False) -> dict[str, Any]:
    if kind == "uri_flow":
        from nl2uri.flow_planner import plan_flow

        return plan_flow(prompt, use_llm=use_llm)
    planners = {
        "single_uri": plan_single,
        "uri_list": plan_list,
        "resource_tree": plan_tree,
        "task_graph": plan_task,
        "workflow_graph": plan_workflow_graph,
    }
    planner = planners.get(kind, plan_single)
    return planner(prompt, use_llm=use_llm)

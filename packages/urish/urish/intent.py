from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from urigen.models import wants_dashboard

from urish.scenario_registry import try_scenario_intent

DASHBOARD_PLANNED_URIS = [
    "agent://hypervisor-dashboard",
    "deployment://hypervisor-dashboard.local",
    "view://process/agent/{agent_id}/latest",
    "view://workflow/{workflow_id}/timeline",
    "view://incident/{incident_id}/explain",
    "repair://agent/{agent_id}/diagnose",
    "repair://agent/{agent_id}/apply",
    "ticket://bug/from-incident/{incident_id}",
]

_AGENT_ID_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"agent://([\w.-]+)", re.I),
    re.compile(r"\b([\w][\w-]*-agent\.local)\b", re.I),
    re.compile(r"\b(hypervisor-dashboard(?:\.local)?)\b", re.I),
    re.compile(r"\b(?:agent|agenta)\s+([\w][\w.-]+(?:\.local)?)\b", re.I),
    re.compile(r"\b([\w][\w-]*\.local)\b", re.I),
)


def extract_agent_id(prompt: str) -> str | None:
    text = prompt.strip()
    for pattern in _AGENT_ID_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        agent_id = match.group(1).strip(".")
        if agent_id == "hypervisor-dashboard":
            return "hypervisor-dashboard.local"
        if agent_id.endswith(".local"):
            return agent_id
        if "-agent" in agent_id or agent_id.endswith("-agent"):
            return f"{agent_id}.local"
        return agent_id
    return None


def _detect_agent_action(prompt: str) -> str | None:
    lower = prompt.lower()
    agent_id = extract_agent_id(prompt)
    mentions_agent = bool(agent_id) or bool(re.search(r"\b(agent|agenta|deployment)\b", lower))
    if not mentions_agent:
        return None
    if re.search(r"\b(zdiagnozuj|diagnoza|diagnose|diagnosis)\b", lower):
        return "diagnose"
    if re.search(r"\b(napraw|repair\s+apply|apply\s+repair)\b", lower):
        return "repair"
    if re.search(r"\b(health|healthcheck|zdrow)\b", lower):
        return "health"
    if re.search(r"\b(log|logi)\b", lower):
        return "logs"
    if re.search(r"\b(runtime|stan\s+runtime)\b", lower):
        return "runtime"
    if re.search(r"\b(proces|process|pokaż|pokaz|show|view|status)\b", lower):
        return "process_view"
    if agent_id:
        return "process_view"
    return None


def agent_uri(agent_id: str, action: str) -> str:
    routes = {
        "process_view": f"view://process/agent/{agent_id}/latest",
        "health": f"health://agent/{agent_id}",
        "diagnose": f"repair://agent/{agent_id}/diagnose",
        "repair": f"repair://agent/{agent_id}/apply",
        "logs": f"log://hypervisor?grep={agent_id}",
        "runtime": f"runtime://agent/{agent_id}/state",
    }
    return routes.get(action, routes["process_view"])


def split_nl_commands(prompt: str) -> list[str]:
    """Split a pasted multi-line prompt into independent NL commands."""
    text = prompt.strip()
    if not text:
        return []
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    if len(lines) <= 1:
        return [text]
    return lines


def is_screenshot_schedule_prompt(prompt: str) -> bool:
    return bool(
        re.search(
            r"\b("
            r"rzut(?:y|ów|y\s+ekran)|"
            r"screenshot\w*|"
            r"zrzut\s+ekran|"
            r"monitor(?:uj|owanie)?\s+stron|"
            r"harmonogram\s+screenshot"
            r")\b",
            prompt,
            re.I,
        )
    )


def detect_intent(prompt: str) -> dict[str, Any]:
    text = prompt.strip()
    kind = _detect_kind(text)
    scenario = None if kind in {"agent", "agent_factory"} else try_scenario_intent(text, kind=kind)
    if scenario:
        return scenario
    if kind == "agent_factory":
        from urish.backends.agent_factory import infer_agent_name

        agent_id = infer_agent_name(text)
        return {
            "kind": "agent_factory",
            "subtype": "generate-agent",
            "profile": None,
            "agent_id": agent_id,
            "deployment_id": f"{agent_id}.local",
            "ecosystem_id": None,
            "dashboard_port": None,
        }
    if kind == "agent":
        action = _detect_agent_action(text) or "process_view"
        agent_id = extract_agent_id(text)
        return {
            "kind": "agent",
            "subtype": action,
            "profile": None,
            "agent_id": (
                agent_id.split(".")[0]
                if agent_id and agent_id.endswith(".local")
                else agent_id
            ),
            "deployment_id": agent_id,
            "ecosystem_id": None,
            "dashboard_port": None,
            "uri": agent_uri(agent_id, action) if agent_id else None,
        }
    if kind == "ecosystem" and wants_dashboard(text, "minimal"):
        return {
            "kind": "ecosystem",
            "subtype": "dashboard-agent",
            "profile": "dashboard-agent",
            "ecosystem_id": "hypervisor-dashboard",
            "agent_id": "hypervisor-dashboard",
            "deployment_id": "hypervisor-dashboard.local",
            "dashboard_port": 8788,
        }
    if kind == "ecosystem":
        from urigen.models import slugify

        if "pogod" in text.lower() or "weather" in text.lower():
            eco_id = "weather-demo"
        else:
            eco_id = slugify(text[:64], fallback="generated-ecosystem")
        return {
            "kind": "ecosystem",
            "subtype": "generic-ecosystem",
            "profile": "minimal",
            "ecosystem_id": eco_id,
            "agent_id": None,
            "deployment_id": None,
            "dashboard_port": None,
        }
    if kind == "workflow":
        return {"kind": "workflow", "subtype": None, "profile": None}
    if kind == "weather":
        from nl2uri.weather_forecast import is_weather_forecast_prompt, weather_forecast_uri

        if is_weather_forecast_prompt(text):
            return {
                "kind": "weather",
                "subtype": "forecast_html",
                "profile": None,
                "uri": weather_forecast_uri(text),
            }
        return {"kind": "weather", "subtype": "forecast", "profile": None}
    return {"kind": "domain", "subtype": None, "profile": None}


# Declarative kind detection.
# It reduces CC in detect_intent by turning long if-chain into pure predicates.
# Order matters (first match wins, matching original logic).
_KIND_DETECTORS: list[tuple[Callable[[str], bool], str]] = [
    (lambda p: bool(re.search(r"\b(ecosystem|ekosystem)\b", p, re.I)), "ecosystem"),
    (
        lambda p: bool(
            re.search(r"\b(stw[oó]rz|zbuduj|generuj)\b", p, re.I)
            and re.search(r"\b(web\s*ui|webui|dashboard|chat\s+markdown)\b", p, re.I)
            and re.search(r"\b(hypervisor\w*|system|api|proces\w*|process|agent\w*)\b", p, re.I)
        ),
        "ecosystem",
    ),
    (
        lambda p: bool(
            re.search(r"\b(stw[oó]rz|zbuduj|generuj)\b.*\b(agent|agenta)\b", p, re.I)
        ),
        "agent_factory",
    ),
    (
        lambda p: bool(
            re.search(r"\b(agent|agenta)\b", p, re.I)
            and re.search(r"\b(stw[oó]rz|zbuduj|generuj)\b", p, re.I)
        ),
        "agent_factory",
    ),
    (lambda p: bool(_detect_agent_action(p)), "agent"),
    (
        is_screenshot_schedule_prompt,
        "workflow",
    ),
    (lambda p: bool(try_scenario_intent(p)), "scenario"),  # special: returns the scenario's kind
    (lambda p: bool(re.search(r"\b(pogod\w*|weather|forecast|prognoz\w*)\b", p, re.I)), "weather"),
    (
        lambda p: bool(
            re.search(r"\b(flow|workflow|graf|health|chrome|localhost|napraw|repair)\b", p, re.I)
        ),
        "workflow",
    ),
]

def _detect_kind(prompt: str) -> str:
    text = prompt.strip()
    for predicate, kind in _KIND_DETECTORS:
        if predicate(text):
            if kind == "scenario":
                scenario = try_scenario_intent(text)
                return str(scenario["kind"]) if scenario else "domain"
            return kind
    return "domain"

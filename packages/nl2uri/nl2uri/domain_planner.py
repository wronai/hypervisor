from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
import yaml

DEFAULT_MODEL_URI = "llm://openrouter/qwen/qwen3-coder-next"


def _slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "generated-domain"


def _llm_uri_from_env() -> str:
    from uri3.config.llm_profiles import resolve_llm_profile

    profile_name = os.getenv("DEFAULT_LLM_PROFILE", "domain_planner")
    try:
        return resolve_llm_profile(profile_name, resolve_secrets=False).model_uri
    except Exception:
        raw = os.getenv("DOMAIN_PLANNER_LLM") or os.getenv("LLM_MODEL")
        if not raw:
            return DEFAULT_MODEL_URI
        if raw.startswith("llm://"):
            return raw
        if raw.startswith("openrouter/"):
            return raw.replace("openrouter/", "llm://openrouter/", 1)
        return f"llm://{raw}"


def _deterministic_weather_plan(prompt: str) -> dict[str, Any]:
    days = 14 if re.search(r"dwa\s*tygod|two\s*weeks|14", prompt, re.I) else 7
    domain_id = "weather_map"
    agent_id = "weather-map-agent"
    return {
        "domain": {"id": domain_id, "uri": "domain://weather-map", "name": "weather-map", "description": "Generate forecast weather maps as HTML URL artifacts."},
        "standards": {"uri_tree_schema": "schemas/uri_tree.schema.json", "data_contract": "protobuf", "agent_manifest": "a2a_agent_card", "resource_model": "mcp_resources"},
        "inputs": {
            "place": {"uri": "input://weather-map/place", "type": "string", "required": True},
            "days": {"uri": "input://weather-map/days", "type": "integer", "default": days},
            "forecast_model": {"uri": "input://weather-map/forecast-model", "type": "string", "default": "auto"},
        },
        "llm": {"planner": {"uri": _llm_uri_from_env(), "api_key_uri": "env://OPENROUTER_API_KEY"}},
        "commands": {
            "generate_weather_map": {
                "uri": "command://weather-map/generate",
                "name": "GenerateWeatherMap",
                "handler_uri": "python://domains.weather_map.handlers.generate_weather_map:handler",
                "input_schema_ref": "app.weather.v1.GenerateWeatherMapCommand",
                "emits": ["event://weather-map/WeatherMapGenerationRequested", "event://weather-map/WeatherMapGenerated"],
            }
        },
        "events": {
            "generation_requested": {"uri": "event://weather-map/WeatherMapGenerationRequested", "name": "WeatherMapGenerationRequested", "schema_ref": "app.weather.v1.WeatherMapGenerationRequested"},
            "generated": {"uri": "event://weather-map/WeatherMapGenerated", "name": "WeatherMapGenerated", "schema_ref": "app.weather.v1.WeatherMapGenerated"},
        },
        "resources": {
            "forecast_data": {"uri_template": "resource://weather/forecast/{place}/{days}", "schema_ref": "app.weather.v1.ForecastDataView", "renderer_ref": "json", "mime_type": "application/json"},
            "html_map": {"uri_template": "resource://weather/maps/{place}/forecast/{days}", "schema_ref": "app.weather.v1.WeatherMapHtmlView", "renderer_ref": "html", "mime_type": "text/html"},
        },
        "artifacts": {
            "html_file": {"uri_template": "artifact://weather-map/{place}/forecast/{days}/index.html", "mime_type": "text/html", "public_url_template": "http://localhost:8000/artifacts/weather-map/{place}/forecast/{days}/index.html"}
        },
        "agent": {
            "id": agent_id,
            "uri": f"agent://{agent_id}",
            "name": agent_id,
            "card_uri": f"a2a://{agent_id}/.well-known/agent-card.json",
            "capabilities": [
                {"name": "generate_weather_map", "type": "command", "uri": f"a2a://{agent_id}/skills/generate_weather_map"},
                {"name": "read_weather_map", "type": "resource_read", "uri": f"a2a://{agent_id}/skills/read_weather_map"},
            ],
        },
        "deployment": {"default": {"uri": "local://agents/generated/weather_map_agent"}},
        "mcp": {"resources_read": {"uri": f"mcp://{agent_id}/resources/read"}, "tools_call": {"uri": f"mcp://{agent_id}/tools/call"}},
        "dependencies": ["pypi://httpx", "pypi://jinja2", "pypi://pydantic"],
    }


def _generic_plan(prompt: str) -> dict[str, Any]:
    slug = _slug(prompt[:80])
    domain_id = slug.replace("-", "_")
    agent_id = f"{slug}-agent"
    return {
        "domain": {"id": domain_id, "uri": f"domain://{slug}", "name": slug, "description": prompt},
        "standards": {"uri_tree_schema": "schemas/uri_tree.schema.json", "data_contract": "protobuf", "agent_manifest": "a2a_agent_card", "resource_model": "mcp_resources"},
        "inputs": {"input": {"uri": f"input://{slug}/input", "type": "string", "required": True}},
        "commands": {"run": {"uri": f"command://{slug}/run", "name": "RunTask", "handler_uri": f"python://domains.{domain_id}.handlers.run:handler", "input_schema_ref": f"app.{domain_id}.v1.RunTaskCommand", "emits": [f"event://{slug}/TaskRequested", f"event://{slug}/TaskCompleted"]}},
        "events": {"requested": {"uri": f"event://{slug}/TaskRequested", "name": "TaskRequested", "schema_ref": f"app.{domain_id}.v1.TaskRequested"}, "completed": {"uri": f"event://{slug}/TaskCompleted", "name": "TaskCompleted", "schema_ref": f"app.{domain_id}.v1.TaskCompleted"}},
        "resources": {"result": {"uri_template": f"resource://{slug}/result/{{id}}", "schema_ref": f"app.{domain_id}.v1.TaskResultView", "renderer_ref": "json", "mime_type": "application/json"}},
        "artifacts": {},
        "agent": {"id": agent_id, "uri": f"agent://{agent_id}", "name": agent_id, "card_uri": f"a2a://{agent_id}/.well-known/agent-card.json", "capabilities": [{"name": "run", "type": "command", "uri": f"a2a://{agent_id}/skills/run"}]},
        "deployment": {"default": {"uri": f"local://agents/generated/{agent_id.replace('-', '_')}"}},
        "mcp": {"resources_read": {"uri": f"mcp://{agent_id}/resources/read"}},
        "dependencies": ["pypi://pydantic"],
    }


def _is_weather_prompt(prompt: str) -> bool:
    return bool(re.search(r"pogod|weather|forecast|map", prompt, re.I))


def _validate_tree_data(tree: dict[str, Any]) -> list[str]:
    from uri3.validators.uri_tree_validator import SCHEMA_PATH

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    from jsonschema import Draft202012Validator

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(tree), key=lambda item: item.path)
    return [f"{list(error.path)}: {error.message}" for error in errors]


def _is_structured_uri_tree(tree: dict[str, Any]) -> bool:
    if not isinstance(tree, dict):
        return False
    domain = tree.get("domain")
    if not isinstance(domain, dict) or not domain.get("id") or not domain.get("uri"):
        return False
    if not isinstance(tree.get("commands"), dict):
        return False
    if not isinstance(tree.get("resources"), dict):
        return False
    agent = tree.get("agent")
    if not isinstance(agent, dict) or not agent.get("id") or not agent.get("uri"):
        return False
    return True


def _normalize_llm_tree(prompt: str, candidate: dict[str, Any]) -> dict[str, Any]:
    if _is_weather_prompt(prompt):
        base = _deterministic_weather_plan(prompt)
        if not _is_structured_uri_tree(candidate):
            base["planner_warning"] = "LLM returned simplified URI Tree; deterministic weather template used."
            return base
        errors = _validate_tree_data(candidate)
        if errors:
            base["planner_warning"] = (
                "LLM URI Tree failed schema validation; deterministic weather template used. "
                + "; ".join(errors[:3])
            )
            return base
        if candidate.get("domain", {}).get("id") != "weather_map":
            base["planner_warning"] = "LLM changed weather domain id; deterministic weather template used."
            return base
        return candidate
    if not _is_structured_uri_tree(candidate):
        plan = _generic_plan(prompt)
        plan["planner_warning"] = "LLM returned simplified URI Tree; generic deterministic template used."
        return plan
    errors = _validate_tree_data(candidate)
    if errors:
        plan = _generic_plan(prompt)
        plan["planner_warning"] = (
            "LLM URI Tree failed schema validation; generic deterministic template used. "
            + "; ".join(errors[:3])
        )
        return plan
    return candidate


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return yaml.safe_load(text)


def _call_openrouter(prompt: str, *, profile_name: str | None = None) -> dict[str, Any]:
    from uri3.config.llm_profiles import resolve_llm_profile

    profile = resolve_llm_profile(profile_name or os.getenv("DEFAULT_LLM_PROFILE", "domain_planner"))
    if not profile.api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing")
    system = """You generate a strict JSON URI Tree for a contract-first agent hypervisor.
Return only JSON (no markdown).
Top-level keys MUST be objects, not arrays:
domain {id, uri, name, description}
inputs { ... }
commands { key: {uri, name, handler_uri, ...} }
events { ... }
resources { key: {uri_template, schema_ref, ...} }
artifacts { ... }
agent {id, uri, card_uri, capabilities: [...]}
deployment {default: {uri: ...}}
mcp { ... }
dependencies [pypi://...]
Never return commands/resources/agent as bare URI strings or YAML lists."""
    payload: dict[str, Any] = {
        "model": profile.model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "temperature": profile.temperature,
        "max_tokens": profile.max_tokens,
    }
    if profile.response_format == "json":
        payload["response_format"] = {"type": "json_object"}
    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{profile.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {profile.api_key}", "Content-Type": "application/json"},
            json=payload,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    return _extract_json(content)


def plan_from_prompt(prompt: str, use_llm: bool | None = None) -> dict[str, Any]:
    if use_llm is None:
        use_llm = os.getenv("NL2A_USE_LLM", "0") in {"1", "true", "TRUE", "yes"}
    if use_llm:
        try:
            llm_tree = _call_openrouter(prompt)
            if not isinstance(llm_tree, dict):
                raise ValueError("LLM planner did not return a JSON object")
            return _normalize_llm_tree(prompt, llm_tree)
        except Exception as exc:
            plan = _deterministic_weather_plan(prompt) if _is_weather_prompt(prompt) else _generic_plan(prompt)
            plan["planner_warning"] = f"LLM planner failed, deterministic fallback used: {exc}"
            return plan
    if _is_weather_prompt(prompt):
        return _deterministic_weather_plan(prompt)
    return _generic_plan(prompt)


plan_domain_from_prompt = plan_from_prompt

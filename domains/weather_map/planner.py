"""Weather domain-specific planner logic.

Extracted from generic nl2uri to externalize domain vocabulary (per architecture audit P1).
This keeps nl2uri planners generic; domain provides its recipes, prompts, constants.
"""

import re
from typing import Any


def is_weather_prompt(prompt: str) -> bool:
    return bool(re.search(r"pogod|weather|forecast|map", prompt, re.I))


def deterministic_weather_plan(prompt: str) -> dict[str, Any]:
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
        "llm": {"planner": {"uri": "llm://openrouter/qwen/qwen3-coder-next", "api_key_uri": "env://OPENROUTER_API_KEY"}},
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

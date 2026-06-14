from __future__ import annotations

from pathlib import Path

CAPABILITY_SOURCES = {
    "weather.forecast.html": "examples/20_touri_capabilities/weather_forecast.uri.capability.yaml",
    "workflow.weather.flow": (
        "examples/20_touri_capabilities/weather_flow_dry_run.uri.capability.yaml"
    ),
    "workflow.check_health.graph": (
        "examples/20_touri_capabilities/check_health_graph.uri.capability.yaml"
    ),
    "stt.mock.transcribe": "examples/21_touri_voice/stt_mock.uri.capability.yaml",
    "tts.mock.speak": "examples/21_touri_voice/tts_mock.uri.capability.yaml",
    "voice.command.from_text": "examples/21_touri_voice/voice_command.uri.capability.yaml",
}

CAPABILITY_SAMPLE_URIS = {
    "weather.forecast.html": "weather://forecast/Gdansk/14/html",
    "workflow.weather.flow": "workflow://flow/weather/dry-run",
    "workflow.check_health.graph": "workflow://graph/check-agent-health/dry-run",
    "stt.mock.transcribe": "stt://mock/transcribe",
    "tts.mock.speak": "tts://mock/speak",
    "voice.command.from_text": "voice://command/from-text",
}

FLOW_SOURCES = {
    "weather-health": "examples/15_compact_uri_flow/weather.uri.flow.yaml",
}

AGENT_CONTRACTS = {
    "weather-map-agent": "contracts/agents/weather_map_agent.yaml",
}

DOMAIN_FILES = {
    "weather_map": [
        "domains/weather_map/domain.yaml",
        "domains/weather_map/uri_tree.yaml",
    ],
}

PROFILE_INCLUDES = {
    "minimal": ["contracts", "capabilities", "flows", "tests"],
    "agent": ["contracts", "capabilities", "flows", "deployments", "tests"],
    "voice": [
        "contracts",
        "capabilities",
        "flows",
        "deployments",
        "markpact",
        "tests",
        "voice",
    ],
    "operator": ["contracts", "capabilities", "flows", "deployments", "tests", "operator"],
    "provider": ["contracts", "capabilities", "flows", "tests"],
    "full": [
        "contracts",
        "capabilities",
        "flows",
        "deployments",
        "markpact",
        "tests",
        "doctor",
        "replay",
        "voice",
        "operator",
    ],
}

DEFAULT_ARTIFACTS = [
    "ecosystem.yaml",
    "domain_pack",
    "agent_contract",
    "touri_capabilities",
    "uri_flows",
    "deployment_config",
    "markpact_readme",
    "test_plan",
]


def repo_path(root: Path, relative: str) -> Path:
    return root / relative

from __future__ import annotations

from typing import Any

from urigen.artifacts import DEFAULT_ARTIFACTS, PROFILE_INCLUDES
from urigen.models import normalize_profile, slugify, wants_operator, wants_voice


def plan_ecosystem(
    prompt: str,
    *,
    profile: str = "minimal",
    ecosystem_id: str | None = None,
) -> dict[str, Any]:
    """Build a side-effect-free ecosystem proposal from a prompt."""
    selected_profile = normalize_profile(profile)
    eco_id = ecosystem_id or _default_ecosystem_id(prompt, selected_profile)
    capabilities = [
        "weather.forecast.html",
        "workflow.weather.flow",
        "workflow.check_health.graph",
    ]
    flows = ["weather-health"]
    if wants_voice(prompt, selected_profile):
        capabilities.extend(["stt.mock.transcribe", "tts.mock.speak", "voice.command.from_text"])
        flows.append("voice-command-health")

    return {
        "version": 1,
        "proposal": {
            "id": eco_id,
            "source_prompt": prompt,
            "kind": "ecosystem",
            "profile": selected_profile,
        },
        "intent": {
            "domains": ["weather_map"],
            "agents": ["weather-map-agent"],
            "capabilities": capabilities,
            "flows": flows,
            "deployments": ["weather-map-agent.local"],
            "operator": wants_operator(prompt, selected_profile),
            "voice": wants_voice(prompt, selected_profile),
        },
        "profile": {
            "name": selected_profile,
            "include": PROFILE_INCLUDES[selected_profile],
        },
        "policy": {
            "requires_approval": True,
            "side_effects": ["generate_files", "create_deployment_config"],
            "execution_allowed": False,
        },
        "artifacts_to_generate": list(DEFAULT_ARTIFACTS),
    }


def _default_ecosystem_id(prompt: str, profile: str) -> str:
    if "pogod" in prompt.lower() or "weather" in prompt.lower():
        base = "weather-voice-demo" if profile in {"voice", "full"} else "weather-demo"
        return base
    return slugify(prompt[:64], fallback="generated-ecosystem")

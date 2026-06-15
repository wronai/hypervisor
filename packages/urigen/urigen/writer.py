from __future__ import annotations

from pathlib import Path
from typing import Any

from urigen.io import dump_yaml


def render_readme(ecosystem: dict[str, Any], embedded: dict[str, str]) -> str:
    eco = ecosystem["ecosystem"]
    lines = [
        f"# {eco['id']}",
        "",
        eco.get("description") or "Generated URI ecosystem.",
        "",
        "## Ecosystem",
        "",
        "```yaml",
        dump_yaml(ecosystem).rstrip(),
        "```",
    ]
    for name, content in embedded.items():
        fence_type = "capability" if name.endswith(".uri.capability.yaml") else "flow"
        lines.extend(
            [
                "",
                f"```markpact:{fence_type} {Path(name).stem}",
                content.rstrip(),
                "```",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def deployment_fragment(*, deployments: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if deployments:
        return {"deployments": deployments}
    return {
        "deployments": [
            {
                "id": "weather-map-agent.local",
                "agent_ref": "agent://weather-map-agent",
                "target_uri": "local://agents/generated/weather_map_agent",
                "health_uri": "http://localhost:8101/health",
                "if_running": "reuse",
            }
        ]
    }


def dashboard_deployment_fragment() -> dict[str, Any]:
    return deployment_fragment(
        deployments=[
            {
                "id": "hypervisor-dashboard.local",
                "agent_ref": "agent://hypervisor-dashboard",
                "target_uri": "local://agents/system/hypervisor_dashboard",
                "status": "planned",
                "health_uri": "http://localhost:8788/health",
                "card_uri": "http://localhost:8788/.well-known/agent-card.json",
                "if_running": "reuse",
            }
        ]
    )


def voice_flow() -> dict[str, Any]:
    return {
        "flow": {
            "id": "voice-command-health",
            "description": (
                "Plan a voice command and generate a weather artifact through runtime-safe URIs."
            ),
        },
        "do": [
            {
                "uri": "python://uri2voice.voice_command:plan_voice_command",
                "with": {"text": "wygeneruj agenta pogodowego i sprawdz health"},
            },
            "python://touri_examples.weather:handler",
        ],
    }


def test_plan(ecosystem_id: str) -> dict[str, Any]:
    return {
        "version": 1,
        "test_plan": {
            "id": f"{ecosystem_id}.test-plan",
            "checks": [
                {"id": "capabilities", "type": "touri.validate"},
                {"id": "flows", "type": "uri2flow.validate"},
                {"id": "explain", "type": "uri3.explain"},
                {"id": "doctor", "type": "uri3.doctor"},
            ],
        },
    }

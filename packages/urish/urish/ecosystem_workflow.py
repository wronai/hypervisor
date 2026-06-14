from __future__ import annotations

from typing import Any

from urish.intent import DASHBOARD_PLANNED_URIS

SHELL_CMD = "urish"


def _quote(text: str) -> str:
    import json

    if " " in text or '"' in text:
        return json.dumps(text, ensure_ascii=False)
    return text


def proposal_path(ecosystem_id: str) -> str:
    return f"output/proposals/{ecosystem_id}.ecosystem.proposal.yaml"


def ecosystem_dir(ecosystem_id: str) -> str:
    return f"output/ecosystems/{ecosystem_id}"


def ecosystem_file(ecosystem_id: str) -> str:
    return f"{ecosystem_dir(ecosystem_id)}/ecosystem.yaml"


def build_ecosystem_next_steps(
    *,
    prompt: str,
    intent: dict[str, Any],
) -> list[str]:
    eco_id = str(intent.get("ecosystem_id") or "generated-ecosystem")
    profile = intent.get("profile") or "minimal"
    proposal = proposal_path(eco_id)
    eco_path = ecosystem_file(eco_id)
    steps = [
        f"{SHELL_CMD} ecosystem plan {_quote(prompt)} --profile {profile} --out {proposal}",
        f"{SHELL_CMD} ecosystem generate {proposal} --out {ecosystem_dir(eco_id)}",
        f"{SHELL_CMD} ecosystem verify {eco_path}",
        f"{SHELL_CMD} ecosystem apply {eco_path} --plan",
        f"{SHELL_CMD} ecosystem apply {eco_path} --approve",
    ]
    if intent.get("subtype") == "dashboard-agent":
        deployment_id = intent.get("deployment_id") or f"{eco_id}.local"
        port = intent.get("dashboard_port") or 8788
        steps.extend(
            [
                f"{SHELL_CMD} agent run {deployment_id} --wait-healthy --approve",
                (
                    f"{SHELL_CMD} call browser://chrome/page/open "
                    f'--payload \'{{"url":"http://localhost:{port}/ui"}}\' --approve'
                ),
            ]
        )
    return steps


def build_planned_uris(intent: dict[str, Any], *, proposal_uri: str, ecosystem_uri: str) -> list[str]:
    uris = [proposal_uri, ecosystem_uri]
    if intent.get("subtype") == "dashboard-agent":
        uris.extend(DASHBOARD_PLANNED_URIS)
    return uris


def build_planned_uris_display(planned_uris: list[str]) -> list[str]:
    """Human-facing subset: skip meta proposal/ecosystem URIs when dashboard URIs exist."""
    skip_prefixes = ("proposal://", "ecosystem://")
    filtered = [uri for uri in planned_uris if not uri.startswith(skip_prefixes)]
    return filtered or list(planned_uris)

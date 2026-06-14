from __future__ import annotations

from typing import Any

from urish.ecosystem_workflow import (
    build_ecosystem_next_steps,
    build_planned_uris,
    ecosystem_dir,
    proposal_path,
)
from urish.intent import agent_uri, detect_intent


def _ask_ecosystem_plan(text: str, intent: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    from urigen.proposal import plan_ecosystem

    profile = intent.get("profile") or "minimal"
    eco_id = intent.get("ecosystem_id")
    generated = plan_ecosystem(text, profile=profile, ecosystem_id=eco_id)
    eco_id = generated.get("proposal", {}).get("id") or eco_id or "generated-ecosystem"
    uris = build_planned_uris(
        intent,
        proposal_uri=f"proposal://ecosystem/{eco_id}",
        ecosystem_uri=f"ecosystem://{eco_id}",
    )
    next_steps = build_ecosystem_next_steps(prompt=text, intent={**intent, "ecosystem_id": eco_id})
    generated.setdefault("intent_meta", intent)
    generated["proposal_path"] = proposal_path(eco_id)
    generated["ecosystem_dir"] = ecosystem_dir(eco_id)
    return generated, uris, next_steps


def _ask_agent_plan(intent: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    action = intent.get("subtype") or "process_view"
    agent_id = intent.get("deployment_id")
    if not agent_id:
        return (
            {"error": "missing agent deployment id in prompt"},
            [],
            ["Podaj deployment id, np. weather-map-agent.local"],
        )
    uri = agent_uri(agent_id, action)
    generated = {"agent_id": agent_id, "action": action, "uri": uri}
    next_steps = [
        f"hypervisor inspect-agent {agent_id}",
        f"uri call {uri}",
    ]
    if action == "diagnose":
        next_steps.append(f"hypervisor repair apply {agent_id} --dry-run")
    elif action == "process_view":
        next_steps.append(f"health://agent/{agent_id}")
    return generated, [uri], next_steps


def _ask_workflow_plan(text: str, *, use_llm: bool) -> tuple[dict[str, Any], list[str], list[str]]:
    from nl2uri.flow_planner import plan_flow

    generated = plan_flow(text, use_llm=use_llm)
    flow_id = (generated.get("flow") or {}).get("id") or "generated-flow"
    uris = [f"workflow://graph/{flow_id}/dry-run"]
    next_steps = [
        f"uri run workflow://graph/{flow_id}/dry-run",
        f"uri run workflow://graph/{flow_id} --approve",
    ]
    return generated, uris, next_steps


def _ask_domain_plan(text: str, *, use_llm: bool) -> tuple[dict[str, Any], list[str], list[str]]:
    from nl2uri.domain_planner import plan_from_prompt

    generated = plan_from_prompt(text, use_llm=use_llm)
    domain_id = (generated.get("domain") or {}).get("id") or "generated-domain"
    uris = [f"domain://{domain_id}"]
    next_steps = [f"uri explain domain://{domain_id}"]
    return generated, uris, next_steps


_ASK_PLANNERS: dict[str, Any] = {
    "ecosystem": lambda text, intent, use_llm: _ask_ecosystem_plan(text, intent),
    "agent": lambda text, intent, use_llm: _ask_agent_plan(intent),
    "workflow": lambda text, intent, use_llm: _ask_workflow_plan(text, use_llm=use_llm),
    "domain": lambda text, intent, use_llm: _ask_domain_plan(text, use_llm=use_llm),
}


def _build_ask_envelope(
    *,
    text: str,
    intent: dict[str, Any],
    kind: str,
    generated: dict[str, Any],
    uris: list[str],
    next_steps: list[str],
    dry_run: bool,
) -> dict[str, Any]:
    return {
        "ok": True,
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded",
        "result_type": "ask",
        "data": {
            "prompt": text,
            "detected_kind": kind,
            "detected_subtype": intent.get("subtype"),
            "profile": intent.get("profile"),
            "agent_id": intent.get("agent_id"),
            "deployment_id": intent.get("deployment_id"),
            "ecosystem_id": intent.get("ecosystem_id"),
            "generated": generated,
            "uris": uris,
            "planned_uris": uris,
            "next_steps": next_steps,
            "dry_run": dry_run,
        },
        "meta": {"runtime": "urish", "transport": "nl2uri", "target": uris[0] if uris else ""},
    }


def ask_prompt(
    prompt: str,
    *,
    dry_run: bool = True,
    use_llm: bool = False,
) -> dict[str, Any]:
    text = prompt.strip()
    intent = detect_intent(text)
    kind = intent["kind"]
    planner = _ASK_PLANNERS.get(kind, _ASK_PLANNERS["domain"])
    generated, uris, next_steps = planner(text, intent, use_llm)
    return _build_ask_envelope(
        text=text,
        intent=intent,
        kind=kind,
        generated=generated,
        uris=uris,
        next_steps=next_steps,
        dry_run=dry_run,
    )

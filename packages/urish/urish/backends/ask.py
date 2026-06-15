from __future__ import annotations

from typing import Any
from urllib.parse import quote

from urish.ecosystem_workflow import (
    build_ecosystem_next_steps,
    build_planned_uris,
    ecosystem_dir,
    proposal_path,
)
from urish.intent import agent_uri, detect_intent, split_nl_commands
from urish.scenario_registry import next_steps_for_intent


def _ask_ecosystem_plan(
    text: str,
    intent: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str]]:
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
            ["Podaj deployment id, np. <agent-id> (zobacz urish agent status lub domains/*)"],
        )
    uri = agent_uri(agent_id, action)
    generated = {"agent_id": agent_id, "action": action, "uri": uri}
    next_steps = [
        f"hypervisor inspect-agent {agent_id}",
        f"uri call {uri}",
    ]
    if action == "diagnose":
        next_steps.append(f"uri repair apply {agent_id} --dry-run")
    elif action == "process_view":
        next_steps.append(f"health://agent/{agent_id}")
    return generated, [uri], next_steps


def _ask_agent_factory_plan(
    text: str,
    intent: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str]]:
    from urish.backends.agent_factory import build_agent_contract, generate_agent_from_prompt, infer_agent_name

    agent_id = infer_agent_name(text, intent.get("agent_id"))
    plan = generate_agent_from_prompt(text, name=agent_id, dry_run=True)
    planned = plan["planned"]
    deployment_id = planned["deployment_id"]
    generate_uri = f"agent-factory://generate/{agent_id}?prompt={quote(text, safe='')}"
    run_uri = f"hypervisor://agent/{deployment_id}/run"
    health_uri = f"health://agent/{deployment_id}"
    view_uri = f"view://process/agent/{deployment_id}/latest"
    generated = {
        "agent_id": agent_id,
        "deployment_id": deployment_id,
        "contract": build_agent_contract(text, name=agent_id),
        "resource_uris": [
            f"agent://{agent_id}",
            f"deployment://{deployment_id}",
            health_uri,
            view_uri,
        ],
    }
    uris = [
        generate_uri,
        run_uri,
    ]
    ssh_deployment_id = planned.get("ssh_deployment_id")
    if ssh_deployment_id:
        generated["ssh_deployment_id"] = ssh_deployment_id
        generated["ssh_target_uri"] = planned.get("ssh_target_uri")
        generated["resource_uris"].append(f"deployment://{ssh_deployment_id}")
        uris.append(f"hypervisor://agent/{ssh_deployment_id}/deploy")
    next_steps = list(plan["next_steps"])
    return generated, uris, next_steps


def _ask_scenario_plan(intent: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    subtype = intent.get("subtype") or "scenario"
    agent_id = intent.get("deployment_id")
    uris = list(intent.get("planned_uris") or [])
    generated = {
        "scenario_subtype": subtype,
        "scenario_id": intent.get("scenario_id"),
        "registry_id": intent.get("registry_id"),
        "registry_source": intent.get("registry_source"),
        "markpact_readme": intent.get("markpact_readme"),
        "agent_id": agent_id,
        "human_in_the_loop": bool(intent.get("human_in_the_loop", False)),
        "artifacts": intent.get("artifacts") or {},
    }
    return generated, uris, next_steps_for_intent(intent)


def _ask_workflow_plan(text: str, *, use_llm: bool) -> tuple[dict[str, Any], list[str], list[str]]:
    from nl2uri.flow_planner import plan_flow
    from nl2uri.graph_planner import WEBSITE_SCREENSHOT_SCHEDULE_ID, plan_screenshot_schedule

    from urish.intent import is_screenshot_schedule_prompt

    if is_screenshot_schedule_prompt(text):
        generated = plan_screenshot_schedule(text, use_llm=use_llm)
        flow_id = WEBSITE_SCREENSHOT_SCHEDULE_ID
        next_steps = [
            f"uri run workflow://graph/{flow_id}/dry-run",
            f"uri run workflow://graph/{flow_id} --approve --adapter playwright",
            "bash scripts/www/install-cron.sh --status  # host schedule for recurring runs",
        ]
    else:
        generated = plan_flow(text, use_llm=use_llm)
        flow_id = (generated.get("flow") or {}).get("id") or "generated-flow"
        next_steps = [
            f"uri run workflow://graph/{flow_id}/dry-run",
            f"uri run workflow://graph/{flow_id} --approve",
        ]
    uris = [f"workflow://graph/{flow_id}/dry-run"]
    return generated, uris, next_steps


def _ask_domain_plan(text: str, *, use_llm: bool) -> tuple[dict[str, Any], list[str], list[str]]:
    from nl2uri.domain_planner import plan_from_prompt

    generated = plan_from_prompt(text, use_llm=use_llm)
    domain = generated.get("domain") or {}
    domain_id = domain.get("id") or "generated-domain"
    uri = domain.get("uri") or f"domain://{domain_id}"
    uris = [uri]
    next_steps = [f"uri explain {uri}"]
    return generated, uris, next_steps


def _ask_weather_plan(text: str, *, use_llm: bool) -> tuple[dict[str, Any], list[str], list[str]]:
    from nl2uri.weather_forecast import plan_weather_forecast

    generated = plan_weather_forecast(text)
    uri = generated["uri"]
    next_steps = [
        f"uri call {uri}",
        f"uri explain {uri}",
    ]
    return generated, [uri], next_steps


_ASK_PLANNERS: dict[str, Any] = {
    "agent_factory": lambda text, intent, use_llm: _ask_agent_factory_plan(text, intent),
    "ecosystem": lambda text, intent, use_llm: _ask_ecosystem_plan(text, intent),
    "agent": lambda text, intent, use_llm: _ask_agent_plan(intent),
    "workflow": lambda text, intent, use_llm: _ask_workflow_plan(text, use_llm=use_llm),
    "weather": lambda text, intent, use_llm: _ask_weather_plan(text, use_llm=use_llm),
    "domain": lambda text, intent, use_llm: _ask_domain_plan(text, use_llm=use_llm),
}


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _plan_single(text: str, *, use_llm: bool) -> dict[str, Any]:
    intent = detect_intent(text)
    kind = intent["kind"]
    if intent.get("registry_id"):
        generated, uris, next_steps = _ask_scenario_plan(intent)
    else:
        planner = _ASK_PLANNERS.get(kind, _ASK_PLANNERS["domain"])
        generated, uris, next_steps = planner(text, intent, use_llm)
    return {
        "prompt": text,
        "detected_kind": kind,
        "detected_subtype": intent.get("subtype"),
        "scenario_id": intent.get("scenario_id"),
        "profile": intent.get("profile"),
        "agent_id": intent.get("agent_id"),
        "deployment_id": intent.get("deployment_id"),
        "ecosystem_id": intent.get("ecosystem_id"),
        "generated": generated,
        "uris": uris,
        "planned_uris": uris,
        "next_steps": next_steps,
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
            "scenario_id": intent.get("scenario_id") or generated.get("scenario_id"),
            "profile": intent.get("profile"),
            "agent_id": intent.get("agent_id") or generated.get("agent_id"),
            "deployment_id": intent.get("deployment_id") or generated.get("deployment_id"),
            "ecosystem_id": intent.get("ecosystem_id"),
            "generated": generated,
            "uris": uris,
            "planned_uris": uris,
            "next_steps": next_steps,
            "dry_run": dry_run,
            "batch": False,
            "actions": [],
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
    lines = split_nl_commands(text)
    if len(lines) <= 1:
        intent = detect_intent(text)
        kind = intent["kind"]
        if intent.get("registry_id"):
            generated, uris, next_steps = _ask_scenario_plan(intent)
        else:
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

    actions = [_plan_single(line, use_llm=use_llm) for line in lines]
    all_uris = _dedupe([uri for action in actions for uri in action["planned_uris"]])
    all_steps = _dedupe([step for action in actions for step in action["next_steps"]])
    envelope = _build_ask_envelope(
        text=text,
        intent={"kind": "batch", "subtype": "multi", "profile": None},
        kind="batch",
        generated={"action_count": len(actions), "lines": lines},
        uris=all_uris,
        next_steps=all_steps,
        dry_run=dry_run,
    )
    data = envelope["data"]
    data["batch"] = True
    data["actions"] = actions
    data["detected_subtype"] = "multi"
    return envelope

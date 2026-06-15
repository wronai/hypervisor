from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from hypervisor_dashboard_agent.chat_format import format_uri_result_markdown
from hypervisor_dashboard_agent.policy import decision_for_uri
from hypervisor_dashboard_agent.uri_client import call_system_uri, uri_implies_dry_run

_AGENT_URI_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"health://agent/([^/]+)", re.I),
    re.compile(r"repair://agent/([^/]+)", re.I),
    re.compile(r"view://process/agent/([^/]+)", re.I),
    re.compile(r"runtime://agent/([^/]+)", re.I),
)


def agent_id_from_uri(uri: str) -> str | None:
    for pattern in _AGENT_URI_PATTERNS:
        match = pattern.search(uri)
        if match:
            return match.group(1)
    return None


@dataclass(frozen=True)
class PlanRunOptions:
    planned_uris: list[str]
    approved: bool = False
    dry_run: bool = True
    policy: str = "dev"
    stop_on_error: bool = True
    auto_repair: bool = True
    retry_after_repair: bool = True


def _execute_uri(
    uri: str,
    *,
    approved: bool,
    dry_run: bool,
    policy: str,
) -> dict[str, Any]:
    effective_dry_run = dry_run or uri_implies_dry_run(uri)
    decision = decision_for_uri(uri, approved=approved, dry_run=effective_dry_run, policy=policy)
    if not decision.allowed:
        return {
            "ok": False,
            "uri": uri,
            "result_type": "policy_blocked",
            "error": decision.reason or "blocked by policy",
            "requires_approval": decision.requires_approval,
        }
    try:
        result = call_system_uri(
            uri,
            approved=approved,
            dry_run=decision.force_dry_run or effective_dry_run,
        )
    except ValueError as exc:
        result = {
            "ok": False,
            "result_type": "error",
            "uri": uri,
            "error": str(exc),
        }
    except Exception as exc:  # pragma: no cover
        result = {
            "ok": False,
            "result_type": "error",
            "uri": uri,
            "error": str(exc),
        }
    result.setdefault("uri", uri)
    result["message_markdown"] = format_uri_result_markdown(result)
    return result


def _attempt_auto_repair(
    agent_id: str,
    *,
    approved: bool,
    dry_run: bool,
    policy: str,
) -> dict[str, Any]:
    repair_uri = f"repair://agent/{agent_id}/auto"
    result = _execute_uri(
        repair_uri,
        approved=approved and not dry_run,
        dry_run=dry_run,
        policy=policy,
    )
    result["repair_for_agent"] = agent_id
    return result


def run_planned_uris(options: PlanRunOptions) -> dict[str, Any]:
    """Execute planned URIs with optional bounded auto-repair and retry."""
    results: list[dict[str, Any]] = []
    repairs: list[dict[str, Any]] = []

    for uri in options.planned_uris:
        result = _execute_uri(
            uri,
            approved=options.approved,
            dry_run=options.dry_run,
            policy=options.policy,
        )
        if (
            not result.get("ok")
            and options.auto_repair
            and (agent_id := agent_id_from_uri(uri))
        ):
            repair = _attempt_auto_repair(
                agent_id,
                approved=options.approved,
                dry_run=options.dry_run,
                policy=options.policy,
            )
            repairs.append(repair)
            result["auto_repair"] = repair
            if options.retry_after_repair and repair.get("ok"):
                retry = _execute_uri(
                    uri,
                    approved=options.approved,
                    dry_run=options.dry_run,
                    policy=options.policy,
                )
                result["retry"] = retry
                if retry.get("ok"):
                    result = {
                        **retry,
                        "auto_repair": result.get("auto_repair"),
                        "retry": retry,
                    }
        results.append(result)
        if options.stop_on_error and not result.get("ok"):
            break

    ok = all(item.get("ok") for item in results) if results else False
    return {
        "ok": ok,
        "result_type": "plan_run",
        "count": len(results),
        "results": results,
        "repairs": repairs,
        "auto_repair": options.auto_repair,
        "message_markdown": format_plan_run_markdown(results, repairs=repairs),
    }


def format_plan_run_markdown(
    results: list[dict[str, Any]],
    *,
    repairs: list[dict[str, Any]] | None = None,
) -> str:
    lines = [f"## Plan run ({len(results)} steps)", ""]
    for index, item in enumerate(results, start=1):
        status = "ok" if item.get("ok") else "failed"
        lines.append(f"{index}. `{item.get('uri', '—')}` → **{status}**")
        repair = item.get("auto_repair")
        if isinstance(repair, dict):
            repair_status = "ok" if repair.get("ok") else "failed"
            agent_id = repair.get("repair_for_agent") or "agent"
            lines.append(f"   - auto-repair `{agent_id}` → **{repair_status}**")
        retry = item.get("retry")
        if isinstance(retry, dict):
            retry_status = "ok" if retry.get("ok") else "failed"
            lines.append(f"   - retry → **{retry_status}**")
    if repairs:
        lines.extend(["", f"_Auto-repair attempts: {len(repairs)}_"])
    return "\n".join(lines)

from __future__ import annotations

from typing import Any


def _header_lines(data: dict[str, Any]) -> list[str]:
    subtype = data.get("detected_subtype")
    kind = data.get("detected_kind") or "unknown"
    if subtype:
        return [f"## Detected: `{subtype}`", f"Type: **{kind}**"]
    return [f"## Detected: **{kind}**"]


def _identity_lines(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if data.get("ecosystem_id"):
        lines.append(f"\n**Name:** `{data['ecosystem_id']}`")
    if data.get("profile"):
        lines.append(f"\n**Profile:** `{data['profile']}`")
    if data.get("agent_id"):
        lines.append(f"\n**Agent:** `agent://{data['agent_id']}`")
    if data.get("deployment_id"):
        lines.append(f"\n**Deployment:** `{data['deployment_id']}`")
    generated = data.get("generated") or {}
    if generated.get("proposal_path"):
        lines.append(f"\n**Proposal:** `{generated['proposal_path']}`")
    return lines


def _planned_lines(data: dict[str, Any]) -> list[str]:
    planned = data.get("planned_uris") or data.get("uris") or []
    display_planned = _display_planned(planned, data.get("detected_subtype"))
    if not display_planned:
        return []
    lines = ["\n### Planned URI"]
    lines.extend(f"- `{uri}`" for uri in display_planned)
    return lines


def _next_step_lines(data: dict[str, Any]) -> list[str]:
    next_steps = data.get("next_steps") or []
    if not next_steps:
        return ["\n_No follow-up steps detected — try a more specific prompt._"]
    lines = [
        "\n### Next steps",
        "Use **Run plan (dry-run)** after ask, or copy a command below.",
    ]
    lines.extend(f"\n```bash\n{step}\n```" for step in next_steps)
    return lines


def _format_action_block(index: int, action: dict[str, Any]) -> list[str]:
    subtype = action.get("detected_subtype")
    kind = action.get("detected_kind") or "unknown"
    header = f"### {index}. "
    if subtype:
        header += f"`{subtype}` · **{kind}**"
    else:
        header += f"**{kind}**"
    lines = [header, f"\n> {action.get('prompt', '')}"]
    if action.get("deployment_id"):
        lines.append(f"\n**Deployment:** `{action['deployment_id']}`")
    elif action.get("agent_id"):
        lines.append(f"\n**Agent:** `agent://{action['agent_id']}`")
    planned = action.get("planned_uris") or action.get("uris") or []
    display_planned = _display_planned(planned, action.get("detected_subtype"))
    if display_planned:
        lines.append("\n#### Planned URI")
        lines.extend(f"- `{uri}`" for uri in display_planned)
    next_steps = action.get("next_steps") or []
    if next_steps:
        lines.append("\n#### Next steps")
        lines.extend(f"\n```bash\n{step}\n```" for step in next_steps[:3])
    return lines


def format_ask_markdown(data: dict[str, Any]) -> str:
    """Turn urish ask payload into chat-friendly markdown."""
    actions = data.get("actions") or []
    if data.get("batch") and actions:
        lines = [f"## Detected {len(actions)} commands", ""]
        for index, action in enumerate(actions, start=1):
            lines.extend(_format_action_block(index, action))
            lines.append("")
        lines.append(
            "_Each line is planned independently. Run URIs one at a time "
            "or use quick prompts for single commands._"
        )
        return "\n".join(lines).strip()

    lines = _header_lines(data)
    lines.extend(_identity_lines(data))
    lines.extend(_planned_lines(data))
    lines.extend(_next_step_lines(data))
    return "\n".join(lines).strip()


def _uri_result_status_label(result: dict[str, Any]) -> str:
    result_type = result.get("result_type") or "result"
    if result_type == "dry_run" or result.get("status") == "preview":
        return "preview"
    if result_type == "diagnosis":
        return "diagnosis"
    ok = bool(result.get("ok"))
    return str(result.get("service_result_status") or ("succeeded" if ok else "failed"))


def _uri_result_header_lines(result: dict[str, Any]) -> list[str]:
    result_type = result.get("result_type") or "result"
    lines = [
        f"## URI: {_uri_result_status_label(result)}",
        f"Type: `{result_type}` · workflow: `{result.get('workflow_status', '—')}`",
    ]
    if title := result.get("title"):
        lines.append(f"Title: **{title}**")
    if view_uri := result.get("view_uri"):
        lines.append(f"View: `{view_uri}`")
    return lines


def _diagnosis_detail_lines(result: dict[str, Any]) -> list[str]:
    if result.get("result_type") != "diagnosis" or not result.get("classification"):
        return []
    classification = result["classification"]
    lines: list[str] = []
    families = classification.get("family") or []
    repairs = classification.get("safe_repairs") or []
    if families:
        lines.append(f"\n**Classification:** `{', '.join(families)}`")
    if repairs:
        lines.append(f"\n**Suggested repairs:** `{', '.join(repairs[:4])}`")
    return lines


def _uri_result_body_lines(body: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if body.get("error"):
        lines.append(f"\n**Error:** {body['error']}")
    elif body.get("user_summary"):
        lines.append(f"\n{body['user_summary']}")
    lines.extend(_runtime_result_lines(body))
    lines.extend(_log_entry_preview_lines(body))
    hint = _next_step_hint(body)
    if hint:
        lines.append("\n### Next step")
        lines.append(hint)
    return lines


def _envelope_json_block(result: dict[str, Any]) -> list[str]:
    import json

    return [
        "\n<details><summary>Envelope JSON</summary>\n",
        "```json",
        json.dumps(result, indent=2, ensure_ascii=False)[:4000],
        "```\n</details>",
    ]


def format_uri_result_markdown(
    result: dict[str, Any],
    *,
    include_envelope: bool = True,
) -> str:
    """Compact markdown summary for URI call / execution envelopes."""
    if result.get("presentation_markdown"):
        lines = [result["presentation_markdown"]]
        if include_envelope:
            lines.extend(_envelope_json_block(result))
        return "\n".join(lines)

    lines = _uri_result_header_lines(result)
    if result.get("content_type") == "text/html" and result.get("html"):
        lines.append("\n### Rendered view")
        lines.append("_HTML preview is shown below in chat._")
    lines.extend(_diagnosis_detail_lines(result))
    if result.get("policy_blocked"):
        lines.append("\n> **Policy blocked** — use `--approve` in CLI or enable approve in the UI.")
    data = result.get("data")
    body = data if isinstance(data, dict) else result
    if isinstance(body, dict):
        lines.extend(_uri_result_body_lines(body))
    if include_envelope:
        lines.extend(_envelope_json_block(result))
    return "\n".join(lines)


def format_uri_result_summary(result: dict[str, Any]) -> str:
    """Terminal-friendly summary without the JSON envelope block."""
    return format_uri_result_markdown(result, include_envelope=False)


def _next_step_hint(body: dict[str, Any]) -> str | None:
    payload = _payload_data(body)
    agent_id = payload.get("agent_id") or body.get("agent_id") or body.get("id")
    incident_codes = set(payload.get("incident_codes") or [])
    for item in payload.get("incidents") or body.get("incidents") or []:
        if isinstance(item, dict) and item.get("code"):
            incident_codes.add(str(item["code"]))
    recommended = payload.get("recommended_action") or body.get("recommended_action")
    if not agent_id:
        return None
    if "RUNTIME_STATE_STALE" in incident_codes or recommended == "restart":
        return (
            f"Restart agent: `uri agent run {agent_id} --wait-healthy --approve` "
            f"or `repair://agent/{agent_id}/apply`"
        )
    if recommended == "repair":
        return f"Diagnose/repair: `repair://agent/{agent_id}/diagnose` then `repair://agent/{agent_id}/apply`"
    return None


def _display_planned(planned: list[str], subtype: str | None) -> list[str]:
    if subtype == "dashboard-agent":
        return [uri for uri in planned if not uri.startswith(("proposal://", "ecosystem://"))]
    return list(planned)


def _runtime_result_lines(data: dict[str, Any]) -> list[str]:
    payload = _payload_data(data)
    inspection = _first_dict(data.get("after"), data.get("inspection"), payload, data)
    lines: list[str] = []
    status_lines = _status_lines(inspection, payload)
    if status_lines:
        lines.append("\n### Runtime")
        lines.extend(status_lines)
    action_lines = _action_lines(data)
    if action_lines:
        lines.append("\n### Actions")
        lines.extend(action_lines)
    incident_lines = _incident_lines(inspection, payload)
    if incident_lines:
        lines.append("\n### Incidents")
        lines.extend(incident_lines)
    log_lines = _log_lines(inspection, payload)
    if log_lines:
        lines.append("\n### Logs")
        lines.extend(log_lines)
    return lines


# Use centralized unwrap from uri3 envelope to eliminate cross-boundary duplication
# (was duplicated in urish render/proof and here).
from uri3.results.envelope import unwrap_data as _payload_data


def _first_dict(*items: Any) -> dict[str, Any]:
    for item in items:
        if isinstance(item, dict):
            return item
    return {}


def _status_lines(inspection: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    process = _first_dict(inspection.get("process"), payload.get("process"))
    readiness = _first_dict(inspection.get("readiness"), payload.get("readiness"))
    health = _first_dict(inspection.get("health"), payload.get("health"))
    fields = {
        "service": inspection.get("service_status") or payload.get("service_status"),
        "process": readiness.get("process") or payload.get("process_status"),
        "health": readiness.get("health") or payload.get("health_status"),
        "pid": process.get("pid"),
        "running": process.get("running"),
        "port": inspection.get("effective_port") or payload.get("effective_port"),
        "health_uri": (
            inspection.get("effective_health_uri")
            or payload.get("effective_health_uri")
            or health.get("uri")
        ),
    }
    for label, value in fields.items():
        if value is not None and value != "":
            lines.append(f"- **{label}:** `{value}`")
    return lines


def _action_lines(data: dict[str, Any]) -> list[str]:
    actions = data.get("actions")
    if not isinstance(actions, list):
        return []
    lines: list[str] = []
    for item in actions[:6]:
        if not isinstance(item, dict):
            continue
        name = item.get("playbook") or item.get("strategy") or item.get("label") or "action"
        status = item.get("status") or item.get("service_result_status")
        result = item.get("result")
        if isinstance(result, dict):
            status = status or result.get("service_result_status") or result.get("runtime_status")
            if result.get("pid"):
                lines.append(f"- `{name}` → `{status or 'done'}` · pid `{result['pid']}`")
                continue
        lines.append(f"- `{name}` → `{status or 'done'}`")
    return lines


def _incident_lines(inspection: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    incidents = inspection.get("incidents") or payload.get("incidents") or []
    lines: list[str] = []
    seen: set[str] = set()
    if isinstance(incidents, list):
        for item in incidents[:6]:
            if not isinstance(item, dict):
                continue
            code = item.get("code") or "INCIDENT"
            detail = item.get("detail") or item.get("uri") or ""
            seen.add(code)
            lines.append(f"- `{code}` {detail}".rstrip())
    for code in payload.get("incident_codes") or []:
        if code and code not in seen:
            lines.append(f"- `{code}`")
    return lines


def _log_lines(inspection: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    candidates = [
        inspection.get("log_uri"),
        inspection.get("process_log_uri"),
        payload.get("log_uri"),
        payload.get("process_log_uri"),
    ]
    related = _first_dict(payload.get("related_uris"), inspection.get("related_uris"))
    candidates.append(related.get("logs"))
    runtime_state = _first_dict(inspection.get("runtime_state"), payload.get("runtime_state"))
    candidates.append(runtime_state.get("process_log_uri"))
    lines = []
    seen: set[str] = set()
    for uri in candidates:
        if not isinstance(uri, str) or not uri or uri in seen:
            continue
        seen.add(uri)
        lines.append(f"- `{uri}`")
    return lines


def _log_entry_preview_lines(data: dict[str, Any]) -> list[str]:
    if data.get("result_type") != "logs":
        return []
    entries = data.get("entries")
    if isinstance(entries, dict):
        entries = entries.get("entries") or []
    if not isinstance(entries, list) or not entries:
        return []
    lines = ["\n### Log entries"]
    for item in entries[-8:]:
        if isinstance(item, dict):
            level = item.get("level") or "log"
            message = str(item.get("message") or item.get("raw") or "").strip()
            line = item.get("line")
            prefix = f"- `{level}`"
            if line is not None:
                prefix += f" line `{line}`"
            lines.append(f"{prefix}: {_shorten_log_message(message)}")
        else:
            lines.append(f"- {_shorten_log_message(str(item).strip())}")
    return lines


def _shorten_log_message(message: str, *, limit: int = 220) -> str:
    compact = " ".join(message.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"

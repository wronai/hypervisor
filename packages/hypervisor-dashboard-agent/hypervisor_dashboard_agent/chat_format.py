from __future__ import annotations

from typing import Any


def _header_lines(data: dict[str, Any]) -> list[str]:
    subtype = data.get("detected_subtype")
    kind = data.get("detected_kind") or "unknown"
    if subtype:
        return [f"## Wykryto: `{subtype}`", f"Typ: **{kind}**"]
    return [f"## Wykryto: **{kind}**"]


def _identity_lines(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if data.get("ecosystem_id"):
        lines.append(f"\n**Nazwa:** `{data['ecosystem_id']}`")
    if data.get("profile"):
        lines.append(f"**Profil:** `{data['profile']}`")
    if data.get("agent_id"):
        lines.append(f"**Agent:** `agent://{data['agent_id']}`")
    if data.get("deployment_id"):
        lines.append(f"**Deployment:** `{data['deployment_id']}`")
    generated = data.get("generated") or {}
    if generated.get("proposal_path"):
        lines.append(f"\n**Proposal:** `{generated['proposal_path']}`")
    return lines


def _planned_lines(data: dict[str, Any]) -> list[str]:
    planned = data.get("planned_uris") or data.get("uris") or []
    display_planned = _display_planned(planned, data.get("detected_subtype"))
    if not display_planned:
        return []
    lines = ["\n### Planowane URI"]
    lines.extend(f"- `{uri}`" for uri in display_planned)
    return lines


def _next_step_lines(data: dict[str, Any]) -> list[str]:
    next_steps = data.get("next_steps") or []
    if not next_steps:
        return ["\n_Nie wykryto dalszych kroków — spróbuj doprecyzować prompt._"]
    lines = [
        "\n### Następne kroki",
        "Możesz skopiować komendę lub kliknąć **Uruchom** (dry-run domyślnie).",
    ]
    lines.extend(f"\n```bash\n{step}\n```" for step in next_steps)
    return lines


def format_ask_markdown(data: dict[str, Any]) -> str:
    """Turn urish ask payload into chat-friendly markdown."""
    lines = _header_lines(data)
    lines.extend(_identity_lines(data))
    lines.extend(_planned_lines(data))
    lines.extend(_next_step_lines(data))
    return "\n".join(lines).strip()


def format_uri_result_markdown(result: dict[str, Any]) -> str:
    """Compact markdown summary for URI call / execution envelopes."""
    result_type = result.get("result_type") or "result"
    if result_type == "dry_run" or result.get("status") == "preview":
        status = "preview"
    else:
        ok = bool(result.get("ok"))
        status = result.get("service_result_status") or ("succeeded" if ok else "failed")
    lines = [
        f"## URI: {status}",
        f"Typ: `{result_type}` · workflow: `{result.get('workflow_status', '—')}`",
    ]
    if result.get("policy_blocked"):
        lines.append("\n> **Policy blocked** — użyj `--approve` w komendzie lub włącz approve w UI.")
    data = result.get("data")
    if isinstance(data, dict) and data.get("error"):
        lines.append(f"\n**Błąd:** {data['error']}")
    elif isinstance(data, dict) and data.get("user_summary"):
        lines.append(f"\n{data['user_summary']}")
    lines.append("\n<details><summary>Envelope JSON</summary>\n")
    lines.append("```json")
    import json

    lines.append(json.dumps(result, indent=2, ensure_ascii=False)[:4000])
    lines.append("```\n</details>")
    return "\n".join(lines)


def _display_planned(planned: list[str], subtype: str | None) -> list[str]:
    if subtype == "dashboard-agent":
        return [uri for uri in planned if not uri.startswith(("proposal://", "ecosystem://"))]
    return list(planned)

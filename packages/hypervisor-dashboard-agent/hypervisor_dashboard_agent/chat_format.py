from __future__ import annotations

from typing import Any


def format_ask_markdown(data: dict[str, Any]) -> str:
    """Turn urish ask payload into chat-friendly markdown."""
    lines: list[str] = []
    subtype = data.get("detected_subtype")
    kind = data.get("detected_kind") or "unknown"

    if subtype:
        lines.append(f"## Wykryto: `{subtype}`")
        lines.append(f"Typ: **{kind}**")
    else:
        lines.append(f"## Wykryto: **{kind}**")

    if data.get("ecosystem_id"):
        lines.append(f"\n**Nazwa:** `{data['ecosystem_id']}`")
    if data.get("profile"):
        lines.append(f"**Profil:** `{data['profile']}`")
    if data.get("agent_id"):
        lines.append(f"**Agent:** `agent://{data['agent_id']}`")

    generated = data.get("generated") or {}
    if generated.get("proposal_path"):
        lines.append(f"\n**Proposal:** `{generated['proposal_path']}`")

    planned = data.get("planned_uris") or data.get("uris") or []
    display_planned = _display_planned(planned, subtype)
    if display_planned:
        lines.append("\n### Planowane URI")
        for uri in display_planned:
            lines.append(f"- `{uri}`")

    next_steps = data.get("next_steps") or []
    if next_steps:
        lines.append("\n### Następne kroki")
        lines.append("Możesz skopiować komendę lub kliknąć **Uruchom** (dry-run domyślnie).")
        for step in next_steps:
            lines.append(f"\n```bash\n{step}\n```")

    if not next_steps:
        lines.append("\n_Nie wykryto dalszych kroków — spróbuj doprecyzować prompt._")

    return "\n".join(lines).strip()


def format_uri_result_markdown(result: dict[str, Any]) -> str:
    """Compact markdown summary for URI call / execution envelopes."""
    ok = bool(result.get("ok"))
    status = result.get("service_result_status") or ("succeeded" if ok else "failed")
    result_type = result.get("result_type") or "result"
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

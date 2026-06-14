from __future__ import annotations

import json

import typer

from uri3.doctor.runner import run_doctor


def register(app: typer.Typer) -> None:
    @app.command()
    def doctor(
        registry: str = typer.Option("", "--registry", help="touri capability registry directory"),
        json_out: bool = typer.Option(False, "--json", help="Output JSON"),
        capability_plan: bool = typer.Option(False, "--capability-plan", help="Include uri2verify capability test plan check"),
        replay_failures: bool = typer.Option(False, "--replay-failures", help="Scan workflow logs for failed/blocked steps"),
        build_registry: bool = typer.Option(False, "--build-registry", help="Write .registry/ indexes"),
        strict_envelope: bool = typer.Option(False, "--strict-envelope", help="Fail when legacy workflow logs lack status fields"),
        migrate_envelope: bool = typer.Option(False, "--migrate-envelope", help="Backfill status fields in legacy workflow JSONL logs"),
    ) -> None:
        """Validate config, registries, explain resolution, and envelope consistency."""
        payload = run_doctor(
            registry=registry or None,
            capability_plan=capability_plan,
            replay_failures=replay_failures,
            build_registry=build_registry,
            strict_envelope=strict_envelope,
            migrate_envelope=migrate_envelope,
        )
        if json_out:
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            typer.echo(_render(payload))
        if not payload.get("ok"):
            raise typer.Exit(code=1)


def _render(payload: dict) -> str:
    lines = [f"doctor: {'ok' if payload.get('ok') else 'FAILED'}", f"registry: {payload.get('registry')}"]
    for check in payload.get("checks") or []:
        status = "ok" if check.get("ok") else "FAIL"
        detail = _check_summary(check)
        lines.append(f"  [{status}] {check.get('id')}{detail}")
    index = payload.get("registry_index") or {}
    if index:
        lines.append(f"registry_index: {index.get('directory')}")
        for path in index.get("files") or []:
            lines.append(f"  - {path}")
    warnings = payload.get("warnings") or []
    if warnings:
        lines.append("warnings:")
        for warning in warnings[:10]:
            lines.append(f"  - {warning}")
        if len(warnings) > 10:
            lines.append(f"  ... and {len(warnings) - 10} more")
    return "\n".join(lines)


def _check_summary(check: dict) -> str:
    if check.get("id") == "touri.registry":
        return f" ({check.get('manifests', 0)} manifests)"
    if check.get("id") == "uri2ops.registry":
        return f" ({check.get('operations', 0)} operations)"
    if check.get("id") == "contract_registry":
        counts = check.get("counts") or {}
        return f" (capabilities={counts.get('capabilities', 0)})"
    if check.get("id") == "explain.smoke":
        return f" ({check.get('checked', 0)} checked, {len(check.get('mismatches') or [])} mismatches)"
    if check.get("id") == "envelope.recent_logs":
        return f" ({check.get('logs', 0)} logs, {check.get('missing_fields', 0)} missing fields)"
    if check.get("id") == "uri2verify.capability_plan":
        return f" ({check.get('tests', 0)} tests)"
    if check.get("id") == "uri2verify.replay_failures":
        return f" ({len(check.get('failures') or [])} failing workflows)"
    if check.get("id") == "boundaries.imports":
        return f" ({check.get('violation_count', 0)} violations)"
    if check.get("id") == "runtime.uri2run_transports":
        return f" ({len(check.get('checked') or [])} transports, {len(check.get('failures') or [])} failures)"
    if check.get("id") == "runtime.browser_delegation":
        return f" (adapter={check.get('adapter')})"
    return ""

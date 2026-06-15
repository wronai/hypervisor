from __future__ import annotations

from typing import Any

import typer

from urish.commands.deps import RuntimeCommandDeps
from urish.commands.ticket_commands import print_ticket_summary


def register_evolution_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    evolve_app = typer.Typer(help="Evolution proposals from tickets and incidents")
    proposal_app = typer.Typer(help="Verify and apply evolution proposals")

    @evolve_app.command("from-ticket")
    def evolve_from_ticket_cmd(
        target: str,
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.evolve import evolve_from_ticket

        try:
            result = evolve_from_ticket(target)
        except FileNotFoundError as exc:
            result = {"ok": False, "not_found": True, "error": str(exc)}
        _print_evolve_summary(result, json_out=json_out)
        deps.emit(
            result,
            output="json" if json_out else "yaml",
            quiet=not json_out,
            json_out=json_out,
        )
        deps.finish(result)

    @evolve_app.command("from-incident")
    def evolve_from_incident_cmd(
        incident_path: str,
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.evolve import evolve_from_incident

        result = evolve_from_incident(incident_path)
        _print_evolve_summary(result, json_out=json_out)
        deps.emit(
            result,
            output="json" if json_out else "yaml",
            quiet=not json_out,
            json_out=json_out,
        )
        deps.finish(result)

    @proposal_app.command("verify")
    def proposal_verify_cmd(
        path: str,
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.evolve import proposal_verify

        result = proposal_verify(path)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @proposal_app.command("apply")
    def proposal_apply_cmd(
        path: str,
        approve: bool = typer.Option(False, "--approve"),
        sandbox: bool = typer.Option(False, "--sandbox"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.evolve import proposal_apply

        result = proposal_apply(path, approve=approve, sandbox=sandbox)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result, policy_blocked=bool(result.get("policy_blocked")))

    app.add_typer(evolve_app, name="evolve")
    app.add_typer(proposal_app, name="proposal")


def _print_evolve_summary(result: dict[str, Any], *, json_out: bool) -> None:
    if json_out or not result.get("ok"):
        return
    data = result.get("data")
    if not isinstance(data, dict):
        return
    if data.get("proposal_path"):
        typer.echo(f"Generated proposal: {data['proposal_path']}")
    print_ticket_summary(data)

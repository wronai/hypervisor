from __future__ import annotations

from typing import Any

import typer

from urish.commands.deps import RuntimeCommandDeps


def register_ticket_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    ticket_app = typer.Typer(help="Ticket artifacts and planfile integration")

    @ticket_app.command("list")
    def ticket_list_cmd(json_out: bool = typer.Option(False, "--json")) -> None:
        from urish.backends.ticket import list_tickets

        result = list_tickets()
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)

    @ticket_app.command("show")
    def ticket_show_cmd(
        target: str,
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.ticket import show_ticket

        try:
            result = show_ticket(target)
        except FileNotFoundError as exc:
            result = {"ok": False, "not_found": True, "error": str(exc)}
        if not json_out and result.get("ok") and isinstance(result.get("data"), dict):
            print_ticket_summary(result["data"])
        deps.emit(
            result,
            output="json" if json_out else "yaml",
            quiet=not json_out,
            json_out=json_out,
        )
        deps.finish(result)

    @ticket_app.command("import")
    def ticket_import_cmd(
        strategy: str = typer.Argument(...),
        sprint: str = typer.Option("", "--sprint"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.ticket import import_tickets

        result = import_tickets(strategy, sprint=sprint)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @ticket_app.command("plan")
    def ticket_plan_cmd(
        target: str,
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.ticket import plan_ticket

        try:
            result = plan_ticket(target)
        except FileNotFoundError as exc:
            result = {"ok": False, "not_found": True, "error": str(exc)}
        if not json_out and result.get("ok") and isinstance(result.get("data"), dict):
            data = result["data"]
            if data.get("proposal_path"):
                typer.echo(f"Generated proposal: {data['proposal_path']}")
            print_ticket_summary(data)
        deps.emit(
            result,
            output="json" if json_out else "yaml",
            quiet=not json_out,
            json_out=json_out,
        )
        deps.finish(result)

    app.add_typer(ticket_app, name="ticket")


def print_ticket_summary(data: dict[str, Any]) -> None:
    intent = data.get("detected_intent") or {}
    if intent.get("subtype"):
        typer.echo(f"Detected: {intent.get('kind')} / {intent.get('subtype')}")
    if data.get("next_steps"):
        typer.echo("Next:")
        for step in data["next_steps"]:
            typer.echo(f"  {step}")

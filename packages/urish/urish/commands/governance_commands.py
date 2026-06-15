from __future__ import annotations

import typer

from urish.commands.deps import RuntimeCommandDeps
from urish.commands.evolution_commands import register_evolution_commands
from urish.commands.repair_commands import register_repair_commands
from urish.commands.ticket_commands import register_ticket_commands


def register_governance_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    register_ticket_commands(app, deps)
    register_repair_commands(app, deps)
    register_evolution_commands(app, deps)

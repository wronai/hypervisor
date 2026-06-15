from __future__ import annotations

import typer

from urish.commands.call_commands import register_call_commands
from urish.commands.deps import RuntimeCommandDeps
from urish.commands.observe_commands import register_observe_commands
from urish.commands.run_commands import register_run_commands

__all__ = ["RuntimeCommandDeps", "register_runtime_commands"]


def register_runtime_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    register_call_commands(app, deps)
    register_run_commands(app, deps)
    register_observe_commands(app, deps)

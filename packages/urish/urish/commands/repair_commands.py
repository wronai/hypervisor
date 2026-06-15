from __future__ import annotations

import typer

from urish.commands.deps import RuntimeCommandDeps


def register_repair_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    repair_app = typer.Typer(help="Self-healing repair supervisor")

    @repair_app.command("diagnose")
    def repair_diagnose_cmd(
        selector: str = typer.Argument(...),
        timeout: float = typer.Option(2.0, "--timeout"),
        log_limit: int = typer.Option(20, "--log-limit"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.repair import repair_diagnose

        result = repair_diagnose(selector, timeout=timeout, log_limit=log_limit)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @repair_app.command("apply")
    def repair_apply_cmd(
        selector: str = typer.Argument(...),
        dry_run: bool = typer.Option(False, "--dry-run"),
        approve: bool = typer.Option(False, "--approve"),
        safe: bool = typer.Option(True, "--safe/--unsafe"),
        playbook: str = typer.Option("", "--playbook"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.repair import repair_apply, repair_diagnose

        if dry_run:
            result = repair_diagnose(selector)
        else:
            result = repair_apply(selector, safe=safe, approve=approve, playbook=playbook or None)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @repair_app.command("learn")
    def repair_learn_cmd(
        incident_path: str = typer.Argument(...),
        sandbox: bool = typer.Option(True, "--sandbox/--no-sandbox"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.repair import repair_learn

        result = repair_learn(incident_path, sandbox=sandbox)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    app.add_typer(repair_app, name="repair")

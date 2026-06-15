from __future__ import annotations

import typer

from urish.commands.deps import RuntimeCommandDeps


def register_environment_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    env_app = typer.Typer(help="Execution environment and operator runtime profiles")

    @env_app.command("list")
    def environments_list_cmd(
        operator: str = typer.Option("", "--operator", help="Fetch live /environments from operator"),
        live: bool = typer.Option(False, "--live", help="Fetch from --operator or default browser-operator"),
        base_url: str = typer.Option("", "--base-url", help="Override operator base URL"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.environments import list_environments

        selected_operator = operator or ("browser-operator.local" if live else "")
        result = list_environments(
            operator=selected_operator,
            live=live or bool(operator),
            base_url=base_url,
        )
        payload = result.get("data", result)
        if isinstance(payload, dict) and "ok" not in payload:
            payload = {"ok": result.get("ok", True), **payload}
        deps.emit(
            payload,
            output="json" if json_out else "yaml",
            quiet=False,
            json_out=json_out,
        )
        deps.finish(result)

    @env_app.command("validate")
    def environments_validate_cmd(
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.environments import validate_environments

        result = validate_environments()
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    app.add_typer(env_app, name="environments")

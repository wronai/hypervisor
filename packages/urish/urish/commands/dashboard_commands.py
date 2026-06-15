from __future__ import annotations

import sys

import typer

from urish.commands.deps import RuntimeCommandDeps


def register_dashboard_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    dashboard_app = typer.Typer(help="Dashboard system-agent workflow shortcuts")
    www_app = typer.Typer(help="Chat UI in repo www/ (NL + markdown + real API)")

    @dashboard_app.command("create")
    def dashboard_create_cmd(
        name: str = typer.Argument("hypervisor-dashboard"),
        prompt: str = typer.Option("", "--prompt"),
        plan_only: bool = typer.Option(False, "--plan-only"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        sandbox: bool = typer.Option(False, "--sandbox"),
        approve: bool = typer.Option(False, "--approve"),
        open_ui: bool = typer.Option(False, "--open"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.dashboard import create_dashboard

        result = create_dashboard(
            name,
            prompt=prompt or None,
            plan_only=plan_only,
            dry_run=dry_run,
            sandbox=sandbox,
            approve=approve,
            open_browser=open_ui,
        )
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @dashboard_app.command("open")
    def dashboard_open_cmd(
        url: str = typer.Option("http://localhost:8788/ui", "--url"),
        approve: bool = typer.Option(False, "--approve"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.call import call_uri
        from urish.policy import PolicyOptions

        result = call_uri(
            "browser://chrome/page/open",
            payload={"url": url},
            dry_run=dry_run,
            policy_options=PolicyOptions.from_flags(approve=approve, dry_run=dry_run),
        )
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @www_app.command("serve")
    def www_serve_cmd(
        host: str = typer.Option("0.0.0.0", "--host"),
        port: int = typer.Option(8788, "--port"),
        reload: bool = typer.Option(False, "--reload"),
    ) -> None:
        """Serve www/ chat and dashboard-agent API (uvicorn)."""
        try:
            import uvicorn
        except ImportError as exc:
            raise typer.BadParameter(
                "Brak uvicorn w bieżącym interpreterze Python.\n"
                f"  python: {sys.executable}\n"
                "  pip install uvicorn\n"
                '  pip install -e ".[server]"   # z katalogu repo hypervisor\n'
                "  source .venv/bin/activate    # jeśli używasz lokalnego venv\n"
                "Jeśli port 8788 jest zajęty (Docker/cron): make stop && urish www serve"
            ) from exc

        typer.echo(f"Chat UI: http://localhost:{port}/www/")
        uvicorn.run(
            "hypervisor_dashboard_agent.main:app",
            host=host,
            port=port,
            reload=reload,
        )

    @www_app.command("open")
    def www_open_cmd(
        host: str = typer.Option("localhost", "--host"),
        port: int = typer.Option(8788, "--port"),
        approve: bool = typer.Option(False, "--approve"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        """Open www chat in browser (requires running dashboard-agent)."""
        from urish.backends.call import call_uri
        from urish.policy import PolicyOptions

        url = f"http://{host}:{port}/www/"
        result = call_uri(
            "browser://chrome/page/open",
            payload={"url": url},
            dry_run=dry_run,
            policy_options=PolicyOptions.from_flags(approve=approve, dry_run=dry_run),
        )
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @www_app.command("create")
    def www_create_cmd(
        prompt: str = typer.Argument(
            "stwórz prosty web UI hypervisora jako chat markdown połączony z API systemu"
        ),
        name: str = typer.Option("hypervisor-dashboard", "--name"),
        plan_only: bool = typer.Option(False, "--plan-only"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        sandbox: bool = typer.Option(False, "--sandbox"),
        approve: bool = typer.Option(False, "--approve"),
        open_ui: bool = typer.Option(False, "--open"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        """Create the www chat/dashboard agent from a natural-language prompt."""
        from urish.backends.dashboard import create_dashboard

        result = create_dashboard(
            name,
            prompt=prompt,
            plan_only=plan_only,
            dry_run=dry_run,
            sandbox=sandbox,
            approve=approve,
            open_browser=open_ui,
        )
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    app.add_typer(dashboard_app, name="dashboard")
    app.add_typer(www_app, name="www")

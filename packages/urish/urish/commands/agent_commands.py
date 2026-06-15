from __future__ import annotations

from pathlib import Path

import typer

from urish.commands.deps import RuntimeCommandDeps


def register_agent_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    agent_app = typer.Typer(
        help="Agent lifecycle shortcuts (maps to hypervisor:// / repair://)"
    )

    @agent_app.command("status")
    def agent_status_cmd(
        selector: str,
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.agent import agent_action

        result = agent_action("status", selector)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @agent_app.command("health")
    def agent_health_cmd(
        selector: str,
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.agent import agent_action

        result = agent_action("health", selector)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @agent_app.command("create-dashboard")
    def agent_create_dashboard_cmd(
        name: str = typer.Argument("hypervisor-dashboard"),
        prompt: str = typer.Option("", "--prompt"),
        plan_only: bool = typer.Option(False, "--plan-only"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        sandbox: bool = typer.Option(False, "--sandbox"),
        approve: bool = typer.Option(False, "--approve"),
        open_ui: bool = typer.Option(False, "--open"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        """Alias for dashboard create — ecosystem plan→generate→verify→apply→run."""
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

    @agent_app.command("run")
    def agent_run_cmd(
        selector: str,
        detach: bool = typer.Option(True, "--detach/--no-detach"),
        wait_healthy: bool = typer.Option(False, "--wait-healthy"),
        approve: bool = typer.Option(False, "--approve"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.agent import agent_action
        from urish.policy import evaluate_policy

        policy_opts = deps.policy_options(
            dry_run=dry_run,
            approve=approve,
            no_approve=False,
            readonly=False,
            sandbox=False,
            policy="",
        )
        uri = f"hypervisor://local/{selector}/run"
        allowed, reason, force_dry_run = evaluate_policy(
            uri,
            options=policy_opts,
            context_policy=deps.context_policy(),
        )
        if not allowed:
            result = {"ok": False, "policy_blocked": True, "error": reason}
            deps.emit(result, output="json", quiet=False, json_out=True)
            deps.finish(result, policy_blocked=True)
        if force_dry_run:
            result = {
                "ok": True,
                "result_type": "plan",
                "data": {"action": "run", "selector": selector},
            }
            deps.emit(
                result,
                output="json" if json_out else "text",
                quiet=False,
                json_out=json_out,
            )
            deps.finish(result)
        result = agent_action(
            "run",
            selector,
            detach=detach,
            wait_healthy=wait_healthy,
            supervise_repair="auto",
        )
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @agent_app.command("generate")
    def agent_generate_cmd(
        prompt: str,
        name: str = typer.Option("", "--name"),
        port: int = typer.Option(0, "--port"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        approve: bool = typer.Option(False, "--approve"),
        overwrite: bool = typer.Option(False, "--overwrite"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        """Generate a resource agent contract/package/deployment from NL."""
        from urish.backends.agent_factory import generate_agent_from_prompt

        result = generate_agent_from_prompt(
            prompt,
            name=name or None,
            port=port or None,
            dry_run=dry_run or not approve,
            approve=approve,
            overwrite=overwrite,
        )
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @agent_app.command("describe")
    def agent_describe_cmd(
        selector: str,
        output: str | None = typer.Option(None, "--output", "-o", help="Write markdown report"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from hypervisor.agent_describe import describe_agent

        report = describe_agent(selector)
        output_path = Path(output) if output else None
        if output_path is not None:
            written = report.write(output_path)
            result = {"ok": True, "written": str(written), **report.data}
            if json_out:
                deps.emit(result, output="json", quiet=False, json_out=True)
            else:
                typer.echo(f"Wrote agent report: {written}")
            deps.finish(result)
            return
        if json_out:
            result = {"ok": True, "markdown": report.markdown, **report.data}
            deps.emit(result, output="json", quiet=False, json_out=True)
        else:
            typer.echo(report.markdown)
        deps.finish({"ok": True, **report.data})

    @agent_app.command("repair")
    def agent_repair_cmd(
        selector: str,
        dry_run: bool = typer.Option(False, "--dry-run"),
        approve: bool = typer.Option(False, "--approve"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urish.backends.agent import agent_action

        if dry_run:
            result = agent_action("diagnose", selector)
        else:
            result = agent_action("repair", selector, safe=not approve, approve=approve)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    app.add_typer(agent_app, name="agent")

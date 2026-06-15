from __future__ import annotations

import typer

from urish.commands.deps import RuntimeCommandDeps
from urish.payload import load_payload


def register_run_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    @app.command("run")
    def run_cmd(
        target: str = typer.Argument(..., help="Flow/graph/task file or workflow:// URI"),
        approve: bool = typer.Option(False, "--approve"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        no_approve: bool = typer.Option(False, "--no-approve"),
        readonly: bool = typer.Option(False, "--readonly"),
        policy: str = typer.Option("", "--policy"),
        adapter: str = typer.Option("mock", "--adapter"),
        json_out: bool = typer.Option(False, "--json"),
        stdin: bool = typer.Option(False, "--stdin"),
    ) -> None:
        """Run workflow graph, uri flow, or uri2ops task."""
        from urish.backends.run import run_target
        from urish.policy import evaluate_policy

        policy_opts = deps.policy_options(
            dry_run=dry_run,
            approve=approve,
            no_approve=no_approve,
            readonly=readonly,
            sandbox=False,
            policy=policy,
        )
        allowed, reason, force_dry_run = evaluate_policy(
            target if "://" in target else f"workflow://file/{target}",
            options=policy_opts,
            context_policy=deps.context_policy(),
        )
        if not allowed:
            result = {"ok": False, "policy_blocked": True, "error": reason}
            deps.emit(result, output="json" if json_out else "text", quiet=False, json_out=json_out)
            deps.finish(result, policy_blocked=True)
            return
        if force_dry_run:
            dry_run = True
        body = load_payload(stdin=stdin) if stdin else {}
        result = run_target(target, approve=approve, dry_run=dry_run, adapter=adapter, payload=body)
        deps.emit(result, output="json" if json_out else "text", quiet=False, json_out=json_out)
        deps.finish(result)

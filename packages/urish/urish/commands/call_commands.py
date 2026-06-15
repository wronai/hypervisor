from __future__ import annotations

import json

import typer

from urish.commands.deps import RuntimeCommandDeps
from urish.payload import load_payload
from urish.shortcuts import resolve_shortcut, resolve_target


def register_call_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    @app.command("call")
    def call_cmd(
        target: str = typer.Argument(..., help="URI to execute"),
        payload: str = typer.Option("{}", "--payload"),
        payload_file: str = typer.Option("", "--payload-file"),
        backend_type: str = typer.Option("", "--type"),
        timeout: float = typer.Option(30.0, "--timeout"),
        json_out: bool = typer.Option(False, "--json"),
        output: str = typer.Option("text", "--output"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        approve: bool = typer.Option(False, "--approve"),
        no_approve: bool = typer.Option(False, "--no-approve"),
        readonly: bool = typer.Option(False, "--readonly"),
        sandbox: bool = typer.Option(False, "--sandbox"),
        policy: str = typer.Option("", "--policy", help="safe|dev|prod"),
        quiet: bool = typer.Option(False, "--quiet"),
        explain_first: bool = typer.Option(
            False, "--explain-first", help="Print explain before call"
        ),
        stdin: bool = typer.Option(False, "--stdin"),
        stdin_data: bool = typer.Option(False, "--stdin-data"),
        stdin_envelope: bool = typer.Option(False, "--stdin-envelope"),
        select: str = typer.Option("", "--select", help="Dot path to extract from stdin envelope"),
    ) -> None:
        """Execute URI via uri3 explain -> uri2run transport -> envelope."""
        from urish.backends.call import call_uri
        from urish.select import select_from_envelope

        policy_opts = deps.policy_options(
            dry_run=dry_run,
            approve=approve,
            no_approve=no_approve,
            readonly=readonly,
            sandbox=sandbox,
            policy=policy,
        )
        try:
            shortcut = resolve_shortcut(target)
            uri = str(shortcut["uri"])
        except ValueError as exc:
            result = {"ok": False, "error": str(exc), "not_found": True}
            deps.emit(result, output=output, quiet=quiet, json_out=True)
            deps.finish(result)
            return

        stdin_mode = "data"
        if stdin_envelope:
            stdin_mode = "envelope"
        elif stdin_data:
            stdin_mode = "data"
        body = load_payload(
            payload,
            payload_file=payload_file or None,
            stdin=stdin or stdin_data or stdin_envelope,
            stdin_mode=stdin_mode,
        )
        if (
            not body
            and payload == "{}"
            and not payload_file
            and not (stdin or stdin_data or stdin_envelope)
        ):
            body = dict(shortcut.get("payload") or {})
        if select and stdin:
            body = {
                "value": select_from_envelope(
                    body if "data" in body else {"data": body},
                    select,
                )
            }

        if explain_first and not json_out and output == "text":
            explain_cmd(uri, json_out=False, output="text")
            typer.echo("")

        result = call_uri(
            uri,
            body,
            backend_type=backend_type,
            timeout=timeout,
            dry_run=dry_run,
            policy_options=policy_opts,
            context_policy=deps.context_policy(),
        )
        deps.emit(result, output=output, quiet=quiet, json_out=json_out)
        deps.finish(result)

    @app.command("explain")
    def explain_cmd(
        target: str = typer.Argument(...),
        registry: str = typer.Option("", "--registry"),
        json_out: bool = typer.Option(False, "--json"),
        output: str = typer.Option("text", "--output"),
    ) -> None:
        """Show how a URI will be resolved and executed."""
        from urish.backends.explain import explain_target
        from urish.render import render_result

        uri = resolve_target(target)
        payload = explain_target(uri, registry=registry or None)
        payload.setdefault("ok", True)
        payload.setdefault("result_type", "explain")
        if json_out or output == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            typer.echo(render_result(payload, output="yaml"))
        deps.finish(payload)

    @app.command("plan")
    def plan_cmd(
        target: str = typer.Argument(...),
        payload: str = typer.Option("{}", "--payload"),
        payload_file: str = typer.Option("", "--payload-file"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        """Dry-run plan for a URI (explain + simulated call)."""
        call_cmd(
            target,
            payload=payload,
            payload_file=payload_file,
            backend_type="",
            timeout=30.0,
            json_out=json_out,
            output="json" if json_out else "yaml",
            dry_run=True,
            approve=False,
            no_approve=False,
            readonly=False,
            sandbox=False,
            policy="",
            quiet=False,
            explain_first=False,
            stdin=False,
            stdin_data=False,
            stdin_envelope=False,
            select="",
        )

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import typer

from urish.payload import load_payload
from urish.shortcuts import resolve_target


@dataclass(frozen=True)
class RuntimeCommandDeps:
    policy_options: Callable[..., Any]
    context_policy: Callable[[], str | None]
    emit: Callable[..., None]
    finish: Callable[..., None]


def register_runtime_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
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
            uri = resolve_target(target)
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

    @app.command("logs")
    def logs_cmd(
        target: str = typer.Argument(..., help="log:// URI"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        """Read logs through log:// URI."""
        from urish.backends.logs import read_log_uri

        uri = resolve_target(target) if "://" not in target else target
        if not uri.startswith("log://"):
            uri = f"log://{uri}"
        result = read_log_uri(uri)
        deps.emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
        deps.finish(result)

    @app.command("watch")
    def watch_cmd(
        target: str = typer.Argument(..., help="health://, log:// or agent id"),
        interval: float = typer.Option(2.0, "--interval"),
        count: int = typer.Option(0, "--count", help="Stop after N events (0 = infinite)"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        """Observe URI state continuously (health, logs, agents)."""
        from urish.backends.watch import render_event, watch_uri

        def _on_event(event: dict[str, Any]) -> None:
            typer.echo(render_event(event, json_out=json_out))

        if count:
            result = watch_uri(target, interval=interval, max_events=count, on_event=_on_event)
            deps.finish(result)
            return

        try:
            watch_uri(target, interval=interval, max_events=0, on_event=_on_event)
        except KeyboardInterrupt:
            raise typer.Exit(0) from None

    @app.command("stream")
    def stream_cmd(
        target: str = typer.Argument(..., help="sse:// or ws:// URI"),
        count: int = typer.Option(0, "--count", help="Stop after N events (0 = infinite)"),
        timeout: float = typer.Option(30.0, "--timeout"),
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        """Stream SSE/WS events as RuntimeEvent envelopes."""
        from urish.backends.stream import stream_uri

        def _on_event(event: dict[str, Any]) -> None:
            typer.echo(json.dumps(event, ensure_ascii=False))

        try:
            result = stream_uri(target, max_events=count, timeout=timeout, on_event=_on_event)
        except KeyboardInterrupt:
            raise typer.Exit(0) from None
        if count:
            deps.finish(result)

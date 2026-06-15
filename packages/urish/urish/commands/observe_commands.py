from __future__ import annotations

import json
from typing import Any

import typer

from urish.commands.deps import RuntimeCommandDeps
from urish.shortcuts import resolve_target


def register_observe_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
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

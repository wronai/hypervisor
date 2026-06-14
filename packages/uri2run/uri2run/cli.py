from __future__ import annotations

import json
import sys
from typing import Any

import typer

app = typer.Typer(help="uri2run — neutral transport runtime for capability backends")


@app.callback()
def root() -> None:
    """Execute URI runtime transports."""


def _json_payload(raw: str) -> dict[str, Any]:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise typer.BadParameter("--payload must decode to a JSON object")
    return payload


@app.command("call")
def call_cmd(
    target: str = typer.Argument(..., help="python://module:func, shell command, or http URL"),
    backend_type: str = typer.Option("", "--type", help="Transport type when target is ambiguous"),
    payload_json: str = typer.Option("{}", "--payload", help="JSON payload"),
    timeout: float = typer.Option(30.0, "--timeout", help="Timeout in seconds"),
) -> None:
    """Execute a backend through uri2run."""
    from uri2run import run_backend

    payload = _json_payload(payload_json)
    backend = _backend_from_target(target, backend_type=backend_type)
    result = run_backend(backend, payload, {"timeout": timeout})
    typer.echo(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    if not result.ok:
        raise typer.Exit(code=1)


def _backend_from_target(target: str, *, backend_type: str) -> dict[str, Any]:
    if backend_type:
        kind = backend_type
    elif target.startswith("python://"):
        kind = "python"
    elif target.startswith("shell://"):
        kind = "shell"
    elif target.startswith(("http://", "https://")):
        kind = "http"
    elif target.startswith("stdio://"):
        kind = "stdio"
    elif target.startswith("sse://"):
        kind = "sse"
    elif target.startswith(("ws://", "wss://")):
        kind = "ws"
    elif target.startswith("docker://"):
        kind = "docker"
    elif target.startswith("ssh://"):
        kind = "ssh"
    elif target.startswith("mcp://"):
        kind = "mcp"
    elif target.startswith("a2a://"):
        kind = "a2a"
    else:
        kind = "shell"
    if kind == "python":
        return {"type": "python", "target": target}
    if kind == "http":
        return {"type": "http", "url": target}
    if kind == "stdio":
        return {"type": "stdio", "command": target.removeprefix("stdio://")}
    if kind == "sse":
        return {"type": "sse", "url": target}
    if kind == "ws":
        return {"type": "ws", "url": target}
    if kind == "docker":
        return {"type": "docker", "target": target}
    if kind == "ssh":
        return {"type": "ssh", "target": target}
    if kind == "mcp":
        return {"type": "mcp", "target": target}
    if kind == "a2a":
        return {"type": "a2a", "target": target}
    if kind == "shell":
        return {"type": "shell", "command": target.removeprefix("shell://")}
    return {"type": kind, "target": target}


def main(argv: list[str] | None = None) -> int:
    try:
        app(prog_name="uri2run", args=argv or sys.argv[1:], standalone_mode=False)
    except typer.Exit as exc:
        return int(exc.code or 0)
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

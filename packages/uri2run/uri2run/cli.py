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


_PREFIX_KINDS: tuple[tuple[str, str], ...] = (
    ("python://", "python"),
    ("shell://", "shell"),
    ("stdio://", "stdio"),
    ("sse://", "sse"),
    ("docker://", "docker"),
    ("ssh://", "ssh"),
    ("mcp://", "mcp"),
    ("a2a://", "a2a"),
)


def _build_backend(kind: str, target: str) -> dict[str, Any]:
    if kind == "python":
        return {"type": "python", "target": target}
    if kind == "http":
        return {"type": "http", "url": target}
    if kind == "stdio":
        return {"type": "stdio", "command": target.removeprefix("stdio://")}
    if kind in {"sse", "ws"}:
        return {"type": kind, "url": target}
    if kind == "shell":
        return {"type": "shell", "command": target.removeprefix("shell://")}
    return {"type": kind, "target": target}


def _infer_backend_kind(target: str, *, backend_type: str) -> str:
    if backend_type:
        return backend_type
    for prefix, kind in _PREFIX_KINDS:
        if target.startswith(prefix):
            return kind
    if target.startswith(("http://", "https://")):
        return "http"
    if target.startswith(("ws://", "wss://")):
        return "ws"
    return ""


def _backend_from_target(target: str, *, backend_type: str) -> dict[str, Any]:
    from uri2run.voice_resolver import resolve_voice_backend

    kind = _infer_backend_kind(target, backend_type=backend_type)
    if not kind:
        voice_backend = resolve_voice_backend(target)
        if voice_backend is not None:
            return voice_backend
        kind = "shell"
    return _build_backend(kind, target)


@app.command("doctor")
def doctor_cmd() -> None:
    """Check uri2run transport dependencies."""
    from uri2run.doctor import doctor_transport_dependencies

    typer.echo(json.dumps(doctor_transport_dependencies(), indent=2, ensure_ascii=False))


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

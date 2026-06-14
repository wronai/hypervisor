from __future__ import annotations

import json
import sys
from typing import Annotated, Any

import typer

from uri2run import run_target

app = typer.Typer(help="uri2run — execute one URI backend through a runtime transport")


def _json_payload(raw: str) -> dict[str, Any]:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise typer.BadParameter("--payload must decode to a JSON object")
    return payload


@app.command("call")
def call_cmd(
    target: Annotated[str, typer.Argument(help="python://, shell://, http:// or https:// target")],
    payload_json: Annotated[str, typer.Option("--payload", help="JSON payload")] = "{}",
) -> None:
    result = run_target(target, payload=_json_payload(payload_json))
    typer.echo(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    try:
        app(prog_name="uri2run", args=argv or sys.argv[1:])
    except typer.Exit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

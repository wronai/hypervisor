from __future__ import annotations

import json
import os
import sys
from typing import Any

import typer

from urish.commands.agent_commands import register_agent_commands
from urish.commands.dashboard_commands import register_dashboard_commands
from urish.commands.ecosystem_commands import register_ecosystem_commands
from urish.commands.governance_commands import register_governance_commands
from urish.commands.runtime import RuntimeCommandDeps, register_runtime_commands
from urish.context import CONTEXT_ENV, list_contexts, load_context
from urish.exit_codes import exit_code_for_result
from urish.policy import PolicyOptions
from urish.render import render_result
from urish.repl import run_repl
from urish.shortcuts import load_shortcut_specs, load_shortcuts

app = typer.Typer(
    help="urish — unified URI shell (URI + payload + context + policy → envelope)",
    no_args_is_help=True,
    invoke_without_command=True,
)

context_app = typer.Typer(help="Execution context")


def _policy_options(
    *,
    dry_run: bool,
    approve: bool,
    no_approve: bool,
    readonly: bool,
    sandbox: bool,
    policy: str,
) -> PolicyOptions:
    ctx = load_context()
    default_policy = (ctx.get("spec") or {}).get("default_policy", "dev")
    selected = policy or default_policy
    return PolicyOptions.from_flags(
        dry_run=dry_run,
        approve=approve,
        no_approve=no_approve,
        readonly=readonly,
        sandbox=sandbox,
        policy=selected,
    )


def _context_policy() -> str | None:
    ctx = load_context()
    return (ctx.get("spec") or {}).get("default_policy")


def _emit(result: dict[str, Any], *, output: str, quiet: bool, json_out: bool) -> None:
    fmt = "json" if json_out else output
    typer.echo(render_result(result, output=fmt, quiet=quiet))


def _finish(result: dict[str, Any], *, policy_blocked: bool = False) -> None:
    blocked = policy_blocked or bool(result.get("policy_blocked"))
    code = exit_code_for_result(result, policy_blocked=blocked)
    if code:
        raise SystemExit(code)


_COMMAND_DEPS = RuntimeCommandDeps(
    policy_options=_policy_options,
    context_policy=_context_policy,
    emit=_emit,
    finish=_finish,
)
register_runtime_commands(app, _COMMAND_DEPS)
register_agent_commands(app, _COMMAND_DEPS)
register_ecosystem_commands(app, _COMMAND_DEPS)
register_dashboard_commands(app, _COMMAND_DEPS)
register_governance_commands(app, _COMMAND_DEPS)


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    """Default help when invoked without URI or subcommand."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


def _print_ask_result(data: dict[str, Any]) -> None:
    """Pretty printer for ask/nl results. Extracted to keep command surface thinner."""
    subtype = data.get("detected_subtype")
    kind = data.get("detected_kind")
    if subtype:
        typer.echo(f"Detected: {subtype} {kind}")
    else:
        typer.echo(f"Detected: {kind}")
    if data.get("ecosystem_id"):
        typer.echo(f"Name: {data['ecosystem_id']}")
    if data.get("profile"):
        typer.echo(f"Profile: {data['profile']}")
    if data.get("agent_id"):
        typer.echo(f"Agent: agent://{data['agent_id']}")
    if data.get("generated", {}).get("proposal_path"):
        typer.echo(f"Generated proposal: {data['generated']['proposal_path']}")
    from urish.ecosystem_workflow import build_planned_uris_display

    planned = build_planned_uris_display(data.get("planned_uris") or data["uris"])
    typer.echo("Planned:")
    for uri in planned:
        typer.echo(f"  {uri}")
    typer.echo("Next:")
    for step in data["next_steps"]:
        typer.echo(f"  {step}")


@app.command("ask")
def ask_cmd(
    prompt: str = typer.Argument(..., help="Natural language prompt"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute"),
    llm: bool = typer.Option(False, "--llm"),
    json_out: bool = typer.Option(False, "--json"),
    out: str = typer.Option("", "--out", help="Write generated artifact to file"),
) -> None:
    """Natural language → URI proposal/flow (does not execute directly)."""
    from urish.backends.ask import ask_prompt

    result = ask_prompt(prompt, dry_run=dry_run, use_llm=llm)
    if out:
        from pathlib import Path

        import yaml

        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(
            yaml.safe_dump(result["data"]["generated"], sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    if json_out:
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_ask_result(result["data"])
    _finish(result)


@app.command("nl")
def nl_cmd(
    prompt: str = typer.Argument(...),
    dry_run: bool = typer.Option(True, "--dry-run/--execute"),
    llm: bool = typer.Option(False, "--llm"),
    json_out: bool = typer.Option(False, "--json"),
    stdin: bool = typer.Option(False, "--stdin"),
) -> None:
    """Alias for ask with workflow bias."""
    if stdin:
        text = sys.stdin.read().strip()
        prompt = f"{prompt} {text}".strip() if prompt else text
    ask_cmd(prompt, dry_run=dry_run, llm=llm, json_out=json_out, out="")


@app.command("select")
def select_cmd(
    path: str = typer.Argument(..., help="Dot path, e.g. data.text"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Extract value from stdin envelope for piping."""
    from urish.select import select_from_envelope

    envelope = json.loads(sys.stdin.read() or "{}")
    value = select_from_envelope(envelope, path)
    if json_out or isinstance(value, (dict, list)):
        typer.echo(json.dumps(value, ensure_ascii=False))
    else:
        typer.echo(str(value))


@app.command("shell")
def shell_cmd() -> None:
    """Interactive REPL for uri commands."""
    raise typer.Exit(run_repl(execute=execute_cli_argv))


@app.command("doctor")
def doctor_cmd(
    strict: bool = typer.Option(False, "--strict", help="Fail on artifact lifecycle/schema drift"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Check uri2run transports, uri3 doctor, and optional artifact gates."""
    from urish.backends.doctor import doctor_all

    result = doctor_all(strict=strict)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@app.command("shortcuts")
def shortcuts_cmd(json_out: bool = typer.Option(False, "--json")) -> None:
    """List configured URI shortcuts."""
    payload = {"ok": True, "shortcuts": load_shortcut_specs(), "result_type": "shortcuts"}
    _emit(payload, output="json" if json_out else "yaml", quiet=False, json_out=json_out)


@app.command("proof")
def proof_cmd(
    target: str = typer.Argument(..., help="URI to prove across CLI/API/runtime/view layers"),
    json_out: bool = typer.Option(False, "--json"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Force non-mutating proof call"),
) -> None:
    """Show whether one URI works through the Taskinity control plane."""
    from urish.backends.proof import proof_uri, render_proof_text

    result = proof_uri(target, dry_run=dry_run)
    if json_out:
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        typer.echo(render_proof_text(result))
    _finish(result)


@context_app.command("list")
def context_list_cmd() -> None:
    for item in list_contexts():
        typer.echo(item)


@context_app.command("show")
def context_show_cmd(context_id: str = typer.Argument("")) -> None:
    import yaml

    typer.echo(yaml.safe_dump(load_context(context_id or None), sort_keys=False))


@context_app.command("use")
def context_use_cmd(context_id: str) -> None:
    os.environ[CONTEXT_ENV] = context_id
    typer.echo(f"context: {context_id}")


app.add_typer(context_app, name="context")


_KNOWN_COMMANDS = frozenset(
    {
        "call",
        "explain",
        "plan",
        "run",
        "logs",
        "watch",
        "stream",
        "ask",
        "nl",
        "select",
        "shell",
        "doctor",
        "shortcuts",
        "proof",
        "agent",
        "dashboard",
        "www",
        "ecosystem",
        "context",
        "environments",
        "ticket",
        "repair",
        "evolve",
        "proposal",
        "help",
        "--help",
        "-h",
    }
)


def _normalize_argv(argv: list[str]) -> list[str]:
    if not argv:
        return argv
    first = argv[0]
    if first in _KNOWN_COMMANDS or first.startswith("-"):
        return argv
    if "://" in first:
        return ["call", *argv]
    try:
        if first in load_shortcuts():
            return ["call", *argv]
    except Exception:  # noqa: BLE001
        pass
    return argv


def execute_cli_argv(argv: list[str]) -> int:
    """Run one uri subcommand (used by REPL and tests)."""
    try:
        normalized = _normalize_argv(list(argv))
        if not normalized:
            return 0
        app(prog_name="uri", args=normalized, standalone_mode=False)
        return 0
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, str):
            return 1
        return int(code)
    except typer.Exit as exc:
        code = getattr(exc, "exit_code", None) or getattr(exc, "code", 0)
        return int(code or 0)


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    if not argv:
        return run_repl(execute=execute_cli_argv)
    return execute_cli_argv(argv)


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from typing import Any

import typer

from uri3.config.cli_shortcuts import cli_examples, resolve_scan_target, scan_shortcuts
from uri3.graph.uri_graph import build_graph_from_tree
from uri3.logs.reader import read_logs_result, summarize_logs
from uri3.protocols.scheme_registry import analyze_uri, describe_uri, list_schemes
from uri3.resolvers.router import Uri3Router
from uri3.scanner.scanner import scan as scan_uri
from uri3.validators.uri_tree_validator import validate_uri_tree
from uri3.validators.uri_validator import validate_uri

app = typer.Typer(
    help="uri3: URI discovery, graph, validation and routing",
    no_args_is_help=False,
)


def _quick_reference() -> str:
    shortcuts = scan_shortcuts()
    scan_lines = "\n".join(f"  {name:<8} {uri}" for name, uri in shortcuts.items()) or "  (none — edit config/uri3.uri.yaml)"
    examples = cli_examples() or [
        "uri3 list",
        "uri3 scan http",
        "uri3 scan --all",
        "uri3 schema ssh://",
    ]
    example_lines = "\n".join(f"  {line}" for line in examples)
    return f"""uri3 — quick reference

Discovery:
  uri3 list              schemes, shortcuts, examples
  uri3 schema --list     URI schemes (same as: uri3 list --schemes)

Scan (use a name or full URI):
{scan_lines}

  uri3 scan http         scan shortcut by name
  uri3 scan <uri>        scan full URI
  uri3 scan --all        run every configured scan shortcut

Actions:
  uri3 resolve <uri>     resolve URI to structured payload
  uri3 call <uri>        execute docker://, python://, log:// actions
  uri3 validate <uri>    validate URI syntax
  uri3 logs 'log://...'  read filtered logs

Examples:
{example_lines}
"""


def _list_payload(*, schemes_only: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {"schemes": list_schemes()}
    if schemes_only:
        return payload
    payload["shortcuts"] = {"scan": scan_shortcuts()}
    payload["examples"] = cli_examples()
    payload["commands"] = [
        {"name": "list", "summary": "Show schemes, scan shortcuts, and examples"},
        {"name": "scan", "summary": "Probe http/ssh/docker; use shortcut name or full URI"},
        {"name": "schema", "summary": "Describe a scheme or URI (alias: uri3 list --schemes)"},
        {"name": "resolve", "summary": "Resolve URI to structured payload"},
        {"name": "call", "summary": "Execute callable URI actions"},
        {"name": "validate", "summary": "Validate URI syntax"},
        {"name": "logs", "summary": "Read filtered logs via log:// URI"},
        {"name": "graph", "summary": "Build dependency graph from URI tree YAML"},
    ]
    return payload


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(_quick_reference())
        raise typer.Exit(0)


@app.command()
def list_cmd(
    schemes: bool = typer.Option(False, "--schemes", help="Show only URI schemes"),
    json_out: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    """List schemes, scan shortcuts, and common examples."""
    payload = _list_payload(schemes_only=schemes)
    if json_out:
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    if schemes:
        for item in payload["schemes"]:
            typer.echo(f"{item['scheme']:<10} {item.get('summary', '')}")
        return
    typer.echo(_quick_reference())


app.command("list", help="List schemes, scan shortcuts, and common examples")(list_cmd)


@app.command()
def validate(uri: str) -> None:
    validate_uri(uri)
    typer.echo("OK")


@app.command("validate-tree")
def validate_tree(path: str) -> None:
    errors = validate_uri_tree(path)
    if errors:
        for error in errors:
            typer.echo(error)
        raise typer.Exit(1)
    typer.echo("OK")


@app.command()
def graph(path: str) -> None:
    graph_obj = build_graph_from_tree(path)
    typer.echo(
        json.dumps(
            {
                "nodes": [node.__dict__ for node in graph_obj.nodes.values()],
                "edges": [edge.__dict__ for edge in graph_obj.edges],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


@app.command()
def resolve(uri: str) -> None:
    result = Uri3Router().resolve(uri)
    typer.echo(json.dumps(result if isinstance(result, dict) else getattr(result, "__dict__", str(result)), indent=2, ensure_ascii=False))


@app.command()
def call(uri: str) -> None:
    """Execute a callable URI action (docker://, python://, log://)."""
    result = Uri3Router().call(uri)
    typer.echo(json.dumps(result if isinstance(result, dict) else getattr(result, "__dict__", str(result)), indent=2, ensure_ascii=False))


@app.command()
def scan(
    target: str = typer.Argument("", help="Shortcut name (http, ssh, docker) or full URI"),
    all_shortcuts: bool = typer.Option(False, "--all", help="Run all configured scan shortcuts"),
) -> None:
    if all_shortcuts:
        shortcuts = scan_shortcuts()
        if not shortcuts:
            typer.echo("No scan shortcuts configured. Edit config/uri3.uri.yaml")
            raise typer.Exit(1)
        payload = {name: [item.__dict__ for item in scan_uri(uri)] for name, uri in shortcuts.items()}
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    if not target:
        typer.echo(_quick_reference())
        typer.echo("\nTip: run `uri3 scan http` or `uri3 scan --all`")
        raise typer.Exit(1)
    try:
        uri = resolve_scan_target(target)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1) from exc
    typer.echo(json.dumps([item.__dict__ for item in scan_uri(uri)], indent=2, ensure_ascii=False))


@app.command()
def logs(
    uri: str,
    summary: bool = typer.Option(False, "--summary", help="Return aggregate counts instead of entries"),
) -> None:
    """Read and filter logs via log:// URI."""
    payload = summarize_logs(uri) if summary else read_logs_result(uri)
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))


@app.command()
def schema(
    target: str = typer.Argument("", help="Scheme (log://) or concrete URI to analyze"),
    list_all: bool = typer.Option(False, "--list", "-l", help="List supported schemes"),
    analyze: bool = typer.Option(False, "--analyze", help="Force full URI analysis"),
) -> None:
    """Describe URI format, options, and API for a scheme or concrete URI."""
    if list_all or not target:
        payload = {"schemes": list_schemes()}
    elif analyze:
        payload = analyze_uri(target)
    else:
        payload = describe_uri(target)
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> None:
    app()


if __name__ == "__main__":
    main()

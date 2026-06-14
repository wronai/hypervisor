import json, typer
from uri3.logs.reader import read_logs, summarize_logs
from uri3.validators.uri_validator import validate_uri
from uri3.validators.uri_tree_validator import validate_uri_tree
from uri3.graph.uri_graph import build_graph_from_tree
from uri3.scanner.scanner import scan as scan_uri
from uri3.resolvers.router import Uri3Router
app = typer.Typer(help="uri3: URI discovery, graph, validation and routing")

@app.command()
def validate(uri: str):
    validate_uri(uri); typer.echo("OK")

@app.command("validate-tree")
def validate_tree(path: str):
    errors = validate_uri_tree(path)
    if errors:
        for e in errors: typer.echo(e)
        raise typer.Exit(1)
    typer.echo("OK")

@app.command()
def graph(path: str):
    g = build_graph_from_tree(path)
    typer.echo(json.dumps({"nodes":[n.__dict__ for n in g.nodes.values()],"edges":[e.__dict__ for e in g.edges]}, indent=2, ensure_ascii=False))

@app.command()
def resolve(uri: str):
    result = Uri3Router().resolve(uri)
    typer.echo(json.dumps(result if isinstance(result, dict) else getattr(result, "__dict__", str(result)), indent=2, ensure_ascii=False))

@app.command()
def scan(uri: str):
    typer.echo(json.dumps([i.__dict__ for i in scan_uri(uri)], indent=2, ensure_ascii=False))

@app.command()
def logs(
    uri: str,
    summary: bool = typer.Option(False, "--summary", help="Return aggregate counts instead of entries"),
):
    """Read and filter logs via log:// URI."""
    payload = summarize_logs(uri) if summary else read_logs(uri)
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))

def main(): app()
if __name__ == "__main__": main()

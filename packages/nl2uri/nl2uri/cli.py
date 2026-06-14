import json
import yaml
import typer

from nl2uri.domain_planner import plan_from_prompt
from nl2uri.writer import write_uri_tree
from uri3.validators.uri_tree_validator import validate_uri_tree

app = typer.Typer(help="nl2uri: natural language -> URI Tree")


@app.command()
def generate(
    prompt: str = typer.Option(..., "-p", "--prompt"),
    out: str = typer.Option("", "--out"),
    no_llm: bool = typer.Option(False, "--no-llm"),
    json_out: bool = typer.Option(False, "--json"),
):
    tree = plan_from_prompt(prompt, use_llm=not no_llm)
    if out:
        path = write_uri_tree(tree, out)
        errors = validate_uri_tree(path)
        if errors:
            typer.echo("URI Tree validation failed:", err=True)
            for error in errors:
                typer.echo(error, err=True)
            raise typer.Exit(1)
        typer.echo(str(path))
        return
    typer.echo(
        json.dumps(tree, indent=2, ensure_ascii=False)
        if json_out
        else yaml.safe_dump(tree, sort_keys=False, allow_unicode=True)
    )


def main():
    app()


if __name__ == "__main__":
    main()

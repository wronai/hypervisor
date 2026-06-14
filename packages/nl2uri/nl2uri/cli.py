import json, yaml, typer
from nl2uri.planner import rule_based_plan
from nl2uri.llm_planner import llm_plan
from nl2uri.writer import write_uri_tree
app = typer.Typer(help="nl2uri: natural language -> URI Tree")

@app.command()
def generate(prompt: str = typer.Option(..., "-p", "--prompt"), out: str = typer.Option("", "--out"), no_llm: bool = typer.Option(False, "--no-llm"), json_out: bool = typer.Option(False, "--json")):
    result = rule_based_plan(prompt) if no_llm else llm_plan(prompt)
    if out:
        write_uri_tree(result.tree, out); typer.echo(out)
    else:
        typer.echo(json.dumps(result.tree, indent=2, ensure_ascii=False) if json_out else yaml.safe_dump(result.tree, sort_keys=False, allow_unicode=True))

def main(): app()
if __name__ == "__main__": main()

from pathlib import Path
import typer
from nl2uri.planner import rule_based_plan
from nl2uri.llm_planner import llm_plan
from nl2uri.writer import write_uri_tree
from hypervisor.domain_pack.generator import generate_domain_pack
app = typer.Typer(help="nl2a: natural language -> URI Tree -> Domain Pack -> Agent contract")

@app.command()
def generate(prompt: str = typer.Option(..., "-p", "--prompt"), no_llm: bool = False, out_dir: str = "domains"):
    plan = rule_based_plan(prompt) if no_llm else llm_plan(prompt)
    domain_dir = Path(out_dir) / plan.tree["domain"]["id"]
    tree_path = domain_dir / "uri_tree.yaml"
    write_uri_tree(plan.tree, tree_path)
    generate_domain_pack(tree_path, domain_dir)
    typer.echo(str(domain_dir))

def main(): app()
if __name__ == "__main__": main()

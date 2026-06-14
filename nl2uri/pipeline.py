from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from hypervisor.domain_pack.generator import generate_domain_pack
from nl2uri.domain_planner import plan_from_prompt
from nl2uri.writer import write_uri_tree
from uri3.validators.uri_tree_validator import validate_uri_tree


@dataclass
class PipelineResult:
    domain_dir: Path
    tree_path: Path
    files: dict[str, str]


def generate_tree(prompt: str, *, no_llm: bool = False) -> dict:
    return plan_from_prompt(prompt, use_llm=not no_llm)


def run_generate_pipeline(
    prompt: str,
    *,
    no_llm: bool = False,
    out_dir: str = "domains",
) -> PipelineResult:
    tree = generate_tree(prompt, no_llm=no_llm)
    domain_dir = Path(out_dir) / tree["domain"]["id"]
    tree_path = write_uri_tree(tree, domain_dir / "uri_tree.yaml")

    errors = validate_uri_tree(tree_path)
    if errors:
        raise ValueError("URI Tree validation failed: " + "; ".join(errors))

    files = generate_domain_pack(tree_path, domain_dir)
    return PipelineResult(domain_dir=domain_dir, tree_path=Path(tree_path), files=files)

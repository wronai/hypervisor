from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from jinja2 import Environment, FileSystemLoader

from generator.hashutil import file_sha256
from generator.model import AgentSpec, load_agent_spec, spec_to_plain_dict
from generator.validate import validate_agent

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "generator" / "templates"
OUTPUT_ROOT = ROOT / "agents" / "generated"


def render_template(env: Environment, template_name: str, dest: Path, context: dict) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    rendered = env.get_template(template_name).render(**context)
    dest.write_text(rendered, encoding="utf-8")


def generate_agent(spec_path: Path) -> Path:
    errors = validate_agent(spec_path)
    if errors:
        raise ValueError("\n".join(errors))

    spec: AgentSpec = load_agent_spec(spec_path)
    contract_hash = file_sha256(spec_path)
    output_dir = OUTPUT_ROOT / spec.output_dir_name
    env = Environment(loader=FileSystemLoader(TEMPLATES), trim_blocks=True, lstrip_blocks=True)

    context = {
        "spec": spec,
        "contract_hash": contract_hash,
        "agent_card": spec_to_plain_dict(spec, contract_hash),
        "capability_names": [cap.name for cap in spec.capabilities],
    }

    files = {
        "__init__.py.j2": output_dir / "__init__.py",
        "main.py.j2": output_dir / "main.py",
        "routes.py.j2": output_dir / "routes.py",
        "agent_card.py.j2": output_dir / "agent_card.py",
        "Dockerfile.j2": output_dir / "Dockerfile",
        "README.md.j2": output_dir / "README.md",
        "test_contract.py.j2": output_dir / "tests" / "test_contract.py",
    }
    for template, destination in files.items():
        render_template(env, template, destination, context)

    return output_dir


def expand_paths(patterns: Iterable[str]) -> list[Path]:
    result: list[Path] = []
    for pattern in patterns:
        matches = sorted(Path().glob(pattern))
        if matches:
            result.extend(matches)
        else:
            path = Path(pattern)
            if path.exists():
                result.append(path)
    return result


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        argv = ["contracts/agents/*.yaml"]
    paths = expand_paths(argv)
    if not paths:
        print("No agent specs matched.")
        return 1
    for path in paths:
        output_dir = generate_agent(path)
        print(f"Generated {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

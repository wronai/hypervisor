from __future__ import annotations

from pathlib import Path

from generator.paths import project_root

AUTO_GENERATED_MARKER = "AUTO-GENERATED FILE. DO NOT EDIT."
GENERATOR_NAME = "resource-agent-factory"


def contract_source_ref(spec_path: Path, root: Path | None = None) -> str:
    """Return a stable repo-relative contract path for generated headers."""
    base = (root or project_root()).resolve()
    resolved = spec_path.expanduser().resolve()
    try:
        return resolved.relative_to(base).as_posix()
    except ValueError:
        return resolved.as_posix()


def python_file_header(source_ref: str, contract_hash: str) -> str:
    return (
        f"# {AUTO_GENERATED_MARKER}\n"
        f"# Source: {source_ref}\n"
        f"# Contract hash: {contract_hash}\n\n"
    )


def dockerfile_header(source_ref: str, contract_hash: str) -> str:
    return (
        f"# {AUTO_GENERATED_MARKER}\n"
        f"# Source: {source_ref}\n"
        f"# Contract hash: {contract_hash}\n"
    )


def markdown_generated_banner(source_ref: str, contract_hash: str) -> str:
    return (
        f"<!-- {AUTO_GENERATED_MARKER} -->\n"
        f"<!-- Source: {source_ref} -->\n"
        f"<!-- Contract hash: {contract_hash} -->\n"
    )


def generated_marker_payload(source_ref: str, contract_hash: str) -> dict[str, str]:
    return {
        "auto_generated": "true",
        "source": source_ref,
        "contract_hash": contract_hash,
        "generator": GENERATOR_NAME,
        "generation_command": (
            "PYTHONPATH=packages/resource-agent-factory "
            f"python -m generator.agent_generator {source_ref}"
        ),
        "markpact_readme": "README.md",
    }

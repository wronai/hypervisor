from __future__ import annotations

from pathlib import Path
from typing import Any

from uri2pact.core import is_markpact_registry, load_markpact_markdown, parse_markpact_yaml_blocks


def _flow_blocks(
    markdown: str,
    readme_path: Path,
    *,
    fragment: str | None,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return parse_markpact_yaml_blocks(
        markdown,
        "flow",
        fragment=fragment,
        source=str(readme_path),
    )


def _require_flow_blocks(
    all_blocks: list[tuple[dict[str, Any], dict[str, Any]]],
    *,
    readme_path: Path,
) -> None:
    if not all_blocks:
        raise ValueError(f"No markpact:flow blocks found in {readme_path}")


def _require_fragment_match(
    matches: list[tuple[dict[str, Any], dict[str, Any]]],
    *,
    fragment: str | None,
    readme_path: Path,
) -> None:
    if fragment and not matches:
        raise ValueError(f"No markpact:flow block matching #{fragment} in {readme_path}")


def _require_unambiguous_flow(
    all_blocks: list[tuple[dict[str, Any], dict[str, Any]]],
    *,
    fragment: str | None,
    readme_path: Path,
) -> None:
    if not fragment and len(all_blocks) > 1:
        raise ValueError(
            f"Multiple markpact:flow blocks in {readme_path}; specify #flow.id fragment"
        )


def _select_flow_block(
    all_blocks: list[tuple[dict[str, Any], dict[str, Any]]],
    matches: list[tuple[dict[str, Any], dict[str, Any]]],
    *,
    fragment: str | None,
    readme_path: Path,
) -> dict[str, Any]:
    _require_flow_blocks(all_blocks, readme_path=readme_path)
    _require_fragment_match(matches, fragment=fragment, readme_path=readme_path)
    _require_unambiguous_flow(all_blocks, fragment=fragment, readme_path=readme_path)
    return (matches or all_blocks)[0][1]


def load_markpact_flow_dict(
    ref: str | Path,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    """Load compact flow YAML from ``markpact://path/to/README.md[#flow.id]``."""
    readme_path, fragment, markdown = load_markpact_markdown(ref, root=root)
    all_blocks = _flow_blocks(markdown, readme_path, fragment=None)
    matches = _flow_blocks(markdown, readme_path, fragment=fragment)
    return _select_flow_block(
        all_blocks,
        matches,
        fragment=fragment,
        readme_path=readme_path,
    )


is_markpact_flow_ref = is_markpact_registry
load_markpact_flow = load_markpact_flow_dict

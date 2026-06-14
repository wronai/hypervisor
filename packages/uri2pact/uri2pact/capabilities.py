from __future__ import annotations

from pathlib import Path
from typing import Any

from uri2pact.core import (
    load_markpact_markdown,
    parse_markpact_yaml_blocks,
)


def load_markpact_capability_dicts(
    ref: str | Path,
    *,
    root: Path | None = None,
) -> list[dict[str, Any]]:
    """Load raw capability YAML dicts from markpact README blocks."""
    readme_path, fragment, markdown = load_markpact_markdown(ref, root=root)
    matches = parse_markpact_yaml_blocks(
        markdown,
        "capability",
        fragment=fragment,
        source=str(readme_path),
    )
    if fragment and not matches:
        raise ValueError(f"No markpact:capability block matching #{fragment} in {readme_path}")
    if not matches:
        raise ValueError(f"No markpact:capability blocks found in {readme_path}")
    return [data for _block, data in matches]

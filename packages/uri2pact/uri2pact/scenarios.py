from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from uri2pact.core import find_repo_root, load_markpact_markdown, parse_markpact_yaml_blocks


def _scenario_body(data: dict[str, Any]) -> dict[str, Any]:
    nested = data.get("scenario")
    if isinstance(nested, dict):
        return nested
    return data


def load_markpact_scenario_dicts(
    ref: str | Path,
    *,
    root: Path | None = None,
    fragment: str | None = None,
) -> list[dict[str, Any]]:
    """Load ``markpact:scenario`` blocks from a README."""
    readme_path, frag, markdown = load_markpact_markdown(ref, root=root)
    use_fragment = fragment if fragment is not None else frag
    matches = parse_markpact_yaml_blocks(
        markdown,
        "scenario",
        fragment=use_fragment,
        source=str(readme_path),
    )
    if use_fragment and not matches:
        raise ValueError(f"No markpact:scenario block matching #{use_fragment} in {readme_path}")
    return [_scenario_body(data) for _meta, data in matches]


def _resolve_include_path(include: str | Path, readme_path: Path, root: Path | None) -> Path:
    p = Path(str(include))
    if p.is_absolute():
        return p
    base = root or find_repo_root(readme_path.parent)
    return base / p


def _merge_include_data(data: dict[str, Any], loaded: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(loaded, dict):
        return data
    # loaded is base, explicit data overrides except the "include" key
    merged = {**loaded, **{k: v for k, v in data.items() if k != "include"}}
    return merged


def _ensure_urish_scenario_registry_kind(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("kind") != "urish.scenario_registry":
        return {**data, "kind": "urish.scenario_registry"}
    return data


def load_markpact_scenario_registry_dicts(
    ref: str | Path,
    *,
    root: Path | None = None,
    fragment: str | None = None,
) -> list[dict[str, Any]]:
    """Load ``markpact:scenario_registry`` blocks (``kind: urish.scenario_registry``)."""
    readme_path, frag, markdown = load_markpact_markdown(ref, root=root)
    use_fragment = fragment if fragment is not None else frag
    matches = parse_markpact_yaml_blocks(
        markdown,
        "scenario_registry",
        fragment=use_fragment,
        source=str(readme_path),
    )
    if use_fragment and not matches:
        raise ValueError(
            f"No markpact:scenario_registry block matching #{use_fragment} in {readme_path}"
        )
    registries: list[dict[str, Any]] = []
    for _meta, data in matches:
        if not isinstance(data, dict):
            continue
        include = data.get("include")
        if include:
            inc_path = _resolve_include_path(include, readme_path, root)
            if inc_path.is_file():
                loaded = yaml.safe_load(inc_path.read_text(encoding="utf-8")) or {}
                data = _merge_include_data(data, loaded)
        data = _ensure_urish_scenario_registry_kind(data)
        registries.append(data)
    return registries


load_markpact_scenario_registry = load_markpact_scenario_registry_dicts

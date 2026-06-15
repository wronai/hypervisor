from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import yaml

_ID_BLOCK_BY_TYPE = {
    "capability": "capability",
    "flow": "flow",
}

MARKPACT_BLOCK_RE = re.compile(
    r"```(?:\w+\s+)?markpact:(?P<kind>\w+)(?:[ \t]+(?P<meta>[^\n]*))?\n(?P<body>[\s\S]*?)\n```",
    re.MULTILINE,
)


def is_markpact_registry(ref: str | Path) -> bool:
    s = str(ref)
    return s.startswith("markpact://") or s.startswith("file://")


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for path in (current, *current.parents):
        if (path / "pyproject.toml").is_file() and (path / "examples").is_dir():
            return path
    return current


def resolve_markpact_ref(ref: str | Path, *, root: Path | None = None) -> tuple[Path, str | None]:
    raw = str(ref)
    if not is_markpact_registry(raw):
        # Allow plain paths to .md files that contain markpact blocks (convenience)
        p = Path(raw)
        if p.suffix in (".md", ".markdown") and p.exists():
            resolved = p.resolve()
            return resolved, None
        raise ValueError(f"Not a markpact registry URI or markdown file: {raw}")

    # Normalize: support both "file:///path/README.md#frag" and "markpact://file:///path/README.md#frag"
    if raw.startswith("file://") or (raw.startswith("markpact://") and "file://" in raw):
        target = raw
        if target.startswith("markpact://"):
            target = target[len("markpact://") :]
        # Parse file URI + optional fragment
        if "#" in target:
            file_part, fragment = target.split("#", 1)
            fragment = fragment.strip() or None
        else:
            file_part, fragment = target, None
        path = _path_from_file_uri(file_part)
    else:
        # Classic markpact://<relative-or-abs-path>[#frag]
        raw_path, fragment = _split_markpact_target(raw)
        path = _resolve_markpact_path(raw_path, root=root)
        if fragment:
            fragment = fragment.strip()

    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"markpact README not found: {resolved} (from {raw})")
    return resolved, fragment


def _split_markpact_target(ref: str) -> tuple[str, str | None]:
    target = ref[len("markpact://") :]
    if "#" in target:
        raw_path, fragment = target.split("#", 1)
        return raw_path, fragment
    return target, None


def _path_from_file_uri(uri: str) -> Path:
    """Convert file:// URI (or markpact://file://...) to Path, handling unquoting."""
    if uri.startswith("markpact://"):
        uri = uri[len("markpact://"):]
    if not uri.startswith("file://"):
        # fallback
        return Path(unquote(uri.strip()))
    path_str = uri[7:]
    # Handle windows file:///c:/... etc by stripping leading /
    if path_str.startswith("/") and len(path_str) > 2 and path_str[2] == ":":
        path_str = path_str[1:]
    return Path(unquote(path_str))


def _resolve_markpact_path(raw_path: str, *, root: Path | None) -> Path:
    if raw_path.startswith("file://"):
        return _path_from_file_uri(raw_path)
    path = Path(unquote(raw_path.strip()))
    if path.is_absolute():
        return path
    return (root or find_repo_root()) / path


def extract_markpact_blocks(markdown: str, block_type: str) -> list[dict[str, Any]]:
    """Parse fenced ``markpact:<block_type>`` blocks from markdown."""
    blocks: list[dict[str, Any]] = []
    for match in MARKPACT_BLOCK_RE.finditer(markdown):
        kind = match.group("kind")
        if kind != block_type:
            continue
        meta = (match.group("meta") or "").strip()
        body = match.group("body").strip()
        blocks.append({"kind": kind, "meta": meta, "body": body})
    return blocks


def load_markpact_markdown(
    ref: str | Path, *, root: Path | None = None
) -> tuple[Path, str | None, str]:
    readme_path, fragment = resolve_markpact_ref(ref, root=root)
    return readme_path, fragment, readme_path.read_text(encoding="utf-8")


def parse_markpact_yaml_blocks(
    markdown: str,
    block_type: str,
    *,
    fragment: str | None = None,
    source: str = "",
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Return ``(block_meta, parsed_yaml)`` pairs matching optional fragment."""
    matches: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for block in extract_markpact_blocks(markdown, block_type):
        data = _parse_block_yaml(block, block_type, source=source)
        block_id = _block_id(block, data, block_type)
        meta_id = (block.get("meta") or "").strip()
        if not _matches_fragment(fragment, block_id, meta_id):
            continue
        matches.append((block, data))
    return matches


def _parse_block_yaml(
    block: dict[str, Any],
    block_type: str,
    *,
    source: str,
) -> dict[str, Any]:
    data = yaml.safe_load(block["body"]) or {}
    if isinstance(data, dict):
        return data
    raise ValueError(
        f"Expected YAML mapping in markpact:{block_type} block ({source or block_type})"
    )


def _matches_fragment(fragment: str | None, block_id: str, meta_id: str) -> bool:
    return not fragment or block_id == fragment or meta_id == fragment


def _typed_block_id(data: dict[str, Any], block_type: str) -> str | None:
    block_key = _ID_BLOCK_BY_TYPE.get(block_type)
    value = data.get(block_key) if block_key else None
    if isinstance(value, dict) and value.get("id"):
        return str(value["id"])
    return None


def _block_id(block: dict[str, Any], data: dict[str, Any], block_type: str) -> str:
    typed_id = _typed_block_id(data, block_type)
    if typed_id:
        return typed_id
    if block.get("meta"):
        return str(block["meta"])
    raise ValueError(f"markpact:{block_type} block missing id and meta id")

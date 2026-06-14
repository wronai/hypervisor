from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """Locate monorepo root by shared contract/schema markers."""
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for path in (current, *current.parents):
        if (path / "contracts").is_dir() and (path / "schemas").is_dir():
            return path
    raise FileNotFoundError("Repository root not found (expected contracts/ and schemas/)")


def repo_root() -> Path:
    return find_repo_root()

from __future__ import annotations

from pathlib import Path


def repo_www_dir() -> Path | None:
    """Return repo-root www/ when running inside the hypervisor workspace."""
    try:
        from uri3.paths import find_repo_root

        www = find_repo_root() / "www"
        return www if www.is_dir() else None
    except Exception:  # noqa: BLE001
        return None

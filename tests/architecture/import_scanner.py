"""Architecture import boundary scanner — delegates to uri3.doctor.boundary_scanner."""

from __future__ import annotations

from pathlib import Path

from uri3.doctor.boundary_scanner import load_boundary_rules, scan_package_boundaries


def repo_root_from_here() -> Path:
    from uri3.config.repo_root import find_repo_root

    return find_repo_root()


__all__ = ["load_boundary_rules", "repo_root_from_here", "scan_package_boundaries"]

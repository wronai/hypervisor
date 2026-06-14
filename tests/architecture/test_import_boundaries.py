"""Architecture: package import boundaries."""

from __future__ import annotations

from tests.architecture.import_scanner import scan_package_boundaries


def test_forbidden_imports():
    violations = scan_package_boundaries()
    assert not violations, "import boundary violations:\n" + "\n".join(violations)

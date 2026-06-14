"""Architecture: uri3 doctor contract."""

from __future__ import annotations

from pathlib import Path

from uri3.doctor.runner import run_doctor

REQUIRED_CHECKS = frozenset(
    {
        "config",
        "contract_registry",
        "touri.registry",
        "uri2ops.registry",
        "explain.smoke",
        "envelope.exports",
        "envelope.recent_logs",
        "boundaries.imports",
        "imports.package_roots",
        "imports.legacy_top_level",
        "runtime.browser_delegation",
        "runtime.uri2run_transports",
    }
)


def test_doctor_contract(repo_root: Path):
    payload = run_doctor(root=repo_root)
    assert payload["ok"] is True
    check_ids = {item["id"] for item in payload["checks"]}
    missing = REQUIRED_CHECKS - check_ids
    assert not missing, f"missing doctor checks: {sorted(missing)}"

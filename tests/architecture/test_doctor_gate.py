"""Architecture: uri3 doctor must pass on the repo (CI gate)."""

from __future__ import annotations

from pathlib import Path

from uri3.doctor.runner import run_doctor


def test_uri3_doctor_gate(repo_root: Path):
    payload = run_doctor(root=repo_root)
    failed = [item["id"] for item in payload.get("checks") or [] if not item.get("ok")]
    assert payload.get("ok") is True, f"uri3 doctor failed checks: {failed}"

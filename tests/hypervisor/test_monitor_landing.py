"""Tests for www landing monitor script."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_monitor(*args: str, repo_root: Path) -> subprocess.CompletedProcess[str]:
    script = repo_root / "scripts" / "www" / "monitor_landing.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_monitor_detects_unreachable_url(repo_root: Path):
    result = _run_monitor("--url", "http://127.0.0.1:1/www/", repo_root=repo_root)
    assert result.returncode == 1
    assert "PAGE_DOWN" in result.stdout


def test_monitor_baseline_and_unchanged_prices(repo_root: Path):
    baseline = repo_root / "output" / "monitoring" / "www-prices-test.json"
    if baseline.exists():
        baseline.unlink()

    created = _run_monitor(
        "--url",
        "http://localhost:8788/www/",
        "--baseline",
        str(baseline),
        "--reset-baseline",
        repo_root=repo_root,
    )
    assert created.returncode == 0
    assert baseline.exists()

    ok = _run_monitor(
        "--url",
        "http://localhost:8788/www/",
        "--baseline",
        str(baseline),
        repo_root=repo_root,
    )
    assert ok.returncode == 0
    assert "OK" in ok.stdout


def test_monitor_detects_price_change(repo_root: Path, tmp_path: Path):
    baseline = tmp_path / "prices.json"
    baseline.write_text(
        json.dumps({"prices": ["OLD PRICE"]}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    result = _run_monitor(
        "--url",
        "http://localhost:8788/www/",
        "--baseline",
        str(baseline),
        "--notify",
        repo_root=repo_root,
    )
    assert result.returncode == 2
    assert "PRICE_CHANGED" in result.stdout

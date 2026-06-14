"""Tests for www URL/uptime monitors and webhook delivery."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_WWW = Path(__file__).resolve().parents[2] / "scripts" / "www"


def _run(script: str, *args: str, repo_root: Path, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    import os

    merged = {**os.environ, **(env or {})}
    return subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "www" / script), *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
        env=merged,
    )


def test_monitor_url_ok(repo_root: Path):
    result = _run(
        "monitor_url.py",
        "--url",
        "http://localhost:8788/health",
        "--contains",
        "hypervisor-dashboard",
        repo_root=repo_root,
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_monitor_url_down(repo_root: Path):
    result = _run(
        "monitor_url.py",
        "--url",
        "http://127.0.0.1:1/health",
        "--notify",
        repo_root=repo_root,
    )
    assert result.returncode == 1
    assert "PAGE_DOWN" in result.stdout
    assert "[NOTIFY]" in result.stderr


def test_baseline_created_does_not_post_webhook():
    posted: list[dict] = []

    def fake_urlopen(req, timeout=10.0):  # noqa: ARG001
        posted.append(json.loads(req.data.decode("utf-8")))
        return type("Resp", (), {"status": 200, "__enter__": lambda s: s, "__exit__": lambda *a: None})()

    sys.path.insert(0, str(SCRIPTS_WWW))
    import monitor_notify

    with patch.object(monitor_notify.urllib.request, "urlopen", fake_urlopen):
        monitor_notify.emit_alert(
            "BASELINE_CREATED",
            "BASELINE_CREATED prices=['x']",
            notify=True,
            webhook="http://hook.test/alert",
        )

    assert not posted


def test_webhook_posts_on_price_change():
    posted: list[dict] = []

    def fake_urlopen(req, timeout=10.0):  # noqa: ARG001
        posted.append(json.loads(req.data.decode("utf-8")))
        return type("Resp", (), {"status": 200, "__enter__": lambda s: s, "__exit__": lambda *a: None})()

    sys.path.insert(0, str(SCRIPTS_WWW))
    import monitor_notify

    with patch.object(monitor_notify.urllib.request, "urlopen", fake_urlopen):
        monitor_notify.emit_alert(
            "PRICE_CHANGED",
            "PRICE_CHANGED old=['STALE'] new=['NEW']",
            url="http://localhost:8788/www/",
            notify=True,
            webhook="http://hook.test/alert",
            extra={"old_prices": ["STALE"], "prices": ["NEW"]},
        )

    assert posted
    assert posted[0]["event"] == "PRICE_CHANGED"
    assert posted[0]["prices"] == ["NEW"]


def test_placeholder_webhook_is_skipped(capsys: pytest.CaptureFixture[str]):
    def fail_urlopen(*_args, **_kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("placeholder webhook should not be posted")

    sys.path.insert(0, str(SCRIPTS_WWW))
    import monitor_notify

    with patch.object(monitor_notify.urllib.request, "urlopen", fail_urlopen):
        monitor_notify.emit_alert(
            "PRICE_CHANGED",
            "PRICE_CHANGED old=['STALE'] new=['NEW']",
            url="http://localhost:8788/www/",
            notify=True,
            webhook="https://twoja-instancja.app.n8n.cloud/webhook/abc123",
            extra={"old_prices": ["STALE"], "prices": ["NEW"]},
        )

    captured = capsys.readouterr()
    assert "[WEBHOOK_SKIPPED]" in captured.err
    assert "placeholder webhook URL" in captured.err


def test_monitor_landing_notify_on_price_change(repo_root: Path, tmp_path: Path):
    baseline = tmp_path / "prices.json"
    baseline.write_text(json.dumps({"prices": ["OLD"]}, ensure_ascii=False) + "\n", encoding="utf-8")
    result = _run(
        "monitor_landing.py",
        "--url",
        "http://localhost:8788/www/",
        "--baseline",
        str(baseline),
        "--notify",
        repo_root=repo_root,
    )
    assert result.returncode == 2
    assert "PRICE_CHANGED" in result.stdout
    assert "[NOTIFY]" in result.stderr

"""Fixtures for examples integration tests."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    root = Path(__file__).resolve().parents[2]
    assert (root / "pyproject.toml").is_file()
    assert (root / "examples").is_dir()
    return root


@pytest.fixture(scope="session")
def examples_env(repo_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    paths = [
        repo_root / "packages" / "resource-agent-factory",
        repo_root / "packages" / "resource-agent-hypervisor",
        repo_root / "packages" / "nl2uri",
        repo_root / "packages" / "uri3",
        repo_root / "packages" / "uri2flow",
        repo_root / "packages" / "uri2ops",
        repo_root / "packages" / "touri",
        repo_root / "packages" / "uri2voice",
        repo_root / "packages" / "uri2pact",
        repo_root / "packages" / "uri2run",
        repo_root / "packages" / "uri2verify",
        repo_root / "examples" / "21_touri_voice",
    ]
    prefix = os.pathsep.join(str(path) for path in paths if path.is_dir())
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{prefix}{os.pathsep}{existing}" if existing else prefix
    env.setdefault("LANG", "en_US.UTF-8")
    env.setdefault("LC_ALL", env["LANG"])
    return env


def run_shell(
    repo_root: Path,
    command: list[str],
    *,
    env: dict[str, str],
    timeout_s: int = 120,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout_s,
        check=False,
    )


def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    probe = subprocess.run(["docker", "info"], capture_output=True, timeout=30, check=False)
    return probe.returncode == 0


def playwright_available() -> bool:
    try:
        import playwright  # noqa: F401

        return True
    except ImportError:
        return False


def skip_if_markers(spec, repo_root: Path) -> None:
    if "docker" in spec.markers and not docker_available():
        pytest.skip("docker not available")
    if "playwright" in spec.markers and not playwright_available():
        pytest.skip("playwright not installed (pip install -e '.[browser]' && playwright install chromium)")

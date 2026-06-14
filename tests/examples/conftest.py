"""Fixtures for examples integration tests."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from tests.conftest import workspace_env


@pytest.fixture(scope="session")
def repo_root() -> Path:
    root = Path(__file__).resolve().parents[2]
    assert (root / "pyproject.toml").is_file()
    assert (root / "examples").is_dir()
    return root


@pytest.fixture(scope="session")
def examples_env(repo_root: Path) -> dict[str, str]:
    return workspace_env(repo_root)


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


def playwright_available(repo_root: Path | None = None) -> bool:
    if repo_root is not None:
        env = workspace_env(repo_root)
        python = shutil.which("python", path=env.get("PATH", ""))
        if python is None:
            return False
        probe = subprocess.run(
            [python, "-c", "import playwright.sync_api"],
            env=env,
            capture_output=True,
            timeout=30,
            check=False,
        )
        return probe.returncode == 0
    try:
        import playwright.sync_api  # noqa: F401

        return True
    except ImportError:
        return False


def skip_if_markers(spec, repo_root: Path) -> None:
    if "docker" in spec.markers and not docker_available():
        pytest.skip("docker not available")
    if "playwright" in spec.markers and not playwright_available(repo_root):
        pytest.skip(
            "playwright not installed "
            "(pip install -e '.[browser]' && playwright install chromium)"
        )

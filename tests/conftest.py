from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

CLI_MODULES: dict[str, str] = {
    "uri3": "uri3.cli",
    "touri": "touri.cli",
    "hypervisor": "hypervisor.cli",
    "urigen": "urigen.cli",
    "urish": "urish.cli",
    "uri2flow": "uri2flow.cli",
    "uri2ops": "uri2ops.cli",
    "uri2run": "uri2run.cli",
    "uri2verify": "uri2verify.cli",
    "nl2uri": "nl2uri.cli",
    "nl2a": "nl2a.cli",
}


@pytest.fixture(scope="session")
def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file() and (parent / "examples").is_dir():
            return parent
    raise RuntimeError("hypervisor repo root not found")


def workspace_pythonpath(repo_root: Path) -> str:
    paths = [
        repo_root,  # root for top-level like domains/ (for externalized domain planners etc.)
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
        repo_root / "packages" / "urigen",
        repo_root / "packages" / "urish",
        repo_root / "agents" / "system" / "hypervisor_dashboard",
        repo_root / "examples" / "21_touri_voice",
    ]
    prefix = os.pathsep.join(str(path) for path in paths if path.is_dir())
    existing = os.environ.get("PYTHONPATH", "")
    return f"{prefix}{os.pathsep}{existing}" if existing else prefix


def workspace_env(repo_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = workspace_pythonpath(repo_root)
    env.setdefault("LANG", "en_US.UTF-8")
    env.setdefault("LC_ALL", env["LANG"])
    bin_dirs = [Path(sys.executable).resolve().parent, repo_root / ".venv" / "bin"]
    prepend = os.pathsep.join(str(path) for path in bin_dirs if path.is_dir())
    if prepend:
        env["PATH"] = f"{prepend}{os.pathsep}{env.get('PATH', '')}"
    return env


def cli_argv(
    name: str,
    *args: str,
    env: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> list[str]:
    """Resolve a workspace console script for subprocess use."""
    candidates: list[Path] = []
    exe_parent = Path(sys.executable).parent
    if exe_parent.name == "bin":
        candidates.append(exe_parent / name)
    if repo_root is not None:
        candidates.append(repo_root / ".venv" / "bin" / name)
    search_path = (env or os.environ).get("PATH", "")
    for directory in search_path.split(os.pathsep):
        if directory:
            candidates.append(Path(directory) / name)
    for script in candidates:
        if script.is_file():
            return [str(script), *args]
    found = shutil.which(name, path=search_path or None)
    if found:
        return [found, *args]
    module = CLI_MODULES.get(name)
    if module:
        code = (
            "from __future__ import annotations; "
            "import importlib, inspect, sys; "
            f"main = getattr(importlib.import_module({module!r}), 'main'); "
            "result = main(sys.argv[1:]) if inspect.signature(main).parameters else main(); "
            "raise SystemExit(0 if result is None else result)"
        )
        return [sys.executable, "-c", code, *args]
    return [name, *args]


@pytest.fixture(scope="session")
def examples_env(repo_root: Path) -> dict[str, str]:
    return workspace_env(repo_root)

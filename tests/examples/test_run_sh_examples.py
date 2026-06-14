"""Run every examples/*/run.sh against the new architecture stack."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.examples.catalog import RUN_SH_EXAMPLES
from tests.examples.conftest import run_shell, skip_if_markers


@pytest.mark.examples
@pytest.mark.parametrize(
    "spec",
    RUN_SH_EXAMPLES,
    ids=lambda spec: f"{spec.id}_{spec.name}",
)
def test_example_run_sh(spec, repo_root: Path, examples_env):
    skip_if_markers(spec, repo_root)
    script = repo_root / spec.path
    assert script.is_file(), f"missing run.sh: {script}"
    result = run_shell(
        repo_root,
        ["bash", str(script)],
        env=examples_env,
        timeout_s=spec.timeout_s,
    )
    assert result.returncode == 0, (
        f"example {spec.id} failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

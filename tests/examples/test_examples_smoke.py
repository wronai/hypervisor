"""Static smoke checks: every catalogued example path exists."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests.examples.catalog import ALL_EXAMPLES, RUN_SH_EXAMPLES


@pytest.mark.examples
def test_examples_readme_lists_known_directories(repo_root: Path):
    readme = (repo_root / "examples" / "README.md").read_text(encoding="utf-8")
    for spec in RUN_SH_EXAMPLES:
        example_dir = spec.path.split("/")[1]
        assert example_dir in readme, f"{example_dir} missing from examples/README.md"


@pytest.mark.examples
@pytest.mark.parametrize("spec", RUN_SH_EXAMPLES, ids=lambda s: s.id)
def test_run_sh_script_exists(spec, repo_root: Path):
    path = repo_root / spec.path
    assert path.is_file(), str(path)


@pytest.mark.examples
def test_touri_capability_manifests_validate(repo_root: Path, examples_env):
    from tests.conftest import cli_argv
    from tests.examples.conftest import run_shell

    registry = repo_root / "examples/20_touri_capabilities"
    for manifest in sorted(registry.glob("*.uri.capability.yaml")):
        result = run_shell(
            repo_root,
            cli_argv("touri", "validate", str(manifest), env=examples_env, repo_root=repo_root),
            env=examples_env,
        )
        assert result.returncode == 0, manifest.name


@pytest.mark.examples
def test_workflow_graph_yaml_parseable(repo_root: Path):
    graphs = [
        repo_root / "examples/14_workflow_executor_mock/task_graph.yaml",
        repo_root / "examples/17_flow_vs_graph/weather.uri.flow.yaml",
    ]
    for path in graphs:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)


@pytest.mark.examples
def test_architecture_stack_imports():
    from uri2run import run_backend
    from uri3.doctor.runner import run_doctor
    from touri.executor import call_uri

    assert callable(run_backend)
    assert callable(run_doctor)
    assert callable(call_uri)


@pytest.mark.examples
def test_catalog_covers_all_run_sh(repo_root: Path):
    discovered = sorted(repo_root.glob("examples/*/run.sh"))
    catalog_paths = {str(repo_root / spec.path) for spec in ALL_EXAMPLES if spec.kind == "run_sh"}
    missing = [str(path) for path in discovered if str(path) not in catalog_paths]
    assert not missing, f"uncatalogued run.sh: {missing}"

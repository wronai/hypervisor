from __future__ import annotations

from pathlib import Path
from typing import Any

from urigen.io import load_yaml


def _repo_relative(path: Path, repo: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def build_apply_plan(
    ecosystem_path: str | Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    ecosystem_file = Path(ecosystem_path).resolve()
    ecosystem_dir = ecosystem_file.parent
    ecosystem = load_yaml(ecosystem_file)
    eco_meta = ecosystem.get("metadata") or ecosystem.get("ecosystem") or {}
    eco_id = str(eco_meta.get("id") or "generated-ecosystem")
    plan_id = f"apply_{eco_id}_001"

    actions: list[dict[str, Any]] = []
    for agent in ecosystem.get("agents") or []:
        contract = agent.get("contract")
        agent_name = str(agent.get("name") or agent.get("id") or "agent").replace("/", "_")
        if not contract:
            continue
        source = ecosystem_dir / contract
        if source.is_file():
            actions.append(
                {
                    "id": f"merge_agent_contract_{agent_name}",
                    "operation": "copy_file",
                    "source": _repo_relative(source, repo_root),
                    "target": contract,
                    "requires_approval": True,
                }
            )

    capabilities_dir = ecosystem_dir / "capabilities"
    if capabilities_dir.is_dir():
        actions.append(
            {
                "id": "copy_capabilities",
                "operation": "copy_dir",
                "source": _repo_relative(capabilities_dir, repo_root),
                "target": "examples/20_touri_capabilities/",
                "requires_approval": True,
            }
        )

    fragment = ecosystem_dir / "deployments" / "agent_deployments.fragment.yaml"
    if fragment.is_file():
        actions.append(
            {
                "id": "update_deployment_registry",
                "operation": "merge_yaml_list",
                "source": _repo_relative(fragment, repo_root),
                "target": "deployments/agent_deployments.yaml",
                "list_key": "deployments",
                "merge_key": "id",
                "requires_approval": True,
            }
        )

    tests_dir = ecosystem_dir / "tests"
    if tests_dir.is_dir():
        actions.append(
            {
                "id": "add_tests",
                "operation": "copy_dir",
                "source": _repo_relative(tests_dir, repo_root),
                "target": f"tests/ecosystems/{eco_id}/",
                "requires_approval": False,
            }
        )

    actions.append(
        {
            "id": "post_verify",
            "operation": "verify",
            "source": _repo_relative(ecosystem_file, repo_root),
            "target": "uri3 doctor",
            "requires_approval": False,
        }
    )

    return {
        "$schema": "schemas/apply_plan.schema.json",
        "apiVersion": "uri3.io/v1",
        "kind": "ApplyPlan",
        "metadata": {
            "id": plan_id,
            "created_by": "urigen://apply-planner",
        },
        "uri": {
            "self": f"apply://ecosystem/{eco_id}/plan",
            "ecosystem": f"ecosystem://{eco_id}",
        },
        "spec": {"actions": actions},
        "verification": {
            "before": [f"urigen verify {_repo_relative(ecosystem_file, repo_root)}"],
            "after": ["uri3 doctor"],
        },
    }

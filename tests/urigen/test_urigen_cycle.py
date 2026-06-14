from __future__ import annotations

from pathlib import Path

from urigen import (
    apply_ecosystem,
    explain_ecosystem,
    generate_ecosystem,
    plan_ecosystem,
    verify_ecosystem,
)
from urigen.cli import main as urigen_main
from urigen.io import write_yaml


def test_plan_generate_verify_explain_cycle(tmp_path: Path):
    proposal = plan_ecosystem(
        "stworz agenta pogodowego z TTS i healthcheckiem",
        profile="voice",
    )
    proposal_path = write_yaml(tmp_path / "proposal.yaml", proposal)

    generated = generate_ecosystem(proposal_path, out=tmp_path / "ecosystem")
    assert generated["ok"] is True
    ecosystem_path = Path(generated["ecosystem_file"])
    assert ecosystem_path.is_file()
    assert (ecosystem_path.parent / "README.md").is_file()
    assert (
        ecosystem_path.parent / "capabilities" / "weather_forecast.uri.capability.yaml"
    ).is_file()
    voice_flow = ecosystem_path.parent / "flows" / "voice_command_health.uri.flow.yaml"
    assert voice_flow.is_file()

    verification = verify_ecosystem(ecosystem_path)
    assert verification["ok"] is True
    assert (ecosystem_path.parent / "verify_report.json").is_file()

    explanation = explain_ecosystem(ecosystem_path)
    assert explanation["ecosystem"]["id"] == "weather-voice-demo"
    weather = next(
        item for item in explanation["capabilities"] if item["id"] == "weather.forecast.html"
    )
    assert weather["matched_registry"] == "touri"
    assert weather["runtime_transport"] == "uri2run:python"
    assert weather["backend"]["type"] == "python"


def test_apply_plan_and_transaction(tmp_path: Path, repo_root: Path):
    (tmp_path / "deployments").mkdir()
    (tmp_path / "deployments" / "agent_deployments.yaml").write_text("deployments: []\n", encoding="utf-8")
    (tmp_path / "contracts" / "agents").mkdir(parents=True)
    (tmp_path / "examples" / "20_touri_capabilities").mkdir(parents=True)
    (tmp_path / "tests" / "ecosystems").mkdir(parents=True)

    proposal_path = write_yaml(tmp_path / "proposal.yaml", plan_ecosystem("agent pogodowy"))
    generated = generate_ecosystem(proposal_path, out=tmp_path / "ecosystem", root=repo_root)

    planned = apply_ecosystem(generated["ecosystem_file"], plan_only=True, root=tmp_path)
    assert planned["status"] == "planned"
    assert Path(planned["plan_path"]).is_file()

    blocked = apply_ecosystem(generated["ecosystem_file"], root=tmp_path)
    assert blocked["ok"] is False
    assert blocked["status"] == "blocked"

    approved = apply_ecosystem(generated["ecosystem_file"], approve=True, root=tmp_path)
    assert approved["ok"] is True
    assert approved["status"] == "applied"
    assert Path(approved["result_path"]).is_file()
    assert (tmp_path / "contracts" / "agents" / "weather_map_agent.yaml").is_file()


def test_proposal_and_ecosystem_have_envelope():
    proposal = plan_ecosystem("agent pogodowy z healthcheckiem")
    assert proposal["kind"] == "EcosystemProposal"
    assert proposal["uri"]["self"].startswith("proposal://ecosystem/")


def test_plan_and_verify_do_not_touch_repo_roots(tmp_path: Path, repo_root: Path):
    protected = [
        repo_root / "contracts",
        repo_root / "deployments",
        repo_root / "agents" / "generated",
    ]
    before = {path: path.stat().st_mtime_ns for path in protected if path.exists()}

    proposal = plan_ecosystem("agent pogodowy z healthcheckiem")
    proposal_path = write_yaml(tmp_path / "proposal.yaml", proposal)
    generated = generate_ecosystem(proposal_path, out=tmp_path / "ecosystem", root=repo_root)
    verification = verify_ecosystem(generated["ecosystem_file"], root=repo_root)

    assert verification["ok"] is True
    after = {path: path.stat().st_mtime_ns for path in protected if path.exists()}
    assert after == before


def test_cli_plan_generate_verify(tmp_path: Path):
    proposal_path = tmp_path / "proposal.yaml"
    ecosystem_dir = tmp_path / "ecosystem"

    assert (
        urigen_main(
            [
                "plan",
                "-p",
                "stworz agenta pogodowego",
                "--out",
                str(proposal_path),
            ]
        )
        == 0
    )
    assert proposal_path.is_file()

    assert urigen_main(["generate", str(proposal_path), "--out", str(ecosystem_dir)]) == 0
    assert urigen_main(["verify", str(ecosystem_dir / "ecosystem.yaml"), "--no-report"]) == 0

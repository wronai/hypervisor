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
from urigen.io import dump_yaml, load_yaml, write_yaml
from urigen.models import normalize_profile, profile_catalog


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
    capability = load_yaml(
        ecosystem_path.parent / "capabilities" / "weather_forecast.uri.capability.yaml"
    )
    assert capability["data_quality"]["failure_code"] == "GENERATED_ECOSYSTEM_DATA_QUALITY_FAILED"
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
    assert weather["verification"]["data_quality_enabled"] is True
    assert explanation["risks"] == []


def test_profile_aliases_are_canonicalized():
    assert normalize_profile("voice-agent") == "voice"
    assert normalize_profile("operator-agent") == "operator"
    assert normalize_profile("ecosystem") == "full"
    assert normalize_profile("dashboard") == "dashboard-agent"

    proposal = plan_ecosystem("stworz agenta pogodowego z TTS", profile="voice-agent")
    assert proposal["proposal"]["profile"] == "voice"
    assert proposal["profile"]["name"] == "voice"
    assert "voice-agent" in profile_catalog()["voice"]["aliases"]


def test_apply_plan_and_transaction(tmp_path: Path, repo_root: Path):
    (tmp_path / "deployments").mkdir()
    (tmp_path / "deployments" / "agent_deployments.yaml").write_text(
        "deployments: []\n", encoding="utf-8"
    )
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


def _setup_apply_tmp(tmp_path: Path, repo_root: Path) -> dict[str, object]:
    (tmp_path / "deployments").mkdir()
    (tmp_path / "deployments" / "agent_deployments.yaml").write_text(
        "deployments: []\n", encoding="utf-8"
    )
    (tmp_path / "contracts" / "agents").mkdir(parents=True)
    (tmp_path / "examples" / "20_touri_capabilities").mkdir(parents=True)
    (tmp_path / "tests" / "ecosystems").mkdir(parents=True)
    proposal_path = write_yaml(tmp_path / "proposal.yaml", plan_ecosystem("agent pogodowy"))
    return generate_ecosystem(proposal_path, out=tmp_path / "ecosystem", root=repo_root)


def test_apply_plan_includes_diff(tmp_path: Path, repo_root: Path):
    generated = _setup_apply_tmp(tmp_path, repo_root)
    planned = apply_ecosystem(generated["ecosystem_file"], plan_only=True, root=tmp_path)
    assert planned["status"] == "planned"
    assert planned.get("diff")
    assert any(item.get("change") in {"create", "update", "merge"} for item in planned["diff"])


def test_apply_idempotent_second_run(tmp_path: Path, repo_root: Path):
    generated = _setup_apply_tmp(tmp_path, repo_root)
    first = apply_ecosystem(generated["ecosystem_file"], approve=True, root=tmp_path)
    assert first["ok"] is True
    second = apply_ecosystem(generated["ecosystem_file"], approve=True, root=tmp_path)
    assert second["ok"] is True
    contract_action = next(
        item
        for item in second["actions"]
        if str(item.get("id", "")).startswith("merge_agent_contract")
    )
    assert contract_action["status"] == "unchanged"


def test_apply_failure_rolls_back_created_files(tmp_path: Path, repo_root: Path, monkeypatch):
    generated = _setup_apply_tmp(tmp_path, repo_root)
    target = tmp_path / "contracts" / "agents" / "weather_map_agent.yaml"
    monkeypatch.setattr(
        "urigen.apply_executor.verify_ecosystem",
        lambda *args, **kwargs: {"ok": False, "checks": [{"id": "doctor", "ok": False}]},
    )
    result = apply_ecosystem(generated["ecosystem_file"], approve=True, root=tmp_path)
    assert result["ok"] is False
    assert result["status"] == "rolled_back"
    assert not target.exists()
    assert (Path(result["rollback"]["path"]) / "manifest.json").is_file()


def test_apply_manual_rollback_restores_files(tmp_path: Path, repo_root: Path):
    generated = _setup_apply_tmp(tmp_path, repo_root)
    result = apply_ecosystem(generated["ecosystem_file"], approve=True, root=tmp_path)
    assert result["ok"] is True
    target = tmp_path / "contracts" / "agents" / "weather_map_agent.yaml"
    original = target.read_text(encoding="utf-8")
    target.write_text("corrupted\n", encoding="utf-8")
    rolled = apply_ecosystem(generated["ecosystem_file"], rollback=True, root=tmp_path)
    assert rolled["ok"] is True
    assert target.read_text(encoding="utf-8") == original


def test_proposal_and_ecosystem_have_envelope(tmp_path: Path):
    proposal = plan_ecosystem("agent pogodowy z healthcheckiem")
    assert proposal["kind"] == "EcosystemProposal"
    assert proposal["uri"]["self"].startswith("proposal://ecosystem/")
    rendered_proposal = dump_yaml(proposal)
    assert rendered_proposal.startswith("$schema:")
    assert "&id" not in rendered_proposal

    proposal_path = write_yaml(tmp_path / "proposal.yaml", proposal)
    generated = generate_ecosystem(proposal_path, out=tmp_path / "ecosystem")
    ecosystem = load_yaml(generated["ecosystem_file"])
    assert ecosystem["kind"] == "Ecosystem"
    assert ecosystem["uri"]["self"].startswith("ecosystem://")
    rendered_ecosystem = dump_yaml(ecosystem)
    assert rendered_ecosystem.startswith("$schema:")
    assert "&id" not in rendered_ecosystem


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


def test_cli_profiles_lists_aliases(capsys):
    assert urigen_main(["profiles", "--json"]) == 0
    output = capsys.readouterr().out
    assert '"voice-agent"' in output
    assert '"dashboard-agent"' in output

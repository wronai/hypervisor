from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def load_audit_module(repo_root: Path):
    path = repo_root / "scripts" / "architecture_responsibility_audit.py"
    spec = importlib.util.spec_from_file_location("architecture_responsibility_audit", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_fixture_files(tmp_path: Path) -> tuple[Path, Path]:
    map_path = tmp_path / "map.toon.yaml"
    dup_path = tmp_path / "duplication.toon.yaml"
    map_path.write_text(
        "\n".join(
            [
                "# hypervisor | 5f 920L | python:5 | 2026-06-15",
                "# stats: 10 func | 0 cls | 5 mod | CCx=3.7 | critical:1 | cycles:0",
                "# alerts[1]: CC proof_uri=38",
                "# hotspots[1]: register_runtime_commands fan=30",
                "# Keys: M=modules",
                "M[5]:",
                "  agents/operators/browser_operator/adapters/browser_router.py,40",
                "  packages/uri3/uri3/graph/adapters/browser_router.py,50",
                "  packages/urish/urish/cli.py,450",
                "  packages/urish/urish/office_scenarios.py,25",
                "  domains/office/scenario_registry.yaml,20",
                "D:",
            ]
        ),
        encoding="utf-8",
    )
    dup_path.write_text(
        "\n".join(
            [
                "# redup/duplication | 2 groups | 4f 900L | 2026-06-15",
                "",
                "SUMMARY:",
                "  files_scanned: 4",
                "  total_lines:   900",
                "  dup_groups:    2",
                "  dup_fragments: 4",
                "  saved_lines:   42",
                "  scan_ms:       1",
                "",
                "HOTSPOTS[1] (files with most duplication):",
                (
                    "  packages/uri2run/uri2run/transports/flow_transport.py  "
                    "dup=54L  groups=2  frags=2  (0.2%)"
                ),
                "",
                "DUPLICATES[2] (ranked by impact):",
                "  [abc] ! STRU  _playwright_ready  L=17 N=2 saved=17 sim=1.00",
                (
                    "      agents/operators/browser_operator/adapters/"
                    "browser_router.py:12-28  (_playwright_ready)"
                ),
                (
                    "      packages/uri3/uri3/graph/adapters/"
                    "browser_router.py:20-36  (_playwright_ready)"
                ),
                "  [def]   EXAC  resolve_view_uri  L=25 N=2 saved=25 sim=1.00",
                (
                    "      output/ecosystems/hypervisor-dashboard/app/"
                    "hypervisor_dashboard_agent/uri_client.py:47-71  (resolve_view_uri)"
                ),
                (
                    "      agents/system/hypervisor_dashboard/"
                    "hypervisor_dashboard_agent/uri_client.py:69-93  (resolve_view_uri)"
                ),
            ]
        ),
        encoding="utf-8",
    )
    return map_path, dup_path


def test_audit_detects_cross_boundary_duplication(repo_root: Path, tmp_path: Path):
    audit = load_audit_module(repo_root)
    map_path, dup_path = write_fixture_files(tmp_path)

    result = audit.build_audit(tmp_path, map_path, dup_path)
    categories = {finding.category for finding in result.findings}

    assert "runtime_operator_boundary_duplication" in categories
    assert "generated_snapshot_duplication" in categories
    assert "large_command_surface" in categories
    assert "stale_map_entry" in categories
    assert any(finding.severity == "critical" for finding in result.findings)


def test_audit_ignores_stale_duplicate_symbol_when_file_changed(
    repo_root: Path,
    tmp_path: Path,
):
    audit = load_audit_module(repo_root)
    map_path, dup_path = write_fixture_files(tmp_path)
    uri2run_file = (
        tmp_path
        / "packages"
        / "uri2run"
        / "uri2run"
        / "transports"
        / "uri2ops_transport.py"
    )
    uri3_file = (
        tmp_path
        / "packages"
        / "uri3"
        / "uri3"
        / "graph"
        / "adapters"
        / "uri2ops_adapter.py"
    )
    uri2run_file.parent.mkdir(parents=True)
    uri3_file.parent.mkdir(parents=True)
    uri2run_file.write_text("def registry_scheme(scheme):\n    return scheme\n", encoding="utf-8")
    uri3_file.write_text("def registry_scheme(scheme):\n    return scheme\n", encoding="utf-8")
    dup_path.write_text(
        "\n".join(
            [
                "# redup/duplication | 1 groups | 2f 20L | 2026-06-15",
                "",
                "SUMMARY:",
                "  files_scanned: 2",
                "  total_lines:   20",
                "  dup_groups:    1",
                "  dup_fragments: 2",
                "  saved_lines:   4",
                "  scan_ms:       1",
                "",
                "DUPLICATES[1] (ranked by impact):",
                "  [abc]   EXAC  _registry_scheme  L=4 N=2 saved=4 sim=1.00",
                (
                    "      packages/uri2run/uri2run/transports/"
                    "uri2ops_transport.py:30-33  (_registry_scheme)"
                ),
                (
                    "      packages/uri3/uri3/graph/adapters/"
                    "uri2ops_adapter.py:37-40  (_registry_scheme)"
                ),
            ]
        ),
        encoding="utf-8",
    )

    result = audit.build_audit(tmp_path, map_path, dup_path)

    assert not any("Duplicate _registry_scheme" in finding.title for finding in result.findings)


def test_audit_flags_domain_named_generic_module_when_file_exists(
    repo_root: Path,
    tmp_path: Path,
):
    audit = load_audit_module(repo_root)
    map_path, dup_path = write_fixture_files(tmp_path)
    office_module = tmp_path / "packages" / "urish" / "urish" / "office_scenarios.py"
    office_module.parent.mkdir(parents=True)
    office_module.write_text(
        "from urish.scenario_registry import match_scenario\n",
        encoding="utf-8",
    )

    result = audit.build_audit(tmp_path, map_path, dup_path)

    assert any(
        finding.category == "domain_named_module_in_generic_package"
        and finding.paths == ["packages/urish/urish/office_scenarios.py"]
        for finding in result.findings
    )


def test_audit_does_not_flag_domain_vocabulary_in_operator_agents(repo_root: Path, tmp_path: Path):
    audit = load_audit_module(repo_root)
    map_path, dup_path = write_fixture_files(tmp_path)
    runtime_file = (
        tmp_path
        / "agents"
        / "operators"
        / "browser_operator"
        / "adapters"
        / "browser_router.py"
    )
    runtime_file.parent.mkdir(parents=True)
    runtime_file.write_text("def route():\n    return 'invoice bank allegro'\n", encoding="utf-8")

    result = audit.build_audit(tmp_path, map_path, dup_path)

    assert not any(
        finding.category == "domain_vocabulary_in_generic_package"
        for finding in result.findings
    )


def test_audit_ignores_its_own_domain_vocabulary(repo_root: Path, tmp_path: Path):
    audit = load_audit_module(repo_root)
    map_path, dup_path = write_fixture_files(tmp_path)
    audit_rules = tmp_path / "scripts" / "architecture_audit" / "areas.py"
    audit_rules.parent.mkdir(parents=True)
    audit_rules.write_text("DOMAIN_VOCABULARY = {'invoice', 'bank'}\n", encoding="utf-8")
    map_path.write_text(
        "\n".join(
            [
                "# hypervisor | 1f 10L | python:1 | 2026-06-15",
                "# stats: 1 func | 0 cls | 1 mod | CCx=1.0 | critical:0 | cycles:0",
                "# Keys: M=modules",
                "M[1]:",
                "  scripts/architecture_audit/areas.py,10",
                "D:",
            ]
        ),
        encoding="utf-8",
    )

    result = audit.build_audit(tmp_path, map_path, dup_path)

    assert not any(
        finding.category == "domain_vocabulary_in_generic_package"
        and finding.paths == ["scripts/architecture_audit/areas.py"]
        for finding in result.findings
    )


def test_audit_cli_outputs_json(repo_root: Path, tmp_path: Path):
    map_path, dup_path = write_fixture_files(tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "architecture_responsibility_audit.py"),
            "--root",
            str(tmp_path),
            "--map",
            str(map_path),
            "--dup",
            str(dup_path),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["modules_parsed"] == 5
    assert payload["summary"]["duplicate_groups_parsed"] == 2
    assert payload["refactor_backlog"]

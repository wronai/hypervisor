# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added comprehensive examples integration suite in `tests/examples/`:
  `catalog.py`, parametrized `run.sh` tests, inline demos (02–08, 15pw), smoke
  checks for touri manifests and architecture stack imports.
- Added `scripts/ci/ensure_editable_install.sh` for examples running outside a
  prepared venv.
- Added CI job **Examples integration** (`.github/workflows/ci.yml`) with
  Playwright browser extra.
- Added pytest markers: `examples`, `docker`, `slow`.
- Added `make examples-test`; `make ci-gate` now runs architecture + full pytest + examples.
- Added `hypervisor inspect-agent` readiness block (process/health/card/effective_port).
- Added `hypervisor supervise --repair auto|restart|sync_health` bounded repair loop.
- Added `hypervisor run-agent --wait-healthy --supervise-repair auto`.
- Added evolutionary repair layer `hypervisor/repair/` with schema-valid incidents,
  error-family classifier, safe playbooks, repair memory, and `hypervisor repair learn`.
- Added schemas: `incident.schema.json`, `repair_plan.schema.json`, `runtime_state.schema.json`.
- Added `knowledge/repair_cases/` for deterministic repair sequences.
- Added artifact standardization layer (`uri3/artifacts/`): schema validation on write,
  runtime state envelope, LogEvent JSONL, workflow step artifacts, ticket/evolution source URIs.
- Added `hypervisor artifacts check|schemas`, `hypervisor ticket import`, `hypervisor evolution propose-from-*`.
- Added `hypervisor artifacts lifecycle` coverage report for `$schema` / `apiVersion`
  / `kind` / `uri.self` across configs, deployments, contracts, runtime state and outputs.
- Added schemas: `ticket`, `log_event`, `workflow_artifact`, `deployment_registry`, `config/config_base`.
- Added `docs/EXTERNAL_PACKAGES.md` with the local `semcod/*` and `wronai/*`
  package audit, version snapshot, integration boundary and recommended next
  package work.
- Completed the `uri2run` MVP runtime package with Python, shell, HTTP,
  `uri_flow`, `uri_graph`, `uri2ops` and mock transport entry points.
- Added `packages/urigen` as the URI Ecosystem Generator MVP with
  `plan`, `generate`, `verify`, `explain`, and approval-gated `apply`.

### Changed

- Updated `examples/01_quickstart_local/run.sh` to light smoke (`uri-tree`,
  `validate`, `graph`) instead of full `make test`.
- Updated `scripts/test-all-examples.sh` to use `run.sh` for examples 01, 04, 09.
- Updated root and `examples/README.md` with run commands, example 16, and test/CI
  instructions.
- Split `uri3/doctor/checks.py` into `uri3/doctor/checks/` submodules with shared
  `boundary_scanner`.
- Updated README with the external package boundary and examples `17`, `18`,
  `20`, `21`, `22`.
- Documented `urigen` in the root README, package README, package catalog,
  CHANGELOG and TODO with its generator-only boundary and next roadmap items.
- Extended `hypervisor run-agent` with `--if-running reuse|restart|fail` so
  detached lifecycle handling can be explicit and idempotent.
- Updated `docs/ROADMAP.md` with the `markpact` / `pactown` / `nlp2dsl` /
  `iterun` / `intract` integration sequence.
- Added manual integration backlog items to `TODO.md` for `pactown`,
  `nlp2dsl`, `intract`, `iterun` and environment wrapper alignment.
- Delegated `touri` backend wrappers to `uri2run.run_backend` while preserving
  the existing `ServiceResult` envelope.
- Extended `uri3 explain` to report `runtime_transport` for `uri2run` backends.

### Fixed

- Fixed `generator.verify` treating `agents/generated/__pycache__` as a generated
  agent directory.
- Fixed `examples/04_nl2a_weather_map` and `examples/20_touri_capabilities` for
  editable install and verify flow.
- Fixed idempotent `hypervisor run-agent --detach` in tutorial example 23
  (`lifecycle.py` reuses healthy agent when already running).
- Fixed lifecycle envelope marking `ok=true` when only PID exists but HTTP health fails.
- Fixed effective `health_uri` derived from uvicorn `--port` in runtime state (ex23 port drift).

## [0.5.20] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/architecture/test_uri2run_envelope.py
- Update tests/ecosystems/weather-demo/test_explain_uris.yaml
- Update tests/ecosystems/weather-demo/test_plan.yaml
- Update tests/ecosystems/weather-demo/test_workflow_dry_run.yaml
- Update tests/hypervisor/test_artifact_standards.py
- Update tests/hypervisor/test_repair_supervisor.py
- Update tests/urigen/test_urigen_cycle.py

### Other
- Update deployments/agent_deployments.yaml
- Update examples/13_nl2uri_multi_uri_graph/task_plan.yaml
- Update output/contract_registry.resolved.json
- Update packages/resource-agent-hypervisor/hypervisor/artifacts/__init__.py
- Update packages/resource-agent-hypervisor/hypervisor/artifacts/gate.py
- Update packages/resource-agent-hypervisor/hypervisor/cli.py
- Update packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py
- Update packages/resource-agent-hypervisor/hypervisor/deployment_registry/loader.py
- Update packages/resource-agent-hypervisor/hypervisor/deployment_registry/models.py
- Update packages/resource-agent-hypervisor/hypervisor/deployment_registry/runtime_state.py
- ... and 67 more files

## [0.5.19] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update docs/CLI_MAP.md
- Update docs/DEPLOYMENT.md
- Update docs/PACKAGE_BOUNDARIES.md
- Update docs/PACKAGE_BOUNDARIES.yaml
- Update docs/README.md
- Update examples/09_run_agent_hypervisor/README.md
- Update examples/README.md
- ... and 4 more files

### Test
- Update tests/examples/catalog.py
- Update tests/examples/conftest.py
- Update tests/examples/test_examples_smoke.py
- Update tests/examples/test_inline_examples.py
- Update tests/examples/test_run_sh_examples.py
- Update tests/generator/test_headers.py
- Update tests/hypervisor/test_agent_runner.py
- Update tests/hypervisor/test_hypervisor_cli.py
- Update tests/hypervisor/test_repair_supervisor.py
- Update tests/urigen/test_urigen_cycle.py

### Other
- Update Makefile
- Update examples/01_quickstart_local/run.sh
- Update examples/04_nl2a_weather_map/run.sh
- Update examples/09_run_agent_hypervisor/run.sh
- Update examples/13_nl2uri_multi_uri_graph/task_plan.yaml
- Update examples/20_touri_capabilities/run.sh
- Update examples/23_nl_to_agent_tutorial/run.sh
- Update knowledge/repair_cases/health_timeout_after_dynamic_port.yaml
- Update output/contract_registry.resolved.json
- Update packages/resource-agent-factory/generator/verify.py
- ... and 60 more files

## [0.5.18] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update docs/CLI_MAP.md
- Update docs/PACKAGE_BOUNDARIES.md
- Update docs/URI2RUN_ARCHITECTURE.md
- Update packages/uri2run/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/architecture/import_scanner.py
- Update tests/architecture/test_doctor_contract.py
- Update tests/architecture/test_doctor_gate.py
- Update tests/architecture/test_result_envelope_contract.py
- Update tests/architecture/test_technical_ok_business_fail.py
- Update tests/architecture/test_uri2run_envelope.py
- Update tests/hypervisor/test_agent_runner.py
- Update tests/uri2run/test_protocol_transports.py
- Update tests/uri2run/test_transport_matrix.py
- Update tests/uri3/test_explain_extended.py

### Other
- Update .gitignore
- Update Makefile
- Update domains/weather_map/uri_tree.yaml
- Update examples/13_nl2uri_multi_uri_graph/task_plan.yaml
- Update examples/20_touri_capabilities/run.sh
- Update examples/23_nl_to_agent_tutorial/run.sh
- Update packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py
- Update packages/touri/touri/backend_dispatch.py
- Update packages/touri/touri/validator.py
- Update packages/uri2run/uri2run/cli.py
- ... and 42 more files

## [0.5.17] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update docs/PACKAGE_BOUNDARIES.md
- Update docs/PACKAGE_BOUNDARIES.yaml
- Update docs/README.md
- Update docs/URI2RUN_ARCHITECTURE.md
- Update packages/README.md
- Update packages/uri2run/README.md
- Update project/README.md
- ... and 1 more files

### Test
- Update tests/architecture/import_scanner.py
- Update tests/architecture/test_explain_contract.py
- Update tests/uri2run/test_stream_transports.py
- Update tests/uri2run/test_transport_matrix.py
- Update tests/uri2run/test_uri2run.py

### Other
- Update packages/touri/pyproject.toml
- Update packages/touri/touri/backend_dispatch.py
- Update packages/touri/touri/backends/__init__.py
- Update packages/touri/touri/backends/mock_backend.py
- Update packages/touri/touri/backends/python_backend.py
- Update packages/touri/touri/backends/shell_backend.py
- Update packages/touri/touri/backends/uri2ops_backend.py
- Update packages/touri/touri/backends/uri_flow_backend.py
- Update packages/touri/touri/backends/uri_graph_backend.py
- Update packages/touri/touri/runtime_adapter.py
- ... and 38 more files

## [0.5.16] - 2026-06-14

### Docs
- Update README.md
- Update docs/ARCHITECTURE_RUNTIME_AND_TESTING.md
- Update docs/PACKAGE_BOUNDARIES.md
- Update docs/PACKAGE_BOUNDARIES.yaml
- Update docs/README.md
- Update docs/ROADMAP.md
- Update docs/URI2RUN_ARCHITECTURE.md
- Update packages/README.md
- Update packages/uri2run/README.md
- Update packages/uri2verify/README.md
- ... and 2 more files

### Test
- Update tests/architecture/envelope_helpers.py
- Update tests/architecture/import_scanner.py
- Update tests/architecture/test_doctor_contract.py
- Update tests/architecture/test_explain_contract.py
- Update tests/architecture/test_import_boundaries.py
- Update tests/architecture/test_result_envelope_contract.py
- Update tests/touri/test_markpact_loader.py

### Other
- Update packages/uri2pact/uri2pact/capabilities.py
- Update packages/uri2pact/uri2pact/flows.py
- Update packages/uri2run/pyproject.toml
- Update packages/uri2run/uri2run/__init__.py
- Update packages/uri2run/uri2run/cli.py
- Update packages/uri2run/uri2run/context.py
- Update packages/uri2run/uri2run/result.py
- Update packages/uri2run/uri2run/runner.py
- Update packages/uri2run/uri2run/transports/__init__.py
- Update packages/uri2run/uri2run/transports/flow_transport.py
- ... and 30 more files

## [0.5.15] - 2026-06-14

### Docs
- Update .registry/README.md
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/EXTERNAL_PACKAGES.md
- Update docs/PACKAGE_BOUNDARIES.md
- Update docs/README.md
- Update docs/ROADMAP.md
- ... and 12 more files

### Test
- Update tests/hypervisor/test_agent_runner.py
- Update tests/hypervisor/test_deployment_selector.py
- Update tests/touri/test_explain.py
- Update tests/touri/test_voice_capabilities.py
- Update tests/uri2verify/test_capability_tests.py
- Update tests/uri2verify/test_replay.py
- Update tests/uri2verify/test_result_checks.py
- Update tests/uri2verify/test_uri2verify_data_quality.py
- Update tests/uri3/test_doctor.py
- Update tests/uri3/test_envelope_migrate.py
- ... and 2 more files

### Other
- Update .registry/capability_index.json
- Update .registry/operation_index.json
- Update .registry/uri_index.json
- Update Makefile
- Update agents/generated/user_agent/agent_card.py
- Update agents/generated/user_agent/routes.py
- Update agents/generated/weather_map_agent/agent_card.py
- Update agents/generated/weather_map_agent/routes.py
- Update app.doql.less
- Update contracts/agents/invoices_agent.yaml
- ... and 111 more files

## [0.1.10] - 2026-06-14

### Fixed
- Fix unused-imports issues (ticket-88df7d99)
- Fix magic-numbers issues (ticket-465f8054)

## [0.1.10] - 2026-06-14

### Fixed
- Fix unused-imports issues (ticket-87d349be)
- Fix unused-imports issues (ticket-7beb6f42)
- Fix unused-imports issues (ticket-1bfcaeeb)

## [0.1.10] - 2026-06-14

### Fixed
- Fix unused-imports issues (ticket-e4a8078c)

## [0.1.10] - 2026-06-14

### Fixed
- Fix string-concat issues (ticket-0df86be1)
- Fix unused-imports issues (ticket-845746ab)
- Fix magic-numbers issues (ticket-8fe1ea3e)

## [0.1.10] - 2026-06-14

### Fixed
- Fix unused-imports issues (ticket-690b4c67)
- Fix magic-numbers issues (ticket-25bdd7ff)
- Fix smart-return-type issues (ticket-e9652153)
- Fix unused-imports issues (ticket-7d2726b5)
- Fix ai-boilerplate issues (ticket-b0ccd6d4)
- Fix smart-return-type issues (ticket-a402183b)
- Fix ai-boilerplate issues (ticket-3e8a9532)
- Fix string-concat issues (ticket-ed0a608d)
- Fix smart-return-type issues (ticket-a8b52d89)
- Fix magic-numbers issues (ticket-865c12d0)
- Fix string-concat issues (ticket-b05ca504)
- Fix unused-imports issues (ticket-dbae451c)
- Fix unused-imports issues (ticket-865c637e)
- Fix ai-boilerplate issues (ticket-69819513)
- Fix string-concat issues (ticket-e83a9f54)
- Fix unused-imports issues (ticket-40311cfb)
- Fix unused-imports issues (ticket-8d8fb28e)
- Fix unused-imports issues (ticket-bde17bd0)
- Fix unused-imports issues (ticket-85dd0f79)
- Fix ai-boilerplate issues (ticket-90917ed0)
- Fix unused-imports issues (ticket-3cc1f81d)
- Fix ai-boilerplate issues (ticket-92a67e2d)
- Fix unused-imports issues (ticket-dd2b1821)
- Fix relative-imports issues (ticket-ba303eb9)
- Fix unused-imports issues (ticket-6d18c8d6)
- Fix smart-return-type issues (ticket-9a4fa4ca)
- Fix ai-boilerplate issues (ticket-afcf5a99)
- Fix unused-imports issues (ticket-a3ef7083)
- Fix unused-imports issues (ticket-1700b2b8)
- Fix unused-imports issues (ticket-0ff0b6f6)
- Fix unused-imports issues (ticket-f5195ea7)
- Fix unused-imports issues (ticket-cb87ddc9)
- Fix unused-imports issues (ticket-343765a5)
- Fix string-concat issues (ticket-86c0756c)
- Fix unused-imports issues (ticket-55bf1f0c)
- Fix ai-boilerplate issues (ticket-15440ab9)
- Fix unused-imports issues (ticket-466161eb)
- Fix unused-imports issues (ticket-9ea83eeb)
- Fix unused-imports issues (ticket-de653f6e)
- Fix unused-imports issues (ticket-133eb4aa)
- Fix unused-imports issues (ticket-7d59cd5b)
- Fix string-concat issues (ticket-c7d9f791)
- Fix unused-imports issues (ticket-e11ca477)
- Fix unused-imports issues (ticket-4264f2fc)
- Fix unused-imports issues (ticket-2409f095)
- Fix relative-imports issues (ticket-e7c63477)
- Fix unused-imports issues (ticket-cd331354)
- Fix llm-generated-code issues (ticket-ffb72480)
- Fix unused-imports issues (ticket-753d7009)
- Fix unused-imports issues (ticket-516a43af)
- Fix magic-numbers issues (ticket-429999e1)
- Fix unused-imports issues (ticket-1576a47a)
- Fix unused-imports issues (ticket-9d598e2c)
- Fix unused-imports issues (ticket-a812e992)
- Fix unused-imports issues (ticket-ceb2ffb9)
- Fix unused-imports issues (ticket-b3e96ca2)
- Fix unused-imports issues (ticket-d3a2ef34)
- Fix ai-boilerplate issues (ticket-0d221dc4)
- Fix unused-imports issues (ticket-7bb433a7)
- Fix unused-imports issues (ticket-bbdc0619)
- Fix unused-imports issues (ticket-d400d413)
- Fix unused-imports issues (ticket-efc955cc)
- Fix smart-return-type issues (ticket-2fedbcbe)
- Fix unused-imports issues (ticket-1dc852fe)
- Fix unused-imports issues (ticket-c25578fb)
- Fix unused-imports issues (ticket-f67d9dfd)
- Fix unused-imports issues (ticket-43ad97cf)
- Fix ai-boilerplate issues (ticket-71c6178b)
- Fix unused-imports issues (ticket-18ee002a)
- Fix unused-imports issues (ticket-94406158)
- Fix ai-boilerplate issues (ticket-e22d376f)
- Fix unused-imports issues (ticket-928d1506)
- Fix unused-imports issues (ticket-4c9edf37)
- Fix string-concat issues (ticket-f92bca3d)
- Fix unused-imports issues (ticket-e8e0d04b)
- Fix unused-imports issues (ticket-36cf5f5d)
- Fix unused-imports issues (ticket-9edaf0d9)
- Fix unused-imports issues (ticket-aa87dded)
- Fix magic-numbers issues (ticket-9830d889)
- Fix string-concat issues (ticket-038db146)
- Fix unused-imports issues (ticket-04c476be)
- Fix unused-imports issues (ticket-79542bb5)
- Fix string-concat issues (ticket-3d67f0f5)
- Fix unused-imports issues (ticket-0e3cbe53)
- Fix smart-return-type issues (ticket-4173afc6)
- Fix unused-imports issues (ticket-a192f40c)
- Fix smart-return-type issues (ticket-6bb46fa8)
- Fix unused-imports issues (ticket-daa55462)
- Fix ai-boilerplate issues (ticket-f022b5e6)

## [0.5.6] - 2026-06-14

### Added

- `log://` URI scheme in `uri3` for reading and filtering log files.
- `uri3.protocols.scheme_registry` — introspection API for URI formats, query options, actions, and examples.
- CLI command `uri3 schema [target]` with `--list` and `--analyze` for scheme docs and concrete URI analysis.
- `uri3.logs.reader` with JSON/text parsing and filters: `level`, `grep`, `logger`, `since`, `until`, `limit`, `offset`, `tail`.
- `uri3.resolvers.log_resolver` and router integration (`resolve`, `call`).
- `uri3 scan log://...` for log discovery with match counts and level breakdown.
- CLI command `uri3 logs <log://...>` with optional `--summary`.
- `Uri3Client.logs()` adapter in hypervisor.
- Tests in `tests/uri3/test_log_uri.py`.

### Changed

- `uri3.protocols.schemes` and hypervisor config `enabled_schemes` include `log`.

### Notes

- Default streams map to `output/logs/{stream}.log` under repo root, e.g. `log://hypervisor?level=ERROR`.
- Explicit files use `log://file/output/logs/hypervisor.log` or `log://hypervisor/subpath.log` with repo-relative paths.
- Filters compose: `log://hypervisor?level=ERROR&grep=deployment&since=1h&limit=100`.

## [0.5.5] - 2026-06-14

### Added

- Monorepo layout under `packages/`:
  - `packages/uri3`
  - `packages/nl2uri` (+ `nl2a`)
  - `packages/resource-agent-hypervisor`
  - `packages/resource-agent-factory`
- uv workspace in root `pyproject.toml`.
- Shared `find_repo_root()` markers (`contracts/` + `schemas/`).

### Changed

- Generator templates path and domain pack `root=` parameter for isolated tests.
- Unified AUTO-GENERATED headers in `resource-agent-factory`.

## [0.5.4] - 2026-06-14

### Added

- `hypervisor/deployment_registry/` (models, loader, writer, status).
- `deployments/agent_deployments.yaml` as Agent Deployment Registry seed.
- Pipeline sync via `sync_from_uri_tree()`.
- Tests in `tests/hypervisor/test_deployment_registry.py`.

## [0.5.3] - 2026-06-14

### Added

- `nl2uri.pipeline.run_full_pipeline()` — prompt → URI Tree → Domain Pack → agent → registry.
- `meta_agent/repair/` split into loader, rules, pipeline.
- E2E tests in `tests/integration/test_nl2a_e2e.py`.

### Changed

- `nl2a` CLI uses full pipeline.
- Config split into `hypervisor/config/{defaults,env,loader,models,validators}.py`.

## [0.5.2] - 2026-06-14

### Added

- Canonical Domain Pack generator in `hypervisor/domain_pack/generator.py` (parse → model → artifacts → write → validate → merge).
- Templates and contract merger for domain packs.
- Tests in `tests/domain_pack/test_generator.py`.

### Changed

- `meta_agent/domain_planner/domain_pack_generator.py` deprecated as re-export.

## [0.5.1] - 2026-06-14

### Added

- Testowe środowisko `testenv/docker-compose.ssh.yml`.
- Kontener `testenv/ssh_agent_host/` z OpenSSH oraz mock agentem HTTP.
- Przykłady w `examples/*/*`:
  - lokalny quickstart,
  - skanowanie HTTP,
  - skanowanie SSH przez kontener,
  - prompt weather-map.
- `deployments/agent_deployments.yaml` jako początek Agent Deployment Registry.
- `uri3.scanner.ssh_scanner` z bezpiecznym trybem `BatchMode=yes`.
- Komendy Makefile:
  - `make docker-ssh-up`,
  - `make docker-ssh-down`,
  - `make scan-http`,
  - `make examples`.
- `uri3` jako paczka od URI, graph, resolverów i scannerów.
- `nl2uri` jako paczka `prompt -> URI Tree`.
- `nl2a` jako pipeline `prompt -> URI Tree -> Domain Pack -> agent`.

### Changed

- README opisuje teraz praktyczny start, przykłady i środowisko SSH.
- `uri3.scanner.scanner` obsługuje `ssh://` obok `http://` i `https://`.
- Resolver logic przeniesiony do `uri3/resolvers/` (`protocol_resolver`, `pypi_resolver`, unified router).

### Notes

- Skaner SSH nie podaje hasła automatycznie i nie powinien tego robić. Do automatyzacji używaj kluczy SSH.
- Mock agent HTTP jest tylko środowiskiem testowym; nie implementuje pełnego A2A task lifecycle.

## [0.5.0] - 2026-06-14

### Added

- Initial split: `uri3`, `nl2uri`, `nl2a`, hypervisor responsibilities documented in `docs/ARCHITECTURE_V0_5.md`.

## [0.1.10] - 2026-06-14

### Fixed
- Fix unused-imports issues (ticket-00003659)
- Fix smart-return-type issues (ticket-872cfffc)
- Fix unused-imports issues (ticket-04f706f9)
- Fix smart-return-type issues (ticket-7dfb5b9a)
- Fix magic-numbers issues (ticket-dac6468f)
- Fix ai-boilerplate issues (ticket-ad9d29e1)
- Fix smart-return-type issues (ticket-8c04edf3)
- Fix unused-imports issues (ticket-6405c5fd)
- Fix smart-return-type issues (ticket-3b7074ab)
- Fix unused-imports issues (ticket-a5ed41d3)
- Fix smart-return-type issues (ticket-009a2fdd)
- Fix unused-imports issues (ticket-928e2453)
- Fix smart-return-type issues (ticket-90793d63)
- Fix unused-imports issues (ticket-c63d0bcd)
- Fix smart-return-type issues (ticket-b1ab7af7)
- Fix unused-imports issues (ticket-5eb38ac1)

## [0.1.10] - 2026-06-14

### Fixed
- Fix relative-imports issues (ticket-9f7a174f)
- Fix unused-imports issues (ticket-34e3f904)
- Fix unused-imports issues (ticket-79b13394)
- Fix unused-imports issues (ticket-cd6cf91d)
- Fix unused-imports issues (ticket-79f07cd0)
- Fix unused-imports issues (ticket-2d8b8b22)
- Fix unused-imports issues (ticket-1394e230)
- Fix unused-imports issues (ticket-98cbf095)
- Fix string-concat issues (ticket-8f700c0b)
- Fix unused-imports issues (ticket-70ac9a95)
- Fix unused-imports issues (ticket-e646160e)
- Fix string-concat issues (ticket-754eab08)
- Fix unused-imports issues (ticket-60b3c445)
- Fix smart-return-type issues (ticket-cba515d7)

## [0.1.10] - 2026-06-14

### Fixed
- Fix relative-imports issues (ticket-aac55abe)
- Fix unused-imports issues (ticket-9f67ccf0)
- Fix wildcard-imports issues (ticket-16ad8cc2)
- Fix wildcard-imports issues (ticket-1c87827e)
- Fix relative-imports issues (ticket-bf353904)
- Fix unused-imports issues (ticket-975ce41a)
- Fix unused-imports issues (ticket-2ee22785)
- Fix magic-numbers issues (ticket-7be21326)
- Fix string-concat issues (ticket-76fb30be)
- Fix unused-imports issues (ticket-c27b69dd)
- Fix unused-imports issues (ticket-3a7f7f87)
- Fix ai-boilerplate issues (ticket-c7663486)
- Fix unused-imports issues (ticket-1755c10d)
- Fix ai-boilerplate issues (ticket-b4a7bb8b)
- Fix unused-imports issues (ticket-02c420a4)
- Fix ai-boilerplate issues (ticket-35af4ff9)
- Fix unused-imports issues (ticket-a8673aa7)
- Fix unused-imports issues (ticket-b6cf4b50)
- Fix smart-return-type issues (ticket-886a9d81)
- Fix ai-boilerplate issues (ticket-9d1ccadf)
- Fix unused-imports issues (ticket-9cc9ea39)
- Fix string-concat issues (ticket-6f54155a)
- Fix unused-imports issues (ticket-64752c7b)
- Fix ai-boilerplate issues (ticket-52ee2d95)
- Fix relative-imports issues (ticket-baabe390)
- Fix unused-imports issues (ticket-19384e19)
- Fix unused-imports issues (ticket-e80b9f4c)
- Fix unused-imports issues (ticket-1022f85b)
- Fix unused-imports issues (ticket-1de82c8e)
- Fix unused-imports issues (ticket-c99e606c)
- Fix string-concat issues (ticket-699631dc)
- Fix unused-imports issues (ticket-0b1dd272)
- Fix unused-imports issues (ticket-7f84b882)
- Fix unused-imports issues (ticket-d8efe300)
- Fix relative-imports issues (ticket-8de13f58)
- Fix unused-imports issues (ticket-5971d29a)
- Fix llm-generated-code issues (ticket-d3276a36)
- Fix wildcard-imports issues (ticket-0472aa36)
- Fix unused-imports issues (ticket-3046f078)
- Fix ai-boilerplate issues (ticket-74738264)
- Fix unused-imports issues (ticket-c790a663)
- Fix unused-imports issues (ticket-6ee1ea5b)
- Fix unused-imports issues (ticket-1865bd39)
- Fix smart-return-type issues (ticket-8109d193)
- Fix relative-imports issues (ticket-75115c32)
- Fix unused-imports issues (ticket-bef18368)
- Fix string-concat issues (ticket-8f4fd2a7)
- Fix unused-imports issues (ticket-18d2eac0)
- Fix unused-imports issues (ticket-47fd0631)
- Fix unused-imports issues (ticket-93ca1e57)
- Fix string-concat issues (ticket-0de00f84)
- Fix unused-imports issues (ticket-26ff25b2)
- Fix unused-imports issues (ticket-8fc846b1)
- Fix unused-imports issues (ticket-df31867d)
- Fix ai-boilerplate issues (ticket-17b687d2)
- Fix relative-imports issues (ticket-5fc840c1)
- Fix unused-imports issues (ticket-b1fcedf4)
- Fix unused-imports issues (ticket-0c58b2eb)
- Fix ai-boilerplate issues (ticket-5a2f5afd)
- Fix unused-imports issues (ticket-4929ca4c)
- Fix magic-numbers issues (ticket-2e360661)
- Fix unused-imports issues (ticket-679eece0)
- Fix unused-imports issues (ticket-be208cde)
- Fix string-concat issues (ticket-664b458a)
- Fix unused-imports issues (ticket-4567b9ae)
- Fix unused-imports issues (ticket-76569e74)
- Fix string-concat issues (ticket-79f62209)
- Fix unused-imports issues (ticket-6004b866)
- Fix smart-return-type issues (ticket-9f6ed7b5)
- Fix ai-boilerplate issues (ticket-a69fd3bf)
- Fix unused-imports issues (ticket-c4ae863a)
- Fix magic-numbers issues (ticket-83678866)
- Fix smart-return-type issues (ticket-9ec767e1)
- Fix ai-boilerplate issues (ticket-e9609036)
- Fix string-concat issues (ticket-287baf05)
- Fix magic-numbers issues (ticket-824a7ac2)
- Fix smart-return-type issues (ticket-567ceda0)
- Fix unused-imports issues (ticket-5bd5b6f1)
- Fix smart-return-type issues (ticket-8bdf2854)
- Fix smart-return-type issues (ticket-a38cece3)
- Fix smart-return-type issues (ticket-8442617a)
- Fix smart-return-type issues (ticket-009f1de9)
- Fix smart-return-type issues (ticket-1a80cdae)
- Fix smart-return-type issues (ticket-a096e306)
- Fix smart-return-type issues (ticket-c166a9ae)
- Fix unused-imports issues (ticket-c240a48d)
- Fix smart-return-type issues (ticket-d472307e)
- Fix smart-return-type issues (ticket-c00ce508)
- Fix smart-return-type issues (ticket-2f8eb260)
- Fix smart-return-type issues (ticket-e006f308)
- Fix smart-return-type issues (ticket-e1b6dfb6)
- Fix smart-return-type issues (ticket-cb424cb6)
- Fix smart-return-type issues (ticket-a2dd5037)
- Fix smart-return-type issues (ticket-65947156)
- Fix smart-return-type issues (ticket-c503af83)
- Fix smart-return-type issues (ticket-765f08a5)
- Fix relative-imports issues (ticket-5469f7d1)
- Fix smart-return-type issues (ticket-36627607)
- Fix ai-boilerplate issues (ticket-3813271f)
- Fix smart-return-type issues (ticket-780e8124)

## [Unreleased]

### Added
- **touri v0.1** — generic URI-to-capability manifest runtime (`validate`, `list`, `call`); package at `packages/touri/`, example `20_touri_capabilities`, docs `TOURI.md`.
- **ServiceResult envelope** — shared `uri3.results` with `workflow_status` / `execution_status` / `service_result_status`, `ErrorEnvelope`, touri `data_quality` validators; `uri3 explain` for resolution order diagnostics; docs `SERVICE_RESULT.md`, `ANTI_TELLM.md`.
- **Envelope migration** — `uri3 run-workflow` and `uri2ops run` outputs include three-level status fields; touri `fallbacks` in capability manifests; `uri3 replay` for workflow JSONL logs.
- **v0.6.1 flow as primary input** — `nl2uri flow`, `uri3 expand-flow` / `run-flow`, `config/flow_defaults.uri.yaml`, `examples/17_flow_vs_graph/`, `docs/FLOW_FORMAT.md`.
- **v0.6.2 flow defaults registry** — `default_operation_for_uri` reads only `config/flow_defaults.uri.yaml` (scheme defaults, patterns, fallback); expanded patterns for dom/screen/input/hypervisor browser ops.
- **v0.6.3 uri3 → uri2ops delegation** — workflow executor delegates `browser://`, `dom://`, `screen://`, `input://` to uri2ops; uri3 browser adapters deprecated (`URI3_USE_LEGACY_BROWSER=1` escape hatch).
- **v0.6.4 LLM compact flow** — `nl2uri flow --llm` uses dedicated flow planner (`flow_planner_llm`), `flow_repair`, and `validate_expanded_flow`; CLI flags `--repair`, `--validate`, `--expand`.
- **uri3 CLI refactor** — commands split into `uri3/cli/commands/` (`discovery`, `resolve`, `graph`, `workflow`, `flow`); example `18_llm_flow_planner`.
- **uri2flow v0.1** — compact URI flow compiler (`validate`, `expand`, `print`); package at `packages/uri2flow/`, example `15_compact_uri_flow`.
- **v0.6 workflow layer** — uri3: `validate-workflow`, `plan-workflow`, `run-workflow` with mock/Playwright browser adapters and JSONL event log.
- **nl2uri multi-output** — CLI: `plan`, `classify`, `single`, `list`, `tree`, `task`, `graph`; LLM graph planner (`--llm`) with registry injection and graph repair.
- **uri2ops v0.1–v0.5** — standalone operator runtime: operation registry, mock/Playwright/Android/Windows adapters, policy, artifacts, `uri2ops serve` (A2A/MCP), remote registry merge.
- Examples: `10_browser_operator` … `16_llm_graph_planner`.
- Docs: `docs/URI2FLOW.md`, `docs/URI2OPS.md`, updated operator and workflow guides.

### Fixed
- `load_workflow_graph()` accepts in-memory `WorkflowGraph` objects (fixes `uri3 run-workflow` TypeError).
- `pcwin_uri` parsing for netloc+path form (`pcwin://window/Notepad/focus`).

## [0.5.14] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/ANTI_TELLM.md
- Update docs/MARKPACT_WITH_TOURI.md
- Update docs/README.md
- Update docs/SERVICE_RESULT.md
- Update docs/TOURI.md
- ... and 10 more files

### Test
- Update tests/capabilities/weather_forecast/fixtures/blocked/error.html
- Update tests/capabilities/weather_forecast/fixtures/fallback/simple.html
- Update tests/capabilities/weather_forecast/fixtures/good/forecast.html
- Update tests/capabilities/weather_forecast/fixtures/irrelevant/empty.html
- Update tests/capabilities/weather_forecast/test_fixtures.py
- Update tests/touri/test_fallbacks.py
- Update tests/touri/test_markpact_loader.py
- Update tests/touri/test_register.py
- Update tests/touri/test_uri2ops_backend.py
- Update tests/touri/test_uri_flow_backend.py
- ... and 7 more files

### Other
- Update Makefile
- Update app.doql.less
- Update examples/20_touri_capabilities/browser_open_mock.uri.capability.yaml
- Update examples/20_touri_capabilities/check_health_graph.uri.capability.yaml
- Update examples/20_touri_capabilities/weather_flow_dry_run.uri.capability.yaml
- Update examples/21_touri_voice/run.sh
- Update examples/21_touri_voice/stt_mock.uri.capability.yaml
- Update examples/21_touri_voice/touri_examples_voice/__init__.py
- Update examples/21_touri_voice/touri_examples_voice/stt.py
- Update examples/21_touri_voice/touri_examples_voice/tts.py
- ... and 55 more files

## [0.5.13] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/ANTI_TELLM.md
- Update docs/README.md
- Update docs/SERVICE_RESULT.md
- Update docs/TOURI.md
- Update docs/URI3.md
- ... and 9 more files

### Test
- Update tests/touri/test_data_quality.py
- Update tests/touri/test_touri.py
- Update tests/uri3/test_cli.py
- Update tests/uri3/test_explain_uri.py
- Update tests/uri3/test_service_result.py

### Other
- Update Makefile
- Update app.doql.less
- Update config/touri.uri.yaml
- Update examples/18_llm_flow_planner/prompt.txt
- Update examples/18_llm_flow_planner/run.sh
- Update examples/20_touri_capabilities/mock_echo.uri.capability.yaml
- Update examples/20_touri_capabilities/run.sh
- Update examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
- Update integration/touri/Makefile.optional.snippet.mk
- Update integration/touri/pyproject.optional.snippet.toml
- ... and 52 more files

## [0.5.12] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update URI2FLOW_DROPIN_README.md
- Update docs/ARCHITECTURE_V0_5.md
- Update docs/FLOW_FORMAT.md
- Update docs/NL2URI.md
- Update docs/OPERATOR_RUNTIME.md
- ... and 21 more files

### Test
- Update tests/conftest.py
- Update tests/integration/test_flow_to_workflow_execution.py
- Update tests/integration/test_uri3_uri2ops_delegation.py
- Update tests/nl2uri/test_flow_planner.py
- Update tests/nl2uri/test_flow_planner_llm.py
- Update tests/nl2uri/test_flow_repair.py
- Update tests/nl2uri/test_graph_planner.py
- Update tests/test_uri2ops_v01.py
- Update tests/uri2flow/conftest.py
- Update tests/uri2flow/test_cli.py
- ... and 4 more files

### Other
- Update Makefile
- Update app.doql.less
- Update config/flow_defaults.uri.yaml
- Update config/llm.uri.yaml
- Update config/operator_registry.uri.yaml
- Update examples/15_compact_uri_flow/branching.uri.flow.yaml
- Update examples/15_compact_uri_flow/run.sh
- Update examples/15_compact_uri_flow/weather.uri.flow.yaml
- Update examples/17_flow_vs_graph/expanded.expected.uri.graph.yaml
- Update examples/17_flow_vs_graph/run.sh
- ... and 88 more files

## [0.5.11] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/OPERATOR_RUNTIME.md
- Update docs/OPERATOR_SECURITY.md
- Update docs/URI_OPERATION_REGISTRY.md
- Update examples/10_browser_operator/README.md
- Update examples/11_playwright_browser/README.md
- ... and 8 more files

### Test
- Update tests/test_operation_registry.py
- Update tests/test_operator_task.py
- Update tests/test_uri2ops_android.py
- Update tests/test_uri2ops_browser.py
- Update tests/test_uri2ops_pcwin.py
- Update tests/test_uri2ops_serve.py
- Update tests/test_uri2ops_v01.py
- Update tests/uri3/test_workflow_executor.py

### Other
- Update .gitignore
- Update app.doql.less
- Update config/extra_operator_registry.yaml
- Update config/operator_policy.uri.yaml
- Update config/operator_registry.uri.yaml
- Update contracts/proto/operator/browser.proto
- Update contracts/proto/operator/common.proto
- Update contracts/proto/operator/events.proto
- Update contracts/proto/operator/input.proto
- Update contracts/proto/operator/screen.proto
- ... and 63 more files

## [0.5.10] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update examples/13_nl2uri_multi_uri_graph/README.md
- Update examples/14_workflow_executor_mock/README.md
- Update examples/15_playwright_browser/README.md
- Update examples/16_llm_graph_planner/README.md
- Update examples/README.md
- ... and 4 more files

### Test
- Update tests/hypervisor/test_remote_runner.py
- Update tests/nl2uri/test_graph_planner.py
- Update tests/nl2uri/test_graph_planner_llm.py
- Update tests/uri3/test_browser_adapter.py
- Update tests/uri3/test_dispatch.py
- Update tests/uri3/test_workflow_executor.py
- Update tests/uri3/test_workflow_graph.py

### Other
- Update app.doql.less
- Update config/llm.uri.yaml
- Update examples/13_nl2uri_multi_uri_graph/prompt.txt
- Update examples/13_nl2uri_multi_uri_graph/run.sh
- Update examples/14_workflow_executor_mock/run.sh
- Update examples/14_workflow_executor_mock/task_graph.yaml
- Update examples/16_llm_graph_planner/prompt.txt
- Update examples/16_llm_graph_planner/run.sh
- Update output/events/workflows/check-agent-health.jsonl
- Update output/events/workflows/otw-rz-chrome-i-sprawd-localhost-8101-health.jsonl
- ... and 130 more files

## [0.5.9] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/CONFIG_URI_YAML.md
- Update docs/DEPLOYMENT.md
- Update docs/EVOLUTION.md
- Update docs/HYPERVISOR_WORKFLOW.md
- Update docs/NL2A_DOMAIN_PACKS.md
- ... and 17 more files

### Test
- Update tests/hypervisor/test_agent_runner.py
- Update tests/hypervisor/test_config.py
- Update tests/hypervisor/test_deployment_registry.py
- Update tests/hypervisor/test_docker_runner.py
- Update tests/hypervisor/test_hypervisor_cli.py
- Update tests/hypervisor/test_remote_runner.py
- Update tests/hypervisor/test_runtime_state.py
- Update tests/nl2uri/test_domain_planner.py
- Update tests/test_hypervisor.py
- Update tests/uri3/test_cli.py
- ... and 9 more files

### Other
- Update .gitignore
- Update Makefile
- Update app.doql.less
- Update config/deployments.uri.yaml
- Update config/docker.uri.yaml
- Update config/llm.uri.yaml
- Update config/runtime.uri.yaml
- Update config/ssh.uri.yaml
- Update config/uri3.uri.yaml
- Update deployments/agent_deployments.yaml
- ... and 95 more files

## [0.5.8] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update docs/ARCHITECTURE_V0_5.md
- Update docs/AUTO_EVOLUTION_PIPELINE.md
- Update docs/CAPABILITY_VERIFICATION.md
- Update docs/CONTRACT_REGISTRY_SCHEMA.md
- Update docs/DEPLOYMENT.md
- ... and 23 more files

### Test
- Update tests/test_evolution_proposal.py
- Update tests/uri3/test_schema.py

### Other
- Update .code2llm_cache/Makefile_1781432184613035723_1749.pkl
- Update .code2llm_cache/add_invoices_agent_1781425233000000000_580.pkl
- Update .code2llm_cache/add_orders_agent_1781426545000000000_425.pkl
- Update .code2llm_cache/agent_deployments_1781431933935252922_718.pkl
- Update .code2llm_cache/broken_agent_1781425233000000000_259.pkl
- Update .code2llm_cache/cli_1781431834923243695_2370.pkl
- Update .code2llm_cache/cli_1781432111403719486_993.pkl
- Update .code2llm_cache/client_1781431801345590702_1141.pkl
- Update .code2llm_cache/contract_registry.resolved_1781431933967261192_4432.pkl
- Update .code2llm_cache/create_invoices_agent_prompt_1781425233000000000_113.pkl
- ... and 39 more files

## [0.5.7] - 2026-06-14

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update agents/custom/README.md
- Update agents/generated/README.md
- Update agents/generated/user_agent/README.md
- Update agents/generated/weather_map_agent/README.md
- Update examples/01_quickstart_local/README.md
- ... and 7 more files

### Test
- Update testenv/docker-compose.ssh.yml
- Update testenv/ssh_agent_host/Dockerfile
- Update testenv/ssh_agent_host/entrypoint.sh
- Update testenv/ssh_agent_host/mock_agent_server.py
- Update tests/generator/__init__.py
- Update tests/generator/test_headers.py
- Update tests/hypervisor/__init__.py
- Update tests/hypervisor/test_config.py
- Update tests/hypervisor/test_deployment_registry.py
- Update tests/integration/__init__.py
- ... and 2 more files

### Other
- Update VERSION
- Update agents/generated/user_agent/.generated.yaml
- Update agents/generated/user_agent/Dockerfile
- Update agents/generated/user_agent/__init__.py
- Update agents/generated/weather_map_agent/.generated.yaml
- Update agents/generated/weather_map_agent/Dockerfile
- Update agents/generated/weather_map_agent/__init__.py
- Update agents/generated/weather_map_agent/agent_card.py
- Update agents/generated/weather_map_agent/main.py
- Update agents/generated/weather_map_agent/routes.py
- ... and 162 more files

## [0.1.2] - 2026-06-14

### Docs
- Update README.md

### Test
- Update tests/meta_agent/__init__.py
- Update tests/meta_agent/test_repair.py
- Update tests/test_nl2a_v04.py

### Other
- Update deployments/agent_deployments.yaml
- Update hypervisor/deployment_registry/loader.py
- Update hypervisor/deployment_registry/models.py
- Update hypervisor/deployment_registry/writer.py
- Update meta_agent/domain_planner/llm_planner.py
- Update meta_agent/repair.py
- Update meta_agent/repair/__init__.py
- Update meta_agent/repair/loader.py
- Update meta_agent/repair/pipeline.py
- Update meta_agent/repair/rules.py
- ... and 4 more files

## [0.1.1] - 2026-06-14

### Docs
- Update README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/domain_pack/__init__.py
- Update tests/domain_pack/test_generator.py
- Update tests/test_nl2a_v04.py
- Update tests/test_uri2llm_v04.py
- Update tests/uri3/__init__.py
- Update tests/uri3/test_resolvers.py

### Other
- Update generator/verify.py
- Update hypervisor/__init__.py
- Update hypervisor/cli.py
- Update hypervisor/contract_registry/merger.py
- Update hypervisor/domain_pack/__init__.py
- Update hypervisor/domain_pack/generator.py
- Update hypervisor/domain_pack/templates.py
- Update hypervisor/domain_pack/writer.py
- Update hypervisor/uri/client.py
- Update hypervisor/uri2llm/__init__.py
- ... and 34 more files

## [0.1.1] - 2026-06-14

### Docs
- Update README.md
- Update agents/generated/user_agent/README.md
- Update docs/ARCHITECTURE.md
- Update docs/ARCHITECTURE_META_FACTORY.md
- Update docs/AUTO_EVOLUTION_PIPELINE.md
- Update docs/CONTRACTS.md
- Update docs/DEPLOYMENT.md
- Update docs/EVOLUTION.md
- Update docs/GENERATOR.md
- Update docs/META_AGENT.md
- ... and 1 more files

### Test
- Update tests/test_generate.py
- Update tests/test_meta_agent.py
- Update tests/test_runtime_client.py
- Update tests/test_validate.py

### Other
- Update .env.example
- Update .gitignore
- Update .idea/hypervisor.iml
- Update .idea/inspectionProfiles/Project_Default.xml
- Update .idea/inspectionProfiles/profiles_settings.xml
- Update .idea/modules.xml
- Update .idea/vcs.xml
- Update Makefile
- Update VERSION
- Update agents/__init__.py
- ... and 40 more files

## [0.1.1] - 2026-06-14

### Docs
- Update README.md

### Test
- Update tests/__init__.py
- Update tests/test_hypervisor.py

### Other
- Update VERSION
- Update hypervisor/__init__.py
- Update hypervisor/_version.py
- Update hypervisor/cli.py
- Update hypervisor/config.py
- Update hypervisor/core.py
- Update hypervisor/data/nlp2uri.yaml
- Update hypervisor/py.typed
- Update uv.lock

## [0.0.1] - 2026-06-14

### Other
- Update .gitignore
- Update .idea/.gitignore
- Update .idea/hypervisor.iml
- Update nlp2uri.yaml
- Update project.sh
- Update tree.sh

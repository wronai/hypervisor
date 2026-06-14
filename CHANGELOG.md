# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.6] - 2026-06-14

### Added

- `log://` URI scheme in `uri3` for reading and filtering log files.
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
  - `make scan-ssh`,
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


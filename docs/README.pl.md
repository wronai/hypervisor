# Documentation index

## Taskinity WWW (czytelna forma)

Po `make start` lub `urish www serve` (`http://localhost:8788`):

| URL | Opis |
|-----|------|
| [`/www/`](../www/index.html) | Landing — integracje, biuro, oferta |
| [`/www/chat.html`](../www/chat.html) | Chat NL → URI |
| [`/www/przyklady.html`](../www/przyklady.html) | Lab integracji (PASS + komendy) |
| [`/www/docs/examples.html`](../www/docs/examples.html) | **Pełna treść `examples/*/*`** |
| [`/www/demo.html`](../www/demo.html) | Demo URI |

Build docs examples: `make www-docs` · szczegóły: [`www/README.md`](../www/README.md)

## Start here (learning curve)

| Document | Time | Topic |
|----------|------|--------|
| [`GETTING_STARTED.md`](./GETTING_STARTED.md) | 15 min | One CLI, one lifecycle, five paths |
| [`AGENTS_AND_MONITORING.pl.md`](./AGENTS_AND_MONITORING.pl.md) | 15 min | **Agenci, komunikacja, ewolucja, monitoring wielu agentów** |
| [`TUTORIAL_THREE_AGENTS.pl.md`](./TUTORIAL_THREE_AGENTS.pl.md) | 20 min | **3 agenci + czat + gdzie są dane + import markpact** |
| [`TUTORIAL_AGENT_SCHEMA_URI.pl.md`](./TUTORIAL_AGENT_SCHEMA_URI.pl.md) | 20 min | **Nowy agent z NL + schema:// + file/device/robot/cron** |
| [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) | 10 min | **Chat, karty biurowe, batch NL, uri2flow vs NL workflow** |
| [`DESKTOP_AUTONOMY.md`](./DESKTOP_AUTONOMY.md) | 10 min | **Desktop operator: przegladarka, ekran, pcwin, Android przez uri2ops** |
| [`DOMAIN_SEPARATION.md`](./DOMAIN_SEPARATION.md) | reference | Granica bibliotek generycznych i artefaktów domenowych |
| [`MENTAL_MODEL.md`](./MENTAL_MODEL.md) | 5 min | 7 core concepts |
| [`URI_COOKBOOK.md`](./URI_COOKBOOK.md) | reference | “I want to…” recipes |
| [`PROFILES.md`](./PROFILES.md) | 5 min | minimal, dashboard-agent, voice |
| [`ARTIFACT_STANDARD.md`](./ARTIFACT_STANDARD.md) | reference | YAML envelope + statuses |
| [`AUTONOMY_LOOP.md`](./AUTONOMY_LOOP.md) | 10 min | incident → repair → evolution |
| [`DASHBOARD.md`](./DASHBOARD.md) | 10 min | Web UI as system agent |
| [`CLI_REFERENCE.md`](./CLI_REFERENCE.md) | reference | urish commands |

## Install & index

- [`README.md`](../README.md) — instalacja, Makefile, przykłady, `make ci-gate`
- [`examples/README.md`](../examples/README.md) — katalog `examples/*/*`
- [`www/docs/examples.html`](../www/docs/examples.html) — **docs WWW** (README + YAML/SH z examples)
- [`www/przyklady.html`](../www/przyklady.html) — lab integracji na WWW
- [`examples/30_golden_path/`](../examples/30_golden_path/) — 15 min end-to-end tutorial
- [`domains/desktop_ops/`](../domains/desktop_ops/) — generyczny pakiet domenowy desktop operatora
- [`examples/31_office_day/`](../examples/31_office_day/) — biuro: portal, faktury, bank, Android token
- [`examples/33_office_workflows/`](../examples/33_office_workflows/) — karty biurowe landing → URI workflow Touri
- [`CHANGELOG.md`](../CHANGELOG.md) · [`TODO.md`](../TODO.md) · [`DONE.md`](./DONE.md)
- [`CLI_MAP.md`](./CLI_MAP.md) — mapa CLI backendów (poziom 3+)

## Wszystkie pliki `docs/*.md`

| Plik | Temat (skrót) |
|------|----------------|
| [`ANTI_TELLM.md`](./ANTI_TELLM.md) | Safeguards vs tellm-style LLM failures |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Architektura ogólna |
| [`ARCHITECTURE_META_FACTORY.md`](./ARCHITECTURE_META_FACTORY.md) | Meta-factory |
| [`ARCHITECTURE_RUNTIME_AND_TESTING.md`](./ARCHITECTURE_RUNTIME_AND_TESTING.md) | Runtime roles, CI test plan |
| [`ARCHITECTURE_V0_5.md`](./ARCHITECTURE_V0_5.md) | Podział uri3 / nl2uri / uri2ops / hypervisor |
| [`ARTIFACT_STANDARD.md`](./ARTIFACT_STANDARD.md) | YAML envelope + statusy |
| [`AUTONOMY_LOOP.md`](./AUTONOMY_LOOP.md) | incident → repair → evolution |
| [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md) | Agenci, flota, monitoring (EN) |
| [`AGENTS_AND_MONITORING.pl.md`](./AGENTS_AND_MONITORING.pl.md) | Agenci, flota, monitoring (PL) |
| [`AUTO_EVOLUTION_PIPELINE.md`](./AUTO_EVOLUTION_PIPELINE.md) | Kontrolowana autoewolucja |
| [`CAPABILITY_VERIFICATION.md`](./CAPABILITY_VERIFICATION.md) | Weryfikacja capability |
| [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) | Chat NL, scenariusze biurowe, compact flow |
| [`CLI_MAP.md`](./CLI_MAP.md) | Mapa CLI backendów |
| [`CLI_REFERENCE.md`](./CLI_REFERENCE.md) | Komendy urish |
| [`COMPATIBILITY_GOVERNANCE.md`](./COMPATIBILITY_GOVERNANCE.md) | Zasady kompatybilności |
| [`CONFIG_URI_YAML.md`](./CONFIG_URI_YAML.md) | Konwencja `*.uri.yaml` |
| [`CONTRACTS.md`](./CONTRACTS.md) | Format YAML agentów |
| [`CONTRACT_REGISTRY.md`](./CONTRACT_REGISTRY.md) | Registry kontraktów |
| [`CONTRACT_REGISTRY_SCHEMA.md`](./CONTRACT_REGISTRY_SCHEMA.md) | Schema registry |
| [`DASHBOARD.md`](./DASHBOARD.md) | Web UI jako system agent |
| [`DESKTOP_AUTONOMY.md`](./DESKTOP_AUTONOMY.md) | Desktop operator, A2A/MCP, separacja domen |
| [`DOMAIN_SEPARATION.md`](./DOMAIN_SEPARATION.md) | Granica bibliotek generycznych i artefaktów domenowych |
| [`../domains/desktop_ops/README.md`](../domains/desktop_ops/README.md) | Generyczny pakiet domenowy desktop operatora |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | Lokalnie, Docker, run-agent |
| [`DONE.md`](./DONE.md) | Ukończone sprinty / analiza |
| [`EVOLUTION.md`](./EVOLUTION.md) | Evolution proposals |
| [`EXAMPLES_TESTING.md`](./EXAMPLES_TESTING.md) | Kompleksowe testy examples + sondy trybu real |
| [`EXTERNAL_PACKAGES.md`](./EXTERNAL_PACKAGES.md) | Audyt paczek zewnętrznych |
| [`FLOW_FORMAT.md`](./FLOW_FORMAT.md) | Compact URI flow |
| [`GENERATOR.md`](./GENERATOR.md) | Agent factory |
| [`GETTING_STARTED.md`](./GETTING_STARTED.md) | **Start tutaj** (15 min) |
| [`HYPERVISOR_V0_2.md`](./HYPERVISOR_V0_2.md) | Wczesna architektura |
| [`HYPERVISOR_V0_3.md`](./HYPERVISOR_V0_3.md) | Contract registry v0.3 |
| [`HYPERVISOR_V0_4.md`](./HYPERVISOR_V0_4.md) | nl2a, uri2llm |
| [`HYPERVISOR_WORKFLOW.md`](./HYPERVISOR_WORKFLOW.md) | Generacja + run-agent |
| [`MARKPACT_WITH_TOURI.md`](./MARKPACT_WITH_TOURI.md) | markpact:// loader |
| [`MENTAL_MODEL.md`](./MENTAL_MODEL.md) | 7 core concepts |
| [`META_AGENT.md`](./META_AGENT.md) | Meta-agent CLI/API |
| [`NL2A_DOMAIN_PACKS.md`](./NL2A_DOMAIN_PACKS.md) | Domain Pack pipeline |
| [`NL2URI.md`](./NL2URI.md) | Multi-output, task/graph, LLM |
| [`OPERATOR_RUNTIME.md`](./OPERATOR_RUNTIME.md) | validate → plan → run |
| [`OPERATOR_SECURITY.md`](./OPERATOR_SECURITY.md) | Polityka, redaction |
| [`PACKAGE_BOUNDARIES.md`](./PACKAGE_BOUNDARIES.md) | Target package split |
| [`PACKAGE_BOUNDARIES.yaml`](./PACKAGE_BOUNDARIES.yaml) | Import rules (YAML) |
| [`PROFILES.md`](./PROFILES.md) | minimal, dashboard-agent, voice |
| [`ROADMAP.md`](./ROADMAP.md) | v0.6 done + v0.7 plan |
| [`SERVICE_RESULT.md`](./SERVICE_RESULT.md) | Shared result envelope |
| [`STANDARDS.md`](./STANDARDS.md) | MCP, Protobuf, JSON Schema |
| [`TOURI.md`](./TOURI.md) | Capability manifests |
| [`TUTORIAL_AGENT_SCHEMA_URI.pl.md`](./TUTORIAL_AGENT_SCHEMA_URI.pl.md) | Agent-obserwator, `schema://agent`, `file://`, device/robot/cron |
| [`TUTORIAL_AGENT_SCHEMA_URI.md`](./TUTORIAL_AGENT_SCHEMA_URI.md) | EN — checker agent, schema URI, generated collab agent |
| [`URI2FLOW.md`](./URI2FLOW.md) | Compact flow → graph |
| [`URI2LLM.md`](./URI2LLM.md) | → dziś `uri3.resolvers` |
| [`URI2OPS.md`](./URI2OPS.md) | Operator runtime, serve |
| [`URI2RUN_ARCHITECTURE.md`](./URI2RUN_ARCHITECTURE.md) | uri2run transports |
| [`URI3.md`](./URI3.md) | uri3 CLI, workflow, doctor |
| [`URI_COOKBOOK.md`](./URI_COOKBOOK.md) | „I want to…” recipes |
| [`URI_OPERATION_REGISTRY.md`](./URI_OPERATION_REGISTRY.md) | Format operation registry |
| [`VOICE_WITH_TOURI.md`](./VOICE_WITH_TOURI.md) | STT/TTS/voice pack |

## v0.6 (aktualne)

| Dokument | Temat |
|----------|--------|
| [`FLOW_FORMAT.md`](./FLOW_FORMAT.md) | Compact URI flow — format wejściowy |
| [`URI2FLOW.md`](./URI2FLOW.md) | Kompilator compact flow → workflow graph |
| [`URI2OPS.md`](./URI2OPS.md) | Operator runtime, adaptery, `uri2ops serve` |
| [`TOURI.md`](./TOURI.md) | Capability manifests `*.uri.capability.yaml`, backend routing |
| [`MARKPACT_WITH_TOURI.md`](./MARKPACT_WITH_TOURI.md) | `markpact://` capability loader for `touri`, flow loader for `uri2flow` |
| [`EXTERNAL_PACKAGES.md`](./EXTERNAL_PACKAGES.md) | Local `semcod/*` and `wronai/*` package audit and integration boundary |
| [`VOICE_WITH_TOURI.md`](./VOICE_WITH_TOURI.md) | STT/TTS as a `touri` capability pack |
| [`SERVICE_RESULT.md`](./SERVICE_RESULT.md) | Shared result envelope (`workflow_status`, `ErrorEnvelope`) |
| [`ANTI_TELLM.md`](./ANTI_TELLM.md) | Safeguards vs tellm-style LLM/provider failures |
| [`OPERATOR_RUNTIME.md`](./OPERATOR_RUNTIME.md) | Przepływ validate → plan → run |
| [`URI_OPERATION_REGISTRY.md`](./URI_OPERATION_REGISTRY.md) | Format operation registry |
| [`OPERATOR_SECURITY.md`](./OPERATOR_SECURITY.md) | Polityka, redaction, artifact URIs |
| [`NL2URI.md`](./NL2URI.md) | Multi-output, task/graph, LLM planner |
| [`URI3.md`](./URI3.md) | Workflow CLI: `validate/plan/run-workflow` |
| [`ROADMAP.md`](./ROADMAP.md) | v0.6 done + v0.7 plan |
| [`PACKAGE_BOUNDARIES.md`](./PACKAGE_BOUNDARIES.md) | Target package split, sprints, duplicate policy |
| [`PACKAGE_BOUNDARIES.yaml`](./PACKAGE_BOUNDARIES.yaml) | Machine-readable import boundary rules |
| [`URI2RUN_ARCHITECTURE.md`](./URI2RUN_ARCHITECTURE.md) | `uri2run` runtime layer + transport test matrix |
| [`ARCHITECTURE_RUNTIME_AND_TESTING.md`](./ARCHITECTURE_RUNTIME_AND_TESTING.md) | Runtime roles, deficits, CI test plan |
| [`URI3.md`](./URI3.md) | uri3 CLI, `doctor`, `explain`, workflow |

## Pakiet uri2verify

| Dokument | Temat |
|----------|--------|
| [`../packages/uri2verify/README.md`](../packages/uri2verify/README.md) | data quality, replay, capability plans |
| [`SERVICE_RESULT.md`](./SERVICE_RESULT.md) | envelope + verification status fields |

## v0.5

| Dokument | Temat |
|----------|--------|
| [`HYPERVISOR_WORKFLOW.md`](./HYPERVISOR_WORKFLOW.md) | Generacja + run-agent + logi |
| [`CONFIG_URI_YAML.md`](./CONFIG_URI_YAML.md) | Konwencja `*.uri.yaml` |
| [`ARCHITECTURE_V0_5.md`](./ARCHITECTURE_V0_5.md) | Podział uri3 / nl2uri / uri2ops / hypervisor |
| [`NL2A_DOMAIN_PACKS.md`](./NL2A_DOMAIN_PACKS.md) | Domain Pack pipeline |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | Lokalnie, Docker, hypervisor `run-agent` |
| [`META_AGENT.md`](./META_AGENT.md) | Meta-agent CLI/API |
| [`EVOLUTION.md`](./EVOLUTION.md) | Evolution proposals |
| [`AUTO_EVOLUTION_PIPELINE.md`](./AUTO_EVOLUTION_PIPELINE.md) | Kontrolowana autoewolucja |
| [`STANDARDS.md`](./STANDARDS.md) | MCP, Protobuf, JSON Schema |

## Pakiet uri2flow

| Dokument | Temat |
|----------|--------|
| [`../packages/uri2flow/README.md`](../packages/uri2flow/README.md) | CLI, format, pipeline |
| [`../packages/uri2flow/docs/FLOW_FORMAT.md`](../packages/uri2flow/docs/FLOW_FORMAT.md) | Spec compact flow |
| [`../packages/uri2flow/CHANGELOG.md`](../packages/uri2flow/CHANGELOG.md) | Historia v0.1 |

## Pakiet uri2ops

| Dokument | Temat |
|----------|--------|
| [`../packages/uri2ops/README.md`](../packages/uri2ops/README.md) | CLI, adaptery, przykłady |
| [`../packages/uri2ops/CHANGELOG.md`](../packages/uri2ops/CHANGELOG.md) | Historia v0.1–v0.5 |
| [`../packages/uri2ops/TODO.md`](../packages/uri2ops/TODO.md) | Roadmapa pakietu |

## Pakiet touri

| Dokument | Temat |
|----------|--------|
| [`TOURI.md`](./TOURI.md) | Manifesty `*.uri.capability.yaml`, backend routing |
| [`../packages/touri/README.md`](../packages/touri/README.md) | CLI, install, demo |
| [`../packages/touri/CHANGELOG.md`](../packages/touri/CHANGELOG.md) | Historia v0.1 |

## Kontrakty i generator

| Dokument | Temat |
|----------|--------|
| [`CONTRACTS.md`](./CONTRACTS.md) | Format YAML agentów |
| [`GENERATOR.md`](./GENERATOR.md) | Agent factory |
| [`CONTRACT_REGISTRY.md`](./CONTRACT_REGISTRY.md) | Registry kontraktów |
| [`COMPATIBILITY_GOVERNANCE.md`](./COMPATIBILITY_GOVERNANCE.md) | Zasady kompatybilności |
| [`CAPABILITY_VERIFICATION.md`](./CAPABILITY_VERIFICATION.md) | Weryfikacja capability |

## Historyczne

| Dokument | Uwaga |
|----------|--------|
| [`URI2LLM.md`](./URI2LLM.md) | → dziś `uri3.resolvers` |
| [`HYPERVISOR_V0_4.md`](./HYPERVISOR_V0_4.md) | nl2a, uri2llm |
| [`HYPERVISOR_V0_3.md`](./HYPERVISOR_V0_3.md) | contract registry v0.3 |
| [`HYPERVISOR_V0_2.md`](./HYPERVISOR_V0_2.md) | wczesna architektura |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | ogólna architektura |
| [`ARCHITECTURE_META_FACTORY.md`](./ARCHITECTURE_META_FACTORY.md) | meta-factory |

## Makefile (skrót)

```bash
make uri-tree graph nl2a-weather test
make validate generate verify
make meta-repair meta-pipeline
make docker-ssh-up scan-http docker-ssh-down
make evolution-check
make run-weather-agent
```

## Testy

```bash
python -m pytest -q
uri2ops registry validate
```

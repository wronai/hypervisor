# Documentation index

Polish index: [`README.pl.md`](./README.pl.md)

## Taskinity WWW (readable form)

After `make start` or `urish www serve` (`http://localhost:8788`):

| URL | Description |
|-----|-------------|
| [`/www/`](../www/index.html) | Landing — integrations, office, offer |
| [`/www/chat.html`](../www/chat.html) | NL chat → URI plan → run (dry-run default) |
| [`/www/przyklady.html`](../www/przyklady.html) | Integration lab (PASS + commands) |
| [`/www/docs/examples.html`](../www/docs/examples.html) | **Full `examples/*/*` content** |
| [`/www/demo.html`](../www/demo.html) | URI demo |

Build docs examples: `make www-docs` · details: [`www/README.md`](../www/README.md)

## Start here (learning curve)

| Document | Time | Topic |
|----------|------|--------|
| [`GETTING_STARTED.md`](./GETTING_STARTED.md) | 15 min | One CLI, one lifecycle, five paths |
| [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md) | 15 min | **Real agents, communication, evolution, multi-agent monitoring** |
| [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md) | 20 min | **3 agents + chat monitoring + data paths + markpact import** |
| [`TUTORIAL_AGENT_SCHEMA_URI.md`](./TUTORIAL_AGENT_SCHEMA_URI.md) | 20 min | **NL-generated agent + schema:// + file/device/robot/cron** |
| [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) | 10 min | **Chat, office cards, batch NL, uri2flow vs NL workflow** |
| [`DESKTOP_AUTONOMY.md`](./DESKTOP_AUTONOMY.md) | 10 min | **Desktop operator agent: browser, screen, pcwin, Android via uri2ops** |
| [`PHYSICAL_AUTONOMY.md`](./PHYSICAL_AUTONOMY.md) | 10 min | **Robot/device URIs: robot://, device://, safety gates** |
| [`DOMAIN_SEPARATION.md`](./DOMAIN_SEPARATION.md) | reference | Generic package vs domain artifact boundary |
| [`EXAMPLES_TESTING.md`](./EXAMPLES_TESTING.md) | reference | **Comprehensive examples test matrix + real-mode probes** |
| [`MENTAL_MODEL.md`](./MENTAL_MODEL.md) | 5 min | 7 core concepts |
| [`SYSTEM_MAP.md`](./SYSTEM_MAP.md) | 10 min | Current structure from `project/map.toon.yaml` |
| [`URI_COOKBOOK.md`](./URI_COOKBOOK.md) | reference | “I want to…” recipes |
| [`PROFILES.md`](./PROFILES.md) | 5 min | minimal, dashboard-agent, voice |
| [`ARTIFACT_STANDARD.md`](./ARTIFACT_STANDARD.md) | reference | YAML envelope + statuses |
| [`AUTONOMY_LOOP.md`](./AUTONOMY_LOOP.md) | 10 min | incident → repair → evolution |
| [`DASHBOARD.md`](./DASHBOARD.md) | 10 min | Web UI as system agent |
| [`CLI_REFERENCE.md`](./CLI_REFERENCE.md) | reference | urish commands |

## Install & index

- [`README.md`](../README.md) — install, Makefile, examples, `make ci-gate`
- [`examples/README.md`](../examples/README.md) — `examples/*/*` catalog
- [`www/docs/examples.html`](../www/docs/examples.html) — **WWW docs** (README + YAML/SH from examples)
- [`www/przyklady.html`](../www/przyklady.html) — integration lab on WWW
- [`examples/30_golden_path/`](../examples/30_golden_path/) — 15 min end-to-end tutorial
- [`domains/desktop_ops/`](../domains/desktop_ops/) — generic desktop operator domain pack
- [`domains/physical_ops/`](../domains/physical_ops/) — generic robot/device operator domain pack
- [`examples/31_office_day/`](../examples/31_office_day/) — office: portal, invoices, bank, Android token
- [`examples/33_office_workflows/`](../examples/33_office_workflows/) — landing office cards → Touri workflow URIs
- [`CHANGELOG.md`](../CHANGELOG.md) · [`TODO.md`](../TODO.md) · [`DONE.md`](./DONE.md)
- [`CLI_MAP.md`](./CLI_MAP.md) — CLI backend map (level 3+)

## All `docs/*.md` files

| File | Topic (summary) |
|------|-----------------|
| [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md) | Real agents, fleet communication, repair/evolve, monitoring tools |
| [`AGENTS_AND_MONITORING.pl.md`](./AGENTS_AND_MONITORING.pl.md) | PL summary — agenci, komunikacja, monitoring |
| [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md) | Step-by-step: 3 agents, storage map, markpact export |
| [`TUTORIAL_THREE_AGENTS.pl.md`](./TUTORIAL_THREE_AGENTS.pl.md) | PL — tutorial 3 agentów + markpact |
| [`TUTORIAL_AGENT_SCHEMA_URI.md`](./TUTORIAL_AGENT_SCHEMA_URI.md) | Checker agent, `schema://agent`, generated collab agent |
| [`TUTORIAL_AGENT_SCHEMA_URI.pl.md`](./TUTORIAL_AGENT_SCHEMA_URI.pl.md) | PL — agent-obserwator, `file://`, device/robot/cron |
| [`ANTI_TELLM.md`](./ANTI_TELLM.md) | Safeguards vs tellm-style LLM failures |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | General architecture |
| [`ARCHITECTURE_META_FACTORY.md`](./ARCHITECTURE_META_FACTORY.md) | Meta-factory |
| [`ARCHITECTURE_RUNTIME_AND_TESTING.md`](./ARCHITECTURE_RUNTIME_AND_TESTING.md) | Runtime roles, CI test plan |
| [`ARCHITECTURE_V0_5.md`](./ARCHITECTURE_V0_5.md) | uri3 / nl2uri / uri2ops / hypervisor split |
| [`ARTIFACT_STANDARD.md`](./ARTIFACT_STANDARD.md) | YAML envelope + statuses |
| [`AUTONOMY_LOOP.md`](./AUTONOMY_LOOP.md) | incident → repair → evolution |
| [`AUTO_EVOLUTION_PIPELINE.md`](./AUTO_EVOLUTION_PIPELINE.md) | Controlled auto-evolution |
| [`CAPABILITY_VERIFICATION.md`](./CAPABILITY_VERIFICATION.md) | Capability verification |
| [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) | Chat NL → URI, office scenarios, compact flow |
| [`CLI_MAP.md`](./CLI_MAP.md) | CLI backend map |
| [`CLI_REFERENCE.md`](./CLI_REFERENCE.md) | urish commands |
| [`COMPATIBILITY_GOVERNANCE.md`](./COMPATIBILITY_GOVERNANCE.md) | Compatibility rules |
| [`CONFIG_URI_YAML.md`](./CONFIG_URI_YAML.md) | `*.uri.yaml` convention |
| [`CONTRACTS.md`](./CONTRACTS.md) | Agent YAML format |
| [`CONTRACT_REGISTRY.md`](./CONTRACT_REGISTRY.md) | Contract registry |
| [`CONTRACT_REGISTRY_SCHEMA.md`](./CONTRACT_REGISTRY_SCHEMA.md) | Registry schema |
| [`DASHBOARD.md`](./DASHBOARD.md) | Web UI as system agent |
| [`DESKTOP_AUTONOMY.md`](./DESKTOP_AUTONOMY.md) | Desktop operator agent, A2A/MCP, domain separation |
| [`DOMAIN_SEPARATION.md`](./DOMAIN_SEPARATION.md) | Generic package vs domain artifact boundary |
| [`../domains/desktop_ops/README.md`](../domains/desktop_ops/README.md) | Generic desktop operator domain pack |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | Local, Docker, run-agent |
| [`DONE.md`](./DONE.md) | Completed sprints / analysis |
| [`EVOLUTION.md`](./EVOLUTION.md) | Evolution proposals |
| [`EXTERNAL_PACKAGES.md`](./EXTERNAL_PACKAGES.md) | External package audit |
| [`FLOW_FORMAT.md`](./FLOW_FORMAT.md) | Compact URI flow |
| [`GENERATOR.md`](./GENERATOR.md) | Agent factory |
| [`GETTING_STARTED.md`](./GETTING_STARTED.md) | **Start here** (15 min) |
| [`HYPERVISOR_V0_2.md`](./HYPERVISOR_V0_2.md) | Early architecture |
| [`HYPERVISOR_V0_3.md`](./HYPERVISOR_V0_3.md) | Contract registry v0.3 |
| [`HYPERVISOR_V0_4.md`](./HYPERVISOR_V0_4.md) | nl2a, uri2llm |
| [`HYPERVISOR_WORKFLOW.md`](./HYPERVISOR_WORKFLOW.md) | Generation + run-agent |
| [`MARKPACT_WITH_TOURI.md`](./MARKPACT_WITH_TOURI.md) | markpact:// loader |
| [`MENTAL_MODEL.md`](./MENTAL_MODEL.md) | 7 core concepts |
| [`META_AGENT.md`](./META_AGENT.md) | Meta-agent CLI/API |
| [`NL2A_DOMAIN_PACKS.md`](./NL2A_DOMAIN_PACKS.md) | Domain Pack pipeline |
| [`NL2URI.md`](./NL2URI.md) | Multi-output, task/graph, LLM |
| [`OPERATOR_RUNTIME.md`](./OPERATOR_RUNTIME.md) | validate → plan → run |
| [`OPERATOR_SECURITY.md`](./OPERATOR_SECURITY.md) | Policy, redaction |
| [`PACKAGE_BOUNDARIES.md`](./PACKAGE_BOUNDARIES.md) | Target package split |
| [`PACKAGE_BOUNDARIES.yaml`](./PACKAGE_BOUNDARIES.yaml) | Import rules (YAML) |
| [`PHYSICAL_AUTONOMY.md`](./PHYSICAL_AUTONOMY.md) | Robot/device URIs, physical safety gates, adapters |
| [`PROFILES.md`](./PROFILES.md) | minimal, dashboard-agent, voice |
| [`ROADMAP.md`](./ROADMAP.md) | v0.6 done + v0.7 plan |
| [`SERVICE_RESULT.md`](./SERVICE_RESULT.md) | Shared result envelope |
| [`STANDARDS.md`](./STANDARDS.md) | MCP, Protobuf, JSON Schema |
| [`SYSTEM_MAP.md`](./SYSTEM_MAP.md) | Current structural map, hotspots and maintenance rules |
| [`TOURI.md`](./TOURI.md) | Capability manifests |
| [`URI2FLOW.md`](./URI2FLOW.md) | Compact flow → graph |
| [`URI2LLM.md`](./URI2LLM.md) | → today `uri3.resolvers` |
| [`URI2OPS.md`](./URI2OPS.md) | Operator runtime, serve |
| [`URI2RUN_ARCHITECTURE.md`](./URI2RUN_ARCHITECTURE.md) | uri2run transports |
| [`URI3.md`](./URI3.md) | uri3 CLI, workflow, doctor |
| [`URI_COOKBOOK.md`](./URI_COOKBOOK.md) | “I want to…” recipes |
| [`URI_OPERATION_REGISTRY.md`](./URI_OPERATION_REGISTRY.md) | Operation registry format |
| [`VOICE_WITH_TOURI.md`](./VOICE_WITH_TOURI.md) | STT/TTS/voice pack |

## v0.6 (current)

| Document | Topic |
|----------|--------|
| [`FLOW_FORMAT.md`](./FLOW_FORMAT.md) | Compact URI flow — input format |
| [`URI2FLOW.md`](./URI2FLOW.md) | Compact flow → workflow graph compiler |
| [`URI2OPS.md`](./URI2OPS.md) | Operator runtime, adapters, `uri2ops serve` |
| [`TOURI.md`](./TOURI.md) | Capability manifests `*.uri.capability.yaml`, backend routing |
| [`MARKPACT_WITH_TOURI.md`](./MARKPACT_WITH_TOURI.md) | `markpact://` capability loader for `touri`, flow loader for `uri2flow` |
| [`EXTERNAL_PACKAGES.md`](./EXTERNAL_PACKAGES.md) | Local `semcod/*` and `wronai/*` package audit and integration boundary |
| [`VOICE_WITH_TOURI.md`](./VOICE_WITH_TOURI.md) | STT/TTS as a `touri` capability pack |
| [`SERVICE_RESULT.md`](./SERVICE_RESULT.md) | Shared result envelope (`workflow_status`, `ErrorEnvelope`) |
| [`ANTI_TELLM.md`](./ANTI_TELLM.md) | Safeguards vs tellm-style LLM/provider failures |
| [`OPERATOR_RUNTIME.md`](./OPERATOR_RUNTIME.md) | validate → plan → run flow |
| [`URI_OPERATION_REGISTRY.md`](./URI_OPERATION_REGISTRY.md) | Operation registry format |
| [`OPERATOR_SECURITY.md`](./OPERATOR_SECURITY.md) | Policy, redaction, artifact URIs |
| [`NL2URI.md`](./NL2URI.md) | Multi-output, task/graph, LLM planner |
| [`URI3.md`](./URI3.md) | Workflow CLI: `validate/plan/run-workflow` |
| [`ROADMAP.md`](./ROADMAP.md) | v0.6 done + v0.7 plan |
| [`PACKAGE_BOUNDARIES.md`](./PACKAGE_BOUNDARIES.md) | Target package split, sprints, duplicate policy |
| [`PACKAGE_BOUNDARIES.yaml`](./PACKAGE_BOUNDARIES.yaml) | Machine-readable import boundary rules |
| [`URI2RUN_ARCHITECTURE.md`](./URI2RUN_ARCHITECTURE.md) | `uri2run` runtime layer + transport test matrix |
| [`ARCHITECTURE_RUNTIME_AND_TESTING.md`](./ARCHITECTURE_RUNTIME_AND_TESTING.md) | Runtime roles, deficits, CI test plan |
| [`URI3.md`](./URI3.md) | uri3 CLI, `doctor`, `explain`, workflow |

## uri2verify package

| Document | Topic |
|----------|--------|
| [`../packages/uri2verify/README.md`](../packages/uri2verify/README.md) | data quality, replay, capability plans |
| [`SERVICE_RESULT.md`](./SERVICE_RESULT.md) | envelope + verification status fields |

## v0.5

| Document | Topic |
|----------|--------|
| [`HYPERVISOR_WORKFLOW.md`](./HYPERVISOR_WORKFLOW.md) | Generation + run-agent + logs |
| [`CONFIG_URI_YAML.md`](./CONFIG_URI_YAML.md) | `*.uri.yaml` convention |
| [`ARCHITECTURE_V0_5.md`](./ARCHITECTURE_V0_5.md) | uri3 / nl2uri / uri2ops / hypervisor split |
| [`NL2A_DOMAIN_PACKS.md`](./NL2A_DOMAIN_PACKS.md) | Domain Pack pipeline |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | Local, Docker, hypervisor `run-agent` |
| [`META_AGENT.md`](./META_AGENT.md) | Meta-agent CLI/API |
| [`EVOLUTION.md`](./EVOLUTION.md) | Evolution proposals |
| [`AUTO_EVOLUTION_PIPELINE.md`](./AUTO_EVOLUTION_PIPELINE.md) | Controlled auto-evolution |
| [`STANDARDS.md`](./STANDARDS.md) | MCP, Protobuf, JSON Schema |

## uri2flow package

| Document | Topic |
|----------|--------|
| [`../packages/uri2flow/README.md`](../packages/uri2flow/README.md) | CLI, format, pipeline |
| [`../packages/uri2flow/docs/FLOW_FORMAT.md`](../packages/uri2flow/docs/FLOW_FORMAT.md) | Compact flow spec |
| [`../packages/uri2flow/CHANGELOG.md`](../packages/uri2flow/CHANGELOG.md) | v0.1 history |

## uri2ops package

| Document | Topic |
|----------|--------|
| [`../packages/uri2ops/README.md`](../packages/uri2ops/README.md) | CLI, adapters, examples |
| [`../packages/uri2ops/CHANGELOG.md`](../packages/uri2ops/CHANGELOG.md) | v0.1–v0.5 history |
| [`../packages/uri2ops/TODO.md`](../packages/uri2ops/TODO.md) | Package roadmap |

## touri package

| Document | Topic |
|----------|--------|
| [`TOURI.md`](./TOURI.md) | Manifests `*.uri.capability.yaml`, backend routing |
| [`../packages/touri/README.md`](../packages/touri/README.md) | CLI, install, demo |
| [`../packages/touri/CHANGELOG.md`](../packages/touri/CHANGELOG.md) | v0.1 history |

## Contracts and generator

| Document | Topic |
|----------|--------|
| [`CONTRACTS.md`](./CONTRACTS.md) | Agent YAML format |
| [`GENERATOR.md`](./GENERATOR.md) | Agent factory |
| [`CONTRACT_REGISTRY.md`](./CONTRACT_REGISTRY.md) | Contract registry |
| [`COMPATIBILITY_GOVERNANCE.md`](./COMPATIBILITY_GOVERNANCE.md) | Compatibility rules |
| [`CAPABILITY_VERIFICATION.md`](./CAPABILITY_VERIFICATION.md) | Capability verification |

## Historical

| Document | Note |
|----------|--------|
| [`URI2LLM.md`](./URI2LLM.md) | → today `uri3.resolvers` |
| [`HYPERVISOR_V0_4.md`](./HYPERVISOR_V0_4.md) | nl2a, uri2llm |
| [`HYPERVISOR_V0_3.md`](./HYPERVISOR_V0_3.md) | contract registry v0.3 |
| [`HYPERVISOR_V0_2.md`](./HYPERVISOR_V0_2.md) | early architecture |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | general architecture |
| [`ARCHITECTURE_META_FACTORY.md`](./ARCHITECTURE_META_FACTORY.md) | meta-factory |

## Makefile (short)

```bash
make uri-tree graph nl2a-weather test
make validate generate verify
make meta-repair meta-pipeline
make docker-ssh-up scan-http docker-ssh-down
make evolution-check
make run-weather-agent
```

## Tests

```bash
python -m pytest -q
uri2ops registry validate
```

# System map

Source: [`project/map.toon.yaml`](../project/map.toon.yaml), generated 2026-06-15.

This document is the human-readable snapshot of the current system shape. Treat
`project/map.toon.yaml` as the machine source of truth and this file as the
navigation layer for maintainers.

## Current Snapshot

| Metric | Value |
|--------|-------|
| Modules | 731 |
| Lines | 49448 |
| Functions | 2269 |
| Classes | 0, because the map generator reports function-oriented exports; dataclass-like entries are listed in details |
| Average cyclomatic complexity | 3.7 |
| Critical functions | 7 |
| Dependency cycles | 0 |
| Trend | flat: 3.7 -> 3.7 |

Interpretation: the project is broad, but the dependency graph is currently
acyclic and average complexity is under the budget documented in
[`URI2RUN_ARCHITECTURE.md`](./URI2RUN_ARCHITECTURE.md). The main risk is not
cycle growth; it is fan-out in orchestration modules and large UI/runtime files.

## Main Runtime Layers

| Layer | Main paths | Responsibility |
|-------|------------|----------------|
| URI core | `packages/uri3/uri3/` | URI schemes, resolver dispatch, workflow graph, logs, doctor, result envelopes |
| NL planning | `packages/nl2uri/nl2uri/` | Natural language to URI, task, flow and graph plans |
| Flow compiler | `packages/uri2flow/uri2flow/` | Compact URI flow to workflow graph, including `markpact://` flow loading |
| Operation runtime | `packages/uri2ops/uri2ops/` | Browser, Android, PC/Windows operation registry and A2A/MCP server |
| Runtime transports | `packages/uri2run/uri2run/` | Python, shell, HTTP, stdio, SSE, WS, Docker, SSH, MCP, A2A, flow and graph transports |
| Capabilities | `packages/touri/touri/` | Capability manifests, matching, fallback and delegation to runtime backends |
| Agent lifecycle | `packages/resource-agent-hypervisor/hypervisor/deployment_registry/` | Deployment registry, run plans, process lifecycle, health, runtime state, supervisor |
| Repair loop | `packages/resource-agent-hypervisor/hypervisor/repair/` | Diagnose, classify, plan, apply playbooks, learn from incidents |
| Agent generation | `packages/resource-agent-factory/generator/` and `agents/generated/*` | Deterministic thin agents from contracts |
| Ecosystem generation | `packages/urigen/urigen/` | Proposal, generated ecosystem, verify, explain, apply, rollback |
| URI shell | `packages/urish/urish/` | User-facing `uri` / `urish` commands, policy, shortcuts, dashboard, repair, ticket/evolve |
| Dashboard agent | `packages/hypervisor-dashboard-agent/` | API and system-agent UI for observing and controlling hypervisor flows |
| WWW product UI | `www/` | Landing, markdown chat, examples gallery, API bridge, monitor scripts |

## Critical Paths

### NL To Runnable Agent

```text
prompt
  -> urish ask / nl2uri
  -> URI plan or ecosystem proposal
  -> urigen generate or nl2a domain pack
  -> contracts + deployment fragment
  -> generator creates agents/generated/*
  -> hypervisor run-agent
  -> inspect / supervise / repair
```

### URI Execution

```text
uri / urish
  -> policy gate
  -> uri3 explain / resolve / workflow
  -> touri capability match when a capability manifest exists
  -> uri2run transport or uri2ops operation adapter
  -> result envelope with workflow_status, execution_status, service_result_status
```

### Self-Healing Agent Runtime

```text
hypervisor inspect-agent
  -> runtime_state + PID check
  -> /health probe
  -> agent card probe
  -> hypervisor log + process log
  -> readiness report
  -> repair diagnose
  -> prioritized repair plan
  -> repair apply
  -> re-inspect after every playbook
```

Important separation:

- `process_status` answers whether the tracked PID is alive.
- `health_status` answers whether the service responds correctly.
- `warning_codes` are non-blocking drift signals.
- `incident_codes` are blocking failures used by the repair planner.

## Structural Hotspots

The map reports these current hotspots:

| Hotspot | Signal | Recommended handling |
|---------|--------|----------------------|
| `createVoiceController` | fan-out 37, CC 29 | Split chat voice UI setup from event binding and API calls |
| `generate_ecosystem` | fan-out 23 | Prefer smaller artifact builders and validators |
| `parse_duplication` | fan-out 23 | Keep TOON parsing small and covered by fixture tests |
| `register_call_commands` | fan-out 22 | Keep command registration declarative; avoid adding runtime logic here |
| `register_ecosystem_commands` | fan-out 21 | Split urigen formatting/policy helpers before adding behavior |

## Largest Files To Watch

| File | Lines | Note |
|------|-------|------|
| `planfile.yaml` | 1319 | Task backlog and generated tickets |
| `www/landing.js` | 835 | Product UI tour, language/theme handling, animation, scenario lab |
| `www/landing-i18n.js` | 719 | Landing copy and language resources |
| `packages/resource-agent-hypervisor/hypervisor/deployment_registry/lifecycle.py` | 640 | Agent run/stop/restart/status lifecycle |
| `www/app.js` | 613 | Chat and UI behavior |
| `goal.yaml` | 511 | Goal/test workflow metadata |
| `packages/resource-agent-hypervisor/hypervisor/cli.py` | 495 | Hypervisor CLI |
| `scripts/examples/effective_weather_playwright.py` | 439 | Example browser workflow |
| `packages/hypervisor-dashboard-agent/hypervisor_dashboard_agent/uri_client.py` | 429 | Dashboard URI bridge |
| `packages/nl2uri/nl2uri/graph_planner.py` | 414 | NL graph planning defaults |

## Entry Points Worth Knowing

| Entry point | Purpose |
|-------------|---------|
| `uri` / `urish` | Primary human shell for ask, call, run, repair, ticket, evolve, dashboard |
| `uri3` | URI resolver, workflow, doctor, logs, schema, replay |
| `uri2run` | Runtime transport calls |
| `uri2ops` | Operator task validation, execution and serve mode |
| `touri` | Capability registry validation and capability calls |
| `urigen` | URI ecosystem proposal/generate/verify/explain/apply |
| `hypervisor` | Deployment registry, lifecycle, inspect, supervise, repair |
| `scripts/test-all-examples.sh` | Sequential shell smoke for examples |
| `make ci-gate` | Architecture gate, pytest and examples integration |

## Maintenance Rules

1. Keep generated agents thin. Edit contracts, templates or custom handlers, not
   `agents/generated/*` directly.
2. Keep CLI modules thin. When fan-out rises, move behavior into backend modules
   or declarative registries.
3. Keep `uri3` as the resolver/workflow core. Runtime execution belongs in
   `uri2run` or `uri2ops`.
4. Keep repair bounded and observable. Every autonomous repair must leave
   runtime state, logs, incidents or proposals.
5. Keep `warning_codes` out of blocking repair decisions unless the service is
   actually unhealthy.
6. When changing `www/landing.js` or `www/app.js`, run the WWW smoke and monitor
   tests because those files are now system-facing UX surfaces.

## Verification Commands

```bash
python -m pytest -q tests/hypervisor/test_runtime_state.py \
  tests/hypervisor/test_agent_runner.py \
  tests/hypervisor/test_sprint1_autonomy.py \
  tests/hypervisor/test_agent_lifecycle.py

python -m ruff check packages/resource-agent-hypervisor/hypervisor \
  packages/uri3 packages/uri2run packages/urish tests/hypervisor

uri3 doctor
make examples-test
bash scripts/test-all-examples.sh
```

Use the narrow hypervisor test set while editing lifecycle or repair behavior.
Use `uri3 doctor` and `make examples-test` before publishing or changing public
contracts.

## Responsibility Audit

Use the planning audit when deciding the next refactor slice from the generated
TOON snapshots:

```bash
make architecture-responsibility-audit
python scripts/architecture_responsibility_audit.py --format json --out output/architecture-responsibility-audit.json
```

The script reads `project/map.toon.yaml` and `project/duplication.toon.yaml`,
classifies files into system, app, command, domain, runtime, generated and docs
areas, then reports:

- generic packages containing domain vocabulary,
- duplication crossing responsibility boundaries,
- generated snapshots that duplicate source packages,
- large command/app/runtime files that should be split before adding behavior.

It is report-only by default. Use `--fail-on warning` only after known legacy
findings are converted into explicit refactor tasks or exceptions.

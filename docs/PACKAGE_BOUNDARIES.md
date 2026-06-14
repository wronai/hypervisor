# Package boundaries and refactor roadmap

This document captures the target architecture for splitting the hypervisor monorepo
without adding new features first. Implementation status is noted per sprint.

## Principles

1. **uri3** = URI core, graph, replay, result envelope (foundation)
2. **uri2ops** = operator runtime (browser, OS, Android, PCWin)
3. **touri** = capability registry + dispatch (not voice/publish/verify)
4. **nl2uri** = prompt → URI plan (no execution)
5. **hypervisor** = policy, lifecycle, deployment, contract registry
6. **One result envelope** — all packages return `uri3.results` / `ServiceResult` shape

## Target package map

```txt
packages/
  uri3                  # URI core, resolver, graph, replay, envelope
  uri2flow              # compact flow → workflow graph
  uri2ops               # operator runtime
  touri                 # capability registry/runtime
  nl2uri                # prompt → URI/flow/graph
  hypervisor-core       # policy, lifecycle, deployment (future split from resource-agent-hypervisor)
  hypervisor-cli        # Typer commands (future split)
  agent-meta            # meta-agent, repair, evolution (future split)
  domainpack            # domain pack generator (future split from hypervisor/domain_pack)
  agentfactory          # resource-agent-factory (rename target)
  uri2voice             # STT/TTS/audio/wake (Sprint 2)
  uri2pact              # markpact/pactown/import (Sprint 3)
  uri2verify            # data quality, replay, fixtures (Sprint 3)
  uri2repair            # iterun-style repair loop (Sprint 5)
  uri2policy            # shared policy gate (later)
```

## Sprint 1 — split hotspots (done)

| Module | Split into |
|--------|------------|
| `nl2uri/flow_repair.py` | `flow_helpers`, `flow_extract`, `flow_sanitize`, `flow_step_ids`, `flow_repair` |
| `uri2ops/server/app.py` | `server/routes/{health,registry,tasks,a2a,mcp}.py` |
| `uri3/graph/graph_executor.py` | `execution_plan`, `step_runner`, `event_emitter`, `graph_executor` |
| `touri/executor.py` | `backend_dispatch`, `fallbacks`, `executor` |

Duplicates marked:

- `packages/uri3/domains/weather_map/` → canonical is `domains/weather_map/`
- `uri3/graph/adapters/browser_*` → deprecated; target is uri2ops via `uri2ops_adapter`

## Sprint 2 — uri2voice (done)

Move voice execution from `examples/21_touri_voice/touri_examples_voice/` into `packages/uri2voice`.
`touri` keeps capability manifests; handlers target `python://uri2voice.*`.

## Sprint 3 — uri2pact (done)

Merge duplicate markpact loaders into `packages/uri2pact`. `touri` and `uri2flow` import from `uri2pact`.

## Sprint 3b — uri2verify (done)

```txt
touri/data_quality.py        → uri2verify/data_quality.py (+ touri wrapper)
uri3/graph/replay.py         → uri2verify/replay.py (+ compatibility shim)
hypervisor/verifier/         → uri2verify/capability_plan.py (+ wrapper)
```

## Sprint 4 — governance tools (done)

```bash
uri3 doctor          # config, registries, envelope consistency
uri3 explain <uri>   # scheme, backend, policy, fallbacks, verification hints
touri explain <uri>  # thin wrapper over uri3 explain
.registry/           # uri_index, capability_index, operation_index (via uri3 doctor --build-registry)
```

Implemented:

- `uri3 doctor` — static checks for config, contract registry, touri/uri2ops registries, explain smoke, envelope exports
- `uri3 doctor --capability-plan` / `--replay-failures` — optional uri2verify integration
- `uri3 doctor --build-registry` — writes `.registry/*.json` indexes
- `uri3 doctor --migrate-envelope` — backfills status fields in legacy workflow JSONL logs
- `uri3 explain` extended — fallbacks, data_quality, uri2verify verification hints
- `touri explain <uri>` — delegates to `uri3.resolvers.explain.explain_uri`
- `WorkflowCompleted` events now include `workflow_status`, `execution_status`, `service_result_status`

## Sprint 5 — `uri2run` + architecture tests (next)

See [`URI2RUN_ARCHITECTURE.md`](./URI2RUN_ARCHITECTURE.md) and [`ARCHITECTURE_RUNTIME_AND_TESTING.md`](./ARCHITECTURE_RUNTIME_AND_TESTING.md).

Sprint A (done in repo):

```txt
tests/architecture/test_import_boundaries.py
tests/architecture/test_result_envelope_contract.py
tests/architecture/test_explain_contract.py
tests/architecture/test_doctor_contract.py
docs/PACKAGE_BOUNDARIES.yaml
```

Sprint B (planned):

```txt
packages/uri2run — python/shell/http/flow/graph transports
touri/backend_dispatch -> uri2run.run_backend (wrappers)
uri3 explain.runtime_transport -> uri2run:* when migrated
```

## Result envelope (mandatory standard)

All execution paths should return:

```json
{
  "ok": true,
  "workflow_status": "completed",
  "execution_status": "completed",
  "service_result_status": "succeeded",
  "result_type": "artifact",
  "data": {},
  "artifact_uri": null,
  "errors": [],
  "warnings": [],
  "meta": {}
}
```

Implement in `uri3.results` (or future `uri3-contracts`) and enforce via `uri2verify`.

## What not to duplicate

| Keep one copy | Remove/limit |
|---------------|--------------|
| `agents/generated/` (repo root) | `packages/resource-agent-factory/agents/generated/` (fixtures only) |
| `domains/*/` (repo root) | `packages/uri3/domains/` (legacy imports) |
| `uri2ops` browser adapters | `uri3/graph/adapters/browser_*` (deprecated) |

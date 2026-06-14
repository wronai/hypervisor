# CLI map — which command to use for what

Quick reference for the hypervisor monorepo CLIs.

| Goal | Command | Package |
|------|---------|---------|
| Plan NL → task graph / flow / graph | `nl2uri plan …` | nl2uri |
| Generate agent from contract | `nl2a generate …` | nl2uri |
| Expand compact URI flow → workflow graph | `uri2flow expand …` | uri2flow |
| Validate / dry-run / run workflow graph | `uri3 run-workflow …` | uri3 |
| Explain URI resolution (registry, backend, transport) | `uri3 explain … --json` | uri3 |
| Governance: config, registries, boundaries, envelope | `uri3 doctor --json` | uri3 |
| Replay workflow JSONL logs | `uri3 replay …` | uri3 |
| Call capability via manifest registry | `touri call … --registry …` | touri |
| List / validate capability manifests | `touri list`, `touri validate` | touri |
| Execute runtime transport directly | `uri2run call …` | uri2run |
| Operator task (browser/OS) plan/run | `uri2ops plan`, `uri2ops run` | uri2ops |
| Data quality / capability test plan / replay checks | `uri2verify …` | uri2verify |
| Agent lifecycle (local/docker/ssh) | `hypervisor deployments`, `hypervisor run-agent`, `hypervisor agent-status` | hypervisor |
| Agent supervision / repair loop | `hypervisor inspect-agent`, `hypervisor supervise` | hypervisor |

## Typical flows

### Weather capability (touri + uri2run)

```bash
uri3 explain weather://forecast/Gdansk/14/html --json
touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
```

### NL → flow → graph → dry-run

```bash
nl2uri plan "wygeneruj agenta pogodowego…" --kind uri_flow --out output/weather.uri.flow.yaml
uri2flow expand output/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri3 run-workflow output/weather.uri.graph.yaml --dry-run
```

### Architecture health check

```bash
make architecture-gate   # pytest tests/architecture + uri3 doctor
make ci-gate             # architecture-gate + full pytest -q
pytest tests/architecture -q
uri3 doctor --json
```

CI (GitHub Actions): `.github/workflows/ci.yml` runs `scripts/ci/architecture_gate.sh` before the full suite.

### Agent supervision

```bash
hypervisor run-agent weather-map-agent.local --detach --if-running reuse
hypervisor run-agent weather-map-agent.local --detach --wait-healthy --supervise-repair auto
hypervisor inspect-agent weather-map-agent.local
hypervisor supervise weather-map-agent.local --repair auto
```

`inspect-agent` reports process liveness, health endpoint status, agent card
probe, recent `log://` errors and incident codes. `supervise` keeps the loop
bounded: inspect first, optionally sync runtime health URI or restart, inspect
again.

## Runtime layering

```txt
touri      → picks capability + policy + fallbacks
uri2run    → executes transport (python/shell/http/docker/…)
uri2ops    → operator/browser/OS actions
uri2verify → data quality + replay + envelope checks
uri3       → URI core, workflow orchestration, explain, doctor
hypervisor → deployment lifecycle
```

See also: [`PACKAGE_BOUNDARIES.md`](./PACKAGE_BOUNDARIES.md), [`URI2RUN_ARCHITECTURE.md`](./URI2RUN_ARCHITECTURE.md).

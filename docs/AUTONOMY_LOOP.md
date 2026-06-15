# Autonomy loop

Same cycle as ecosystems, applied to failures:

```text
observe → diagnose → repair → (learn) → evolve → ticket
```

## 1. Observe

```bash
uri agent status weather-map-agent.local
hypervisor inspect-agent weather-map-agent.local
hypervisor supervise weather-map-agent.local --watch --repair auto --interval 15
uri logs log://hypervisor?grep=weather-map-agent.local
```

Readiness separates **process running** from **health OK** and detects port/health URI drift.

Dashboard feed:

```bash
curl -s http://localhost:8788/api/events
curl -N http://localhost:8788/api/events/stream
```

`/api/events` merges schema-valid incidents, WWW monitor snapshots, **LogEvent**
records from `output/logs/*.jsonl`, and live agent health. `/api/events/stream`
exposes the same data as Server-Sent Events for the chat sidebar.

Lifecycle and repair operations now emit durable events to:

```text
output/logs/hypervisor-events.jsonl
```

Covered operations: `run-agent`, `stop-agent`, `restart-agent`,
`repair diagnose`, `repair apply`, `repair heal`, and `repair learn`. Full
per-step workflow telemetry remains in the workflow event logs under
`output/events/workflows/`.

`supervise --watch` keeps observing one deployment, applies repair backoff for
repeated failures and writes deduped `LogEvent` JSONL to
`output/logs/hypervisor-watch.jsonl`, which is visible in `/api/events` and SSE.

## 2. Diagnose

```bash
uri repair diagnose weather-map-agent.local
```

Produces a **RepairPlan** envelope with classification and safe playbooks.

## 3. Repair

```bash
uri repair apply weather-map-agent.local --dry-run
uri repair apply weather-map-agent.local --approve
hypervisor supervise weather-map-agent.local --repair auto --learn
hypervisor supervise weather-map-agent.local --watch --repair auto --learn
hypervisor repair heal weather-map-agent.local
```

Bounded strategies: restart, sync health URI, port rebound (policy-gated).

## 4. Incident artifact

Unresolved failures become schema-valid incidents:

```text
output/incidents/{date}/{agent}/inc_*.yaml
```

URI: `incident://agent/{deployment}/{incident_id}`

## 5. Evolution

```bash
uri evolve from-incident output/incidents/.../inc_*.yaml
uri proposal verify evolution/proposals/from_incident_*.yaml
uri proposal apply … --sandbox
```

## 6. Ticket (planfile)

```bash
hypervisor ticket import planfile.yaml
uri ticket show ticket://feature/PL-10
uri evolve from-ticket ticket://feature/PL-10
```

Dashboard tickets that describe a UI agent chain into the ecosystem pipeline automatically.

## Dashboard narrative

The dashboard agent shows human-readable timelines; each button maps to a URI:

```text
[Pokaż logi]     → log://...
[Diagnozuj]      → repair://.../diagnose
[Napraw]         → repair://.../apply  (--approve)
[Utwórz ticket]  → ticket://...
```

See [`DASHBOARD.md`](./DASHBOARD.md).

## Current autonomy boundary

Taskinity is autonomous for low-risk observation and bounded repair:

- NL planning, URI preview, agent inspection and monitor checks run without approval.
- Mutating workflow steps, repair apply, tickets and external system writes require
  approval through CLI flags or dashboard policy.
- `supervise --watch` is available for continuous local observation of one
  deployment per process.
- Lifecycle and repair commands emit dashboard-visible `LogEvent` records to
  `output/logs/hypervisor-events.jsonl`.
- The remaining gap is the full uri-healer loop `incident → classify logs → regenerate agent
  or rollback artifact → redeploy → verify → learn` for all failure families.

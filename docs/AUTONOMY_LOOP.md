# Autonomy loop

Same cycle as ecosystems, applied to failures:

```text
observe → diagnose → repair → (learn) → evolve → ticket
```

## 1. Observe

```bash
uri agent status weather-map-agent.local
hypervisor inspect-agent weather-map-agent.local
uri logs log://hypervisor?grep=weather-map-agent.local
```

Readiness separates **process running** from **health OK** and detects port/health URI drift.

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

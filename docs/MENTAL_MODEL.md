# Mental model — 7 concepts

Do not learn all packages on day one. Learn this vocabulary:

| Concept | Meaning | Example |
|---------|---------|---------|
| **URI** | Address of a resource or action | `agent://weather-map-agent` |
| **Agent** | Service that exposes capabilities | weather-map-agent, hypervisor-dashboard |
| **Capability** | What an agent or system can do | `weather.forecast.html`, `view.process.agent` |
| **Flow** | Ordered sequence of URI steps | compact `*.uri.flow.yaml` → workflow graph |
| **Runtime** | Where a URI executes | python, shell, http, docker, ssh |
| **Artifact** | Saved plan, log, incident, proposal | `output/incidents/.../inc_*.yaml` |
| **Policy** | Safety gates | `--dry-run`, `--approve`, `--readonly` |

## Level 2 (after the first week)

| Concept | Meaning |
|---------|---------|
| Incident | Schema-valid record of a runtime failure |
| RepairPlan | Diagnosis + safe playbooks envelope |
| Ticket | Planfile task as `ticket://feature/PL-1` |
| EvolutionProposal | Change proposal from ticket or incident |
| ApplyPlan | urigen diff before mutating the repo |
| RuntimeState | `runtime://agent/{deployment}/state` |
| AgentReadiness | process vs health vs card vs logs |

## Core sentence

```text
An agent has capabilities.
Each capability has a URI.
Every URI can be explained, verified, run, observed in UI, and stored as an artifact.
```

## One lifecycle for everything

Agents, dashboards, workflows, and ecosystems share the same cycle:

```text
plan → generate → verify → apply → run → observe → repair/evolve
```

Policy rule:

```text
plan / generate / verify / explain  = no --approve required
apply / run / repair / evolution    = --approve required (or --sandbox)
```

## Package names (when you go deeper)

| Short name | Role |
|------------|------|
| **urish** | URI Shell — your single CLI |
| **urigen** | URI Generator — ecosystem artifacts |
| **hypervisor** | Agent deployment and supervision |
| **uri2run** | URI runtime transports |
| **uri3** | Explain, doctor, schema, workflow |
| **uri2ops** | Operator workflows and serve |
| **touri** | Capability registry and matching |

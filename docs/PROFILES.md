# Ecosystem profiles

Users pick a **profile** instead of hand-picking capabilities, flows, and deployments.

```bash
uri ecosystem profiles
uri ecosystem plan "stwórz dashboard hypervisora" --profile dashboard-agent
uri ask "stwórz web UI do procesów hypervisora"   # auto-selects dashboard-agent
```

## Profiles

| Profile | Use case | Generates |
|---------|----------|-----------|
| `minimal` | Weather demo agent + health | capabilities, flows, weather deployment |
| `voice` | minimal + STT/TTS/voice | voice capabilities and flows |
| `dashboard-agent` | Hypervisor Web UI system agent | view/repair/ticket capabilities, dashboard deployment |
| `agent` | agent package with deployment fragment | partial |
| `operator` | Browser/shell/system operator | partial |
| `ecosystem` / `full` | Domain + agent + deploy + tests | *(partial)* |

Friendly aliases are accepted:

```text
dashboard       → dashboard-agent
voice-agent     → voice
operator-agent  → operator
ecosystem       → full
```

Planned but not yet generated as dedicated profiles: `api-agent`, `repair-agent`.

## dashboard-agent

Semantic id: **`hypervisor-dashboard`** (not a slug from the full prompt).

Planned URIs:

```text
agent://hypervisor-dashboard
deployment://hypervisor-dashboard.local
view://process/agent/{agent_id}/latest
view://workflow/{workflow_id}/timeline
view://incident/{incident_id}/explain
repair://agent/{agent_id}/diagnose
ticket://bug/from-incident/{incident_id}
```

Workflow:

```bash
uri ecosystem plan "…" --profile dashboard-agent \
  --out output/proposals/hypervisor-dashboard.ecosystem.proposal.yaml
uri ecosystem generate output/proposals/hypervisor-dashboard.ecosystem.proposal.yaml \
  --out output/ecosystems/hypervisor-dashboard
uri ecosystem verify output/ecosystems/hypervisor-dashboard/ecosystem.yaml
uri ecosystem apply output/ecosystems/hypervisor-dashboard/ecosystem.yaml --plan
uri ecosystem apply output/ecosystems/hypervisor-dashboard/ecosystem.yaml --approve
uri agent run hypervisor-dashboard.local --wait-healthy --approve
uri dashboard open
```

Shortcut:

```bash
uri dashboard create hypervisor-dashboard --plan-only
uri dashboard create hypervisor-dashboard --approve --open
```

## Policy

- `plan`, `generate`, `verify`, `explain` — safe, no repo mutation
- `apply --approve`, `agent run --approve` — mutates repo or runtime

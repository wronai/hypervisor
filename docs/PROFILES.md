# Ecosystem profiles

Users pick a **profile** instead of hand-picking capabilities, flows, and deployments.

```bash
uri ecosystem plan "stwórz dashboard hypervisora" --profile dashboard-agent
uri ask "stwórz web UI do procesów hypervisora"   # auto-selects dashboard-agent
```

## Profiles

| Profile | Use case | Generates |
|---------|----------|-----------|
| `minimal` | Weather demo agent + health | capabilities, flows, weather deployment |
| `voice` | minimal + STT/TTS/voice | voice capabilities and flows |
| `dashboard-agent` | Hypervisor Web UI system agent | view/repair/ticket capabilities, dashboard deployment |
| `api-agent` | HTTP agent with endpoints | *(planned)* |
| `repair-agent` | Diagnose/repair focused agent | *(planned)* |
| `operator-agent` | Browser/shell/system operator | *(planned)* |
| `ecosystem` / `full` | Domain + agent + deploy + tests | *(partial)* |

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

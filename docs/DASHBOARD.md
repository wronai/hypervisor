# Dashboard agent

The hypervisor dashboard is **not a special frontend**. It is a normal **system agent** with profile `dashboard-agent`:

```text
AgentContract + capabilities + URI tree + deployment + tests + ecosystem manifest
```

## Identity

```text
agent://hypervisor-dashboard
deployment://hypervisor-dashboard.local   (port 8788)
```

Package: `packages/hypervisor-dashboard-agent/`

## Capabilities

| Capability | URI | Side effects |
|------------|-----|--------------|
| Process view | `view://process/agent/{agent_id}/latest` | read-only |
| Workflow timeline | `view://workflow/{workflow_id}/timeline` | read-only |
| Incident explain | `view://incident/{incident_id}/explain` | read-only |
| Repair diagnose | `repair://agent/{agent_id}/diagnose` | read-only |
| Repair apply | `repair://agent/{agent_id}/apply` | **requires approval** |
| Ticket from incident | `ticket://bug/from-incident/{incident_id}` | **requires approval** |

Contract resources use `resource://dashboard/...` internally; views expose `view://...` to users.

## Create via urish (not hand-written HTML)

```bash
uri ask "stwórz web UI agenta hypervisor-dashboard do pokazywania procesów"
uri dashboard create hypervisor-dashboard --plan-only
uri dashboard create hypervisor-dashboard --approve --open
```

Or step by step — see [`PROFILES.md`](./PROFILES.md).

## UI expectations

The dashboard should show **cards and timelines**, not raw JSON:

```text
Agent pogodowy — Status: zdegradowany

✓ przygotowano plan
⚠ port 8101 był zajęty → 8105
✗ health nie odpowiada
↻ 3 próby restartu

[Pokaż logi] [Diagnozuj] [Napraw] [Utwórz ticket]
```

Each action resolves to a URI call through the dashboard policy gate.

## Observe running agents

```bash
uri agent run hypervisor-dashboard.local --wait-healthy --approve
uri dashboard open
uri call view://process/agent/weather-map-agent.local/latest
```

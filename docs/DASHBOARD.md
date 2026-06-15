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

## WWW chat (`www/chat.html`)

Product chat is **not** a separate backend — it calls the same dashboard-agent API as CLI `uri ask` / `uri call`:

```text
NL prompt  →  POST /api/ask  →  urish ask  →  markdown plan (URIs + next_steps)
User action  →  POST /api/uri/call or /api/plan/run  →  policy gate  →  touri / uri3 / hypervisor
```

Important:

- Chat **plans** on Enter; it runs only after a URI action or **Run plan** button.
- Paste **one NL command per line** for batch planning (`Detected N commands`).
- Six **office cards** on the landing page map to [`domains/office/`](../domains/office/) (same URIs as chat quick prompts).
- Default **dry-run** in UI; use Run with approve or `uri run … --approve` for execution.
- **Run plan** (`POST /api/plan/run`): optional `auto_repair` + retry on agent URI failures; checkbox **speak result** → mock TTS summary.
- Sidebar events: `/api/events` and SSE `/api/events/stream` — incidents, monitor snapshots, **log events** (`output/logs/*.jsonl`), live agent health.
- Monitor webhooks: `POST /api/monitors/webhook` writes `output/monitoring/webhook-*.json`
  and `output/logs/hypervisor-webhook.jsonl`, then the event appears in `/api/events`
  and SSE.
- Voice: `/api/voice/transcribe` (mock / Whisper) → same `POST /api/ask` path; `/api/voice/speak` for TTS.

Full guide: [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md) · WWW details: [`www/README.md`](../www/README.md)

```bash
make start
# http://localhost:8788/www/chat.html

uri ask "Wejdź na stronę dostawcy, pobierz raport CSV za ten miesiąc i zapisz w rozliczeniach."
uri run workflow://office/supplier-report/monthly --dry-run
```

## Observe running agents

```bash
uri agent run hypervisor-dashboard.local --wait-healthy --approve
uri dashboard open
uri call view://process/agent/weather-map-agent.local/latest
```

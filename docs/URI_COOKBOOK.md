# URI cookbook

Quick recipes. Prefer **`uri`** shortcuts where listed; full URIs work everywhere.

## Agents and health

| I want to… | Command / URI |
|------------|----------------|
| Agent status | `uri agent status weather-map-agent.local` |
| Agent health | `uri agent health weather-map-agent.local` or `uri hwa` |
| Run agent | `uri agent run weather-map-agent.local --wait-healthy --approve` |
| Inspect readiness | `hypervisor inspect-agent weather-map-agent.local` |
| Health URI | `health://agent/weather-map-agent.local` |

## Logs and observation

| I want to… | Command / URI |
|------------|----------------|
| Hypervisor logs | `uri logs log://hypervisor?grep=weather-map-agent.local` |
| Watch health | `uri watch health://agent/weather-map-agent.local --count 5` |
| Explain URI | `uri explain weather://forecast/Gdansk/14/html` |

## Repair and autonomy

| I want to… | Command / URI |
|------------|----------------|
| Diagnose | `uri repair diagnose weather-map-agent.local` or `uri rwa` |
| Dry-run repair | `uri repair apply weather-map-agent.local --dry-run` |
| Apply repair | `uri repair apply weather-map-agent.local --approve` |
| Repair URI | `repair://agent/weather-map-agent.local/diagnose` |

## Tickets and evolution

| I want to… | Command / URI |
|------------|----------------|
| List tickets | `uri ticket list` |
| Show ticket | `uri ticket show ticket://feature/PL-1` |
| Proposal from ticket | `uri evolve from-ticket ticket://feature/PL-1` |
| Verify proposal | `uri proposal verify evolution/proposals/proposal_from_ticket_PL-1.yaml` |
| Sandbox apply | `uri proposal apply … --sandbox` |

## Ecosystem (create agents)

| I want to… | Command |
|------------|---------|
| Natural language plan | `uri ask "stwórz agenta pogodowego"` |
| Plan ecosystem | `uri ecosystem plan "…" --profile minimal --out output/proposals/weather.yaml` |
| Generate artifacts | `uri ecosystem generate output/proposals/weather.yaml --out output/ecosystems/weather` |
| Verify | `uri ecosystem verify output/ecosystems/weather/ecosystem.yaml` |
| Apply plan | `uri ecosystem apply …/ecosystem.yaml --plan` |
| Apply for real | `uri ecosystem apply …/ecosystem.yaml --approve` |

## Dashboard (Web UI agent)

| I want to… | Command / URI |
|------------|----------------|
| Plan dashboard | `uri ask "stwórz web UI hypervisor-dashboard"` |
| Create (plan only) | `uri dashboard create hypervisor-dashboard --plan-only` |
| Run dashboard | `uri agent run hypervisor-dashboard.local --wait-healthy --approve` |
| Open UI | `uri dashboard open` or `uri dashboard-ui --approve` |
| Process view | `view://process/agent/weather-map-agent.local/latest` |
| Incident explain | `view://incident/{incident_id}/explain` |

## Shortcuts (`config/cli_shortcuts.uri.yaml`)

| Shortcut | URI |
|----------|-----|
| `uri hwa` | `health://agent/weather-map-agent.local` |
| `uri rwa` | `repair://agent/weather-map-agent.local/diagnose` |
| `uri wh` | `weather://forecast/Gdansk/14/html` |
| `uri weather-status` | same as `hwa` |
| `uri weather-process` | process view for weather agent |
| `uri dashboard-ui --approve` | open dashboard UI with payload from config |

## Multi-agent monitoring

| I want to… | Command / surface |
|------------|-------------------|
| List all deployments | `hypervisor deployments` or `GET /api/agents` |
| Inspect one agent | `hypervisor inspect-agent invoices-agent.local` |
| Run several agents | `hypervisor run-agent … --detach` per deployment (unique ports) |
| Watch health | `uri watch health://agent/weather-map-agent.local --count 5` |
| Fleet events (WWW) | `curl http://localhost:8788/api/events` · chat sidebar SSE |
| Hypervisor logs | `uri3 logs 'log://hypervisor?level=ERROR&limit=50'` |
| Bounded auto-repair | `hypervisor supervise weather-map-agent.local --repair auto` |
| Plan run + auto-repair (chat) | `POST /api/plan/run` with `auto_repair: true` |

Full reference: [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md) · tutorial [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md) · schema checker [`TUTORIAL_AGENT_SCHEMA_URI.md`](./TUTORIAL_AGENT_SCHEMA_URI.md).

## Policy reminders

```bash
uri call repair://agent/demo/apply              # blocked without --approve
uri call repair://agent/demo/apply --dry-run    # show plan only
uri call repair://agent/demo/apply --approve    # execute
```

## Chat and office (WWW / CLI)

| I want to… | Command / action |
|------------|------------------|
| Plan from NL | `uri ask "…"` or POST `/api/ask` |
| Batch plans (one line each) | Paste multiline in chat → `Detected N commands` |
| Office · supplier CSV | `uri ask "Wejdź na stronę dostawcy, pobierz raport CSV…"` → `uri run workflow://office/supplier-report/monthly --dry-run` |
| Office · ZUS portal | `uri run workflow://portal/zus-form/dry-run` |
| Office · bank batch | `uri run workflow://bank/batch-transfer/dry-run` |
| Office · invoices | `uri run workflow://invoices/batch/dry-run` |
| Run example bundle | `bash examples/33_office_workflows/run.sh` |
| Full office day mock | `bash examples/31_office_day/run.sh` |

Chat **does not** auto-execute — run `uri run` or click **Run URI** after the plan.

See [`CHAT_AND_WORKFLOWS.md`](./CHAT_AND_WORKFLOWS.md).

## Compact URI flow (author YAML)

| I want to… | Command |
|------------|---------|
| Validate compact flow | `uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml` |
| Expand to graph | `uri2flow expand … --out output/weather.uri.graph.yaml` |
| Dry-run workflow | `uri3 run-workflow output/weather.uri.graph.yaml --dry-run --browser mock` |
| Execute mock | `uri3 run-workflow output/weather.uri.graph.yaml --approve --browser mock` |
| One-shot demo | `bash examples/15_compact_uri_flow/run.sh` |

`uri2flow` compiles only; execution is `uri3`. Different path from chat NL → `workflow://graph/…`.

## Port drift and registry sync

| I want to… | Command |
|------------|---------|
| Inspect readiness | `hypervisor inspect-agent invoices-agent.local` |
| Sync declared health URI to effective port | `hypervisor repair apply invoices-agent.local --playbook sync_health_uri` |
| Start with auto-rebind | `hypervisor run-agent … --detach --wait-healthy --supervise-repair auto` |

After port rebound on start, registry is updated automatically when the agent stays healthy.

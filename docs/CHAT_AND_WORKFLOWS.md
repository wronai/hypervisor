# Chat, office scenarios, and workflows

How **Taskinity Chat** (`www/chat.html`) relates to **compact URI flows** (`uri2flow`) and **workflow execution** (`uri3` / `uri run`).

## One-sentence model

**Chat translates natural language into a URI plan; execution starts only when the user clicks a URI/Run plan action or runs the equivalent CLI command, with dry-run as the default and approval required for side effects.**

Chat does **not** auto-run an entire workflow on Enter. Enter submits text to
`POST /api/ask`; the result then exposes guarded actions:

- `Preview` / URI chip — policy preview, no side effects.
- `Dry-run` / `Run plan (dry-run)` — executes the planned URI sequence in preview mode.
- `Run real` / `Run plan (approve)` — sends `approved=true` and `dry_run=false` through the policy gate.

## Chat pipeline (step by step)

```text
1. User types NL, uses the microphone, or clicks an office card → prefilled prompt.
2. `POST /api/ask` → `urish ask` → `detect_intent` + `planned_uris` + `next_steps`.
3. UI shows markdown: detected kind, planned URI, next steps and action buttons.
4. User runs one URI (`POST /api/uri/call`) or the whole plan (`POST /api/plan/run`).
   - Plan run supports `auto_repair` (default true) and `retry_after_repair` — on agent step
     failure calls `repair://agent/{id}/auto` and optionally retries the step.
   - Checkbox **speak result** sets `speak_summary: true` → `POST /api/voice/speak` (mock TTS).
5. Backend: touri / uri3 / hypervisor / uri2ops (policy gate, dry-run default).
6. Result envelope + logs + artifacts (`output/artifacts/workflows/…`).
7. Sidebar refreshes agents and events from `/api/agents`, `/api/events` and `/api/events/stream`.
   Event types: `incident.created`, `monitor.snapshot`, `log.event`, `agent.health`.
```

### Multi-line prompts (batch)

Paste **one command per line** — each line is planned independently:

```text
pokaż proces agenta weather-map-agent.local
zdiagnozuj agenta invoices-agent.local
rob rzuty ekranów stron softreck.com … co 5 minut …
```

Response header: `Detected 3 commands` with a numbered block per line.

Implementation: `urish.intent.split_nl_commands()` → `urish.backends.ask.ask_prompt()`.

### Office landing cards ↔ chat

Six cards on [`www/index.html`](../www/index.html) map to canonical scenarios in
[`domains/office/scenario_registry.yaml`](../domains/office/scenario_registry.yaml) and
[`domains/office/README.md`](../domains/office/README.md) (`markpact:scenario`).
`urish` only loads this declarative registry; office, invoice, bank and ERP terms are
not hardcoded in the generic package.

| Card | Example quote | Primary workflow URI |
|------|---------------|----------------------|
| Website · CSV | Wejdź na stronę dostawcy, pobierz raport CSV… | `workflow://office/supplier-report/monthly` |
| Portal · ZUS | Zaloguj się do portalu klienta, formularz ZUS… | `workflow://portal/zus-form/dry-run` |
| Subiekt · ERP | Otwórz Subiekta, wklej dane z Excela… | `pcwin://window/Subiekt GT/focus` |
| Invoices · Woo | Wystaw faktury za WooCommerce… | `workflow://invoices/batch/dry-run` |
| Bank | Przygotuj przelewy… zatrzymaj przed autoryzacją | `workflow://bank/batch-transfer/dry-run` |
| Android · 2FA | Bank czeka na potwierdzenie w aplikacji… | `android://device/pixel-7/screenshot` |

- Click a card → `localStorage.taskinity.chatPrompt` → [`www/chat.html`](../www/chat.html)
- Quick prompts in chat sidebar use the same six quotes (English labels)
- i18n: `www/office-cards-i18n.js` (PL / EN / DE on landing)

Example:

```bash
uri ask "Wejdź na stronę dostawcy, pobierz raport CSV za ten miesiąc i zapisz w rozliczeniach."
uri run workflow://office/supplier-report/monthly --dry-run
```

Tests: `tests/urish/test_office_scenarios.py`. The tests use the generic
`urish.scenario_registry` loader; `urish` no longer exposes `office_*`
compatibility modules.

Boundary notes: [`DOMAIN_SEPARATION.md`](./DOMAIN_SEPARATION.md)

Example bundle: [`examples/33_office_workflows/`](../examples/33_office_workflows/)

Full office day (mock chain): [`examples/31_office_day/`](../examples/31_office_day/)

## Two ways to get a workflow

| Path | Input | Compiler | Execute |
|------|--------|----------|---------|
| **Author / CI** | `*.uri.flow.yaml` | `uri2flow expand` → graph YAML | `uri3 run-workflow …` |
| **Chat / NL** | Polish/English sentence | `nl2uri` → stable `workflow://graph/website-screenshot-schedule/dry-run` for screenshot schedules; other flows may use `{slug}` | `uri run workflow://…` |

They are **not** the same code path. Example 15 uses compact flow; chat screenshot schedules use NL workflow planning.

### Compact flow (example 15)

```bash
bash examples/15_compact_uri_flow/run.sh
uri3 run-workflow output/weather.uri.graph.yaml --dry-run --browser mock
uri3 run-workflow output/weather.uri.graph.yaml --approve --browser mock
```

See [`URI2FLOW.md`](./URI2FLOW.md) · [`examples/15_compact_uri_flow/`](../examples/15_compact_uri_flow/)

## Agent ports and health URI drift

When a preferred port is busy (e.g. `8101`, `8103`), hypervisor **rebinds** to a free port and stores the **effective** health URI in runtime state.

| Symptom | Action |
|---------|--------|
| `HEALTH_URI_DRIFT` warning in inspect | `hypervisor repair apply invoices-agent.local --playbook sync_health_uri` |
| Flow YAML hardcodes `:8101` but agent on `:8118` | Update flow URL or sync registry; mock browser still passes |
| `No module named uvicorn` in process log | `pip install 'uvicorn>=0.27'` in the hypervisor venv |

After successful start with port rebound, registry is updated automatically (`registry_sync.persist_rebound_port`).

`health://agent/{deployment}` uses **inspect** (effective port), not only declared registry port.

## Docker WWW stack

`make start` mounts (see `www/docker-compose.yml`):

- `www/`, `packages/`, `agents/generated/`, `deployments/`, `output/`, …

Chat API: `http://localhost:8788/api/ask` · UI: `http://localhost:8788/www/chat.html`

Redirect: `/chat.html` → `/www/chat.html`

## Events and voice

The chat sidebar is backed by a unified event feed:

| Endpoint | Use |
|----------|-----|
| `GET /api/events` | incidents, monitor snapshots, **log events** (`LogEvent` / ERROR from `output/logs/*.jsonl`), live agent health |
| `GET /api/events/stream` | SSE feed used by the browser to refresh the sidebar |
| `POST /api/monitors/webhook` | external monitor/webhook input; writes `output/monitoring/webhook-*.json` and `output/logs/hypervisor-webhook.jsonl` |
| `POST /api/plan/run` | execute planned URIs; `auto_repair`, `retry_after_repair`, optional `speak_summary` |
| `POST /api/voice/speak` | mock TTS after plan or when **speak result** is checked |

Voice input uses the same text pipeline after transcription:

```text
microphone → POST /api/voice/transcribe → transcript → POST /api/ask → URI plan
```

The UI exposes `mock` and Whisper modes. Mock mode is deterministic for tests and
demo prompts. Whisper mode uses `packages/uri2voice/uri2voice/stt_whisper.py`:
`OPENAI_API_KEY` selects the OpenAI audio transcription path; without it the code
tries a local `openai-whisper` install.

## Related docs

- [`DASHBOARD.md`](./DASHBOARD.md) — dashboard agent + WWW API
- [`VOICE_WITH_TOURI.md`](./VOICE_WITH_TOURI.md) — voice capability pack
- [`GETTING_STARTED.md`](./GETTING_STARTED.md) — five learning paths
- [`URI_COOKBOOK.md`](./URI_COOKBOOK.md) — recipes
- [`AGENTS_AND_MONITORING.md`](./AGENTS_AND_MONITORING.md) — real agents, fleet ops, monitoring tools
- [`DEPLOYMENT.md`](./DEPLOYMENT.md) — run-agent, inspect, supervise
- [`www/README.md`](../www/README.md) — product pages

Polish index: [`README.pl.md`](./README.pl.md) (section *Chat i workflow biurowe*).

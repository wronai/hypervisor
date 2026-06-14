# urish

Unified URI shell facade: one command (`uri`) over uri3, uri2run, uri2ops, hypervisor, urigen.

```bash
uri call python://uri2voice.stt:transcribe --payload '{"text":"test"}'
uri call python://uri2voice.stt:transcribe --payload @payload.json
uri explain weather://forecast/Gdansk/14/html
uri agent health weather-map-agent.local
uri doctor
uri doctor --strict
uri ask "stworz agenta pogodowego z healthcheckiem"
uri ask "stwórz web UI agenta hypervisor-dashboard do pokazywania procesów"
uri dashboard create hypervisor-dashboard --plan-only
uri watch health://agent/weather-map-agent.local
uri stream sse://localhost:8791/events
uri shell
```

Semantic model everywhere:

```text
URI + payload + context + policy → explain → execute → ServiceResult envelope
```

## Subcommands

| Command | Backend |
|---------|---------|
| `call`, `explain`, `plan` | uri3 + uri2run |
| `run` | uri2ops / uri2flow |
| `logs`, `watch` | uri3 logs |
| `stream` | SSE/WS |
| `ask`, `nl` | nl2uri + urigen |
| `select` | envelope piping |
| `agent` | hypervisor |
| `dashboard` | urigen + hypervisor dashboard agent |
| `repair` | repair supervisor |
| `ticket` | planfile |
| `evolve`, `proposal` | evolution |
| `ecosystem` | urigen |
| `context` | config/urish/contexts |

## Policy

```bash
uri call repair://agent/demo/apply --dry-run
uri call repair://agent/demo/apply --approve --policy prod
uri run workflow://flow/demo --approve
```

Exit codes: `0=ok`, `1=failed`, `2=execution`, `3=validation`, `4=policy blocked`, `5=not found`, `6=dependency missing`.

Legacy CLIs remain as backends; `uri` is the user-facing facade.

**Learning curve:** start with [`docs/GETTING_STARTED.md`](../../docs/GETTING_STARTED.md) — one shell, one lifecycle, profiles instead of package names.

## Dashboard Agent Workflow

`urish` creates the dashboard as a controlled URI ecosystem, not as an ad-hoc
web app:

```bash
uri ecosystem plan "stwórz web UI agenta hypervisor-dashboard do pokazywania procesów" \
  --profile dashboard-agent \
  --out output/proposals/hypervisor-dashboard.ecosystem.proposal.yaml
uri ecosystem generate output/proposals/hypervisor-dashboard.ecosystem.proposal.yaml \
  --out output/ecosystems/hypervisor-dashboard
uri ecosystem verify output/ecosystems/hypervisor-dashboard/ecosystem.yaml
uri ecosystem apply output/ecosystems/hypervisor-dashboard/ecosystem.yaml --plan
uri agent run hypervisor-dashboard.local --wait-healthy --approve
```

Shortcut:

```bash
uri dashboard create hypervisor-dashboard --plan-only
uri agent create-dashboard hypervisor-dashboard --dry-run
```

Read-only dashboard views stay behind `resource://dashboard/...` contracts and
`view://...` capabilities. Mutating actions such as `repair://.../apply` remain
approval-gated.

The generated ecosystem also carries the dashboard app source under `app/`
(`hypervisor_dashboard_agent.main:app`) so the workflow artifact contains the
system agent implementation, not only registrations.

## Ticket → Evolution → Ecosystem

When a planfile task describes a dashboard agent, `urish` chains the ticket flow
into the ecosystem pipeline:

```bash
uri ticket show ticket://feature/PL-10
uri evolve from-ticket ticket://feature/PL-10
uri proposal verify evolution/proposals/proposal_from_ticket_PL-10.yaml
uri proposal apply evolution/proposals/proposal_from_ticket_PL-10.yaml --sandbox
uri ecosystem generate output/proposals/hypervisor-dashboard.ecosystem.proposal.yaml \
  --out output/ecosystems/hypervisor-dashboard
uri ecosystem apply output/ecosystems/hypervisor-dashboard/ecosystem.yaml --approve
```

`uri doctor --strict` additionally validates incidents, tickets, evolution
proposals, and artifact lifecycle envelope coverage.

## Internal Shape

`urish.cli` only wires the Typer app and high-level command groups. Runtime
commands (`call`, `explain`, `plan`, `run`, `logs`, `watch`, `stream`) are
registered from `urish.commands.runtime`; backend work stays in
`urish.backends.*`.

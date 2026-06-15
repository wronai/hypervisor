# Example 35 — Website screenshot schedule (chat NL)

Chat prompts like “rob rzuty ekranów stron softreck.com prototypowanie.pl co 5 minut
do folderu ~/images/” plan a **stable** workflow URI:

| URI | Mode |
|-----|------|
| `workflow://graph/website-screenshot-schedule/dry-run` | Plan only (mock browser) |
| `workflow://graph/website-screenshot-schedule` | Execute with approval |

Manifests: [`website_screenshot_schedule_dry_run.uri.capability.yaml`](../20_touri_capabilities/website_screenshot_schedule_dry_run.uri.capability.yaml)

Source files (task graph, this README as provenance) are now addressable via native `file://` URIs. The system (path resolution in uri2run, graph loading in uri3, markpact loaders in uri2pact) supports `file://` alongside `markpact://file://...` for generated agent/workflow sources and logs.

Example:
```
file://$(pwd)/examples/35_website_screenshot_schedule/task_graph.yaml
file://$(pwd)/examples/35_website_screenshot_schedule/README.md
```
(See `packages/uri2pact/uri2pact/core.py`, `uri2run/transports/paths.py`, `uri3/graph/graph_validator.py` for the `file://` support rollout.)

## Quick start

```bash
bash examples/35_website_screenshot_schedule/run.sh
```

Manual:

```bash
uri explain workflow://graph/website-screenshot-schedule/dry-run
uri run workflow://graph/website-screenshot-schedule/dry-run
uri run workflow://graph/website-screenshot-schedule --approve --adapter mock
```

Real PNG captures (optional):

```bash
pip install -e '.[browser]'
playwright install chromium
uri run workflow://graph/website-screenshot-schedule --approve --adapter playwright
```

Recurring host schedule is **not** auto-installed by chat — use `scripts/www/install-cron.sh`
or wire a custom cron entry that calls the workflow URI.

**Viewing log content (`treść logów`) via `log://*` (recommended):**

The detailed execution trace for this workflow (StepStarted, screenshot_softreck, artifact_uri for the PNGs, WorkflowCompleted etc.) lives in the per-workflow event file. It is addressable as a first-class `log://` URI:

```bash
# Short, clean forms (new)
urish logs 'log://workflow/website-screenshot-schedule?limit=10'
urish logs 'log://events/website-screenshot-schedule?tail=true&limit=8'           # only recent / changes
urish logs 'log://workflow/website-screenshot-schedule?grep=screenshot_softreck|artifact_uri&limit=5'

# Explicit file form (also works everywhere)
urish logs 'log://file/output/events/workflows/website-screenshot-schedule.jsonl?tail=true&limit=5'
```

Live observation vs one-shot content:
- `urish logs 'log://...'`  → actual log lines / parsed events (the treść you want)
- `urish watch 'log://...'` → polling RuntimeEvent snapshots (status only, use --json for payload)

Examples with watch (snapshots):

```bash
urish watch 'log://hypervisor?grep=website-screenshot-schedule|browser|screen' --interval 1
urish watch 'log://events/website-screenshot-schedule?tail=true&limit=3' --interval 2 --json
```

The workflow-specific events are intentionally separate from the main `log://hypervisor` / `log://hypervisor-events` (those contain agent lifecycle, repair, deployment etc.).

See also the tip printed by `bash examples/35_website_screenshot_schedule/run.sh`.

**file:// URI support** (rolled out for markpact sources, graphs, flows, agent READMEs):
The defining sources for this schedule (task_graph.yaml and this README as provenance/chat source) are referenceable as:
`file://$(pwd)/examples/35_website_screenshot_schedule/task_graph.yaml`
`file://$(pwd)/examples/35_website_screenshot_schedule/README.md`

See updates in `packages/uri2pact/uri2pact/core.py` (markpact file:// + fragments), `uri2run/transports/paths.py`, `uri3/graph/graph_validator.py` (graph load from file://), and generator marker now emits `file://` for `markpact_readme`.
This allows uniform `file://` (and `markpact://file://...`) handling in logs, explain, touri/uri run, and agent/workflow provenance (matching the generated agents in `agents/generated/*/README.md`).

## Chat

Paste the Polish batch example from Taskinity Chat intro — line 3 resolves to
`workflow://graph/website-screenshot-schedule/dry-run` (not a per-prompt slug).

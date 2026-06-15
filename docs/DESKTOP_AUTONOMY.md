# Desktop Autonomy

Desktop autonomy is implemented as a controlled capability layer, not as hidden
domain logic inside the hypervisor.

```text
NL/domain prompt
  -> domains/* scenario or workflow
  -> URI task graph
  -> agent://desktop-operator
  -> uri2ops operation registry
  -> browser / screen / input / pcwin / android adapter
  -> artifacts, logs, validation and approval gates
```

## Separation Rule

| Layer | Owns | Must not own |
|-------|------|--------------|
| `domains/*` | Business workflows, scenario routing, domain vocabulary | Desktop adapter implementation |
| `agents/operators/` | Capability-agent contracts | Domain scenario data |
| `packages/uri2ops` | Operation registry, adapters, A2A/MCP serve runtime | Business workflows |
| `hypervisor` | Deployment, policy, events, incidents, approval | Direct clicking, typing or OS control |

The default capability contract is
[`agents/operators/desktop_operator.yaml`](../agents/operators/desktop_operator.yaml).
The generic routing/domain pack is
[`domains/desktop_ops/`](../domains/desktop_ops/).

## Running The Operator

Start the desktop operator HTTP daemon:

```bash
uri2ops serve --host 127.0.0.1 --port 8791
```

Or run it through the hypervisor deployment registry:

```bash
hypervisor run-agent desktop-operator.local --detach --wait-healthy
hypervisor inspect-agent desktop-operator.local
```

Health and discovery:

```bash
curl -s http://127.0.0.1:8791/health
curl -s http://127.0.0.1:8791/.well-known/agent-card.json
curl -s http://127.0.0.1:8791/mcp/tools
```

The same runtime can be called through:

| Protocol | Endpoint |
|----------|----------|
| A2A | `POST http://127.0.0.1:8791/a2a/tasks` |
| MCP tools list | `GET http://127.0.0.1:8791/mcp/tools` |
| MCP tool call | `POST http://127.0.0.1:8791/mcp/tools/call` |
| CLI | `uri2ops run <task.yaml> --adapter mock --approve` |

One-URI product proof:

```bash
taskinity proof view://process/agent/weather-map-agent.local/latest
uri proof view://process/agent/weather-map-agent.local/latest
```

## Safety Defaults

The operator starts from mock adapters. Real desktop control must be selected
explicitly:

```bash
uri2ops run examples/10_browser_operator/task.health.yaml --adapter playwright --approve
uri2ops run examples/12_android_operator/task.android.yaml --adapter adb --approve
uri2ops run examples/13_pcwin_operator/task.pcwin.yaml --adapter uia --approve
```

Write actions require approval. Workflows must stop before credentials,
irreversible submits and external side effects unless a user-approved policy
allows that step.

## Domain Usage

Domain packages should depend on generic operation URIs instead of embedding
adapter details. For example, an office scenario can plan:

```text
browser://chrome/page/open
pcwin://window/<id>/focus
android://device/<id>/screenshot
workflow://office/<task>/dry-run
```

The scenario remains in `domains/office/`. The executable operation remains in
`uri2ops`. The capability contract remains in `agents/operators/`.

For generic operator discovery, use the dedicated `desktop_ops` pack:

```text
domains/desktop_ops/domain.yaml             # layer and ownership contract
domains/desktop_ops/operator_registry.yaml  # browser/screen/input/pcwin/android cards
domains/desktop_ops/scenario_registry.yaml  # NL routing for generic operator prompts
```

That pack is capability vocabulary only. Vertical scenarios should stay in their
own `domains/<domain>/` directory and reference operation URIs from there.

## Generation Rule For LLMs

When an LLM generates an app or agent for desktop autonomy:

1. Put business routing and examples in `domains/<domain>/`.
2. Put generated HTTP agents in `agents/generated/`.
3. Reuse `agent://desktop-operator` for browser, screen, input, pcwin and
   android operations.
4. Use `agent://device-robot-operator` and `domains/physical_ops/` for
   `robot://` and `device://` operations instead of adding physical hardware to
   the desktop operator.
5. Do not create a new desktop agent per scenario.
6. Do not put domain-specific names, approval shortcuts or workflow defaults in
   `agents/operators/desktop_operator.yaml`.

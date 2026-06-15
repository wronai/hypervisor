# Domain Separation

The system separates generic libraries from project/domain data.

## Rule

Generic packages may implement loaders, validators, routers and execution
adapters. They must not embed business scenarios, specific customer workflows or
generated agent facts.

| Layer | Allowed | Not allowed |
|------|---------|-------------|
| `packages/urish` | NL shell, URI planning facade, scenario registry loader | Invoice, WooCommerce, ZUS, ERP, bank-specific scenario data |
| `packages/uri3` | URI routing, graph execution, log/resource schemes | Project-specific workflow examples as hidden defaults |
| `packages/uri2ops` | Operation registry, operator adapters, A2A/MCP serve runtime | Business workflows, scenario routing |
| `packages/resource-agent-factory` | Generate agents from contracts | Hand-authored generated output |
| `agents/` | Generated agents, scenario registries, markpact provenance | Generic runtime code |
| `agents/operators/` | Capability-agent contracts such as desktop operation | Domain scenarios, customer workflow defaults |
| `domains/*` | Domain packs, workflow vocabulary, scenario registries | Desktop adapter implementation |
| `examples/` | Demonstrations and mock workflows | Required hidden runtime state |

## Current Fix

The former office routing data in:

```txt
packages/urish/urish/office_intent.py
packages/urish/urish/office_scenarios.py
```

has been moved to:

```txt
domains/office/scenario_registry.yaml
domains/office/README.md          # markpact:scenario + markpact:scenario_registry
agents/scenarios/                 # pointer README only
```

The old `urish.office_*` compatibility modules have been removed. Use the
generic scenario registry API instead:

```python
from urish.scenario_registry import match_scenario, scenarios_for_kind

scenario = match_scenario(prompt, kind="office")
all_office_scenarios = scenarios_for_kind("office")
```

## How `urish` Uses It

```text
NL prompt
  -> urish.intent.detect_intent
  -> urish.scenario_registry loads domains/*/scenario_registry.yaml + markpact scenarios
  -> planned_uris + next_steps + artifact refs
```

Override the scenario source:

```bash
URISH_SCENARIO_REGISTRY=/path/to/project/agents/scenarios urish ask "..."
```

## Desktop Operator Boundary

Autonomous desktop control uses a generic capability agent:

```txt
agents/operators/desktop_operator.yaml
domains/desktop_ops/
```

That file describes `agent://desktop-operator` and points at `uri2ops serve`.
It can expose `browser://`, `screen://`, `input://`, `pcwin://` and
`android://` operations, but it must not contain office, invoice, bank or other
domain workflow data.

Domain packages may reference those operation URIs in their own workflows. The
domain remains in `domains/<domain>/`; the executable adapter remains in
`packages/uri2ops`; deployment and audit remain in `hypervisor`.

The generic `domains/desktop_ops/` pack is the only domain pack allowed to
describe the operator capability vocabulary itself. It still does not execute
actions and it does not contain vertical workflow defaults.

Guide: [`DESKTOP_AUTONOMY.md`](./DESKTOP_AUTONOMY.md).

## Audit Notes

Known demo seeds that still contain example-specific names:

- `packages/nl2uri/nl2uri/planner_templates.py` and graph/flow planners contain
  weather demo defaults used by examples and deterministic tests.
- `packages/urigen/urigen/artifacts.py` contains sample capability/flow mappings
  and demo URIs for generated ecosystems.
- `packages/urigen/urigen/generator.py` still emits a weather demo deployment when
  no explicit agent profile is supplied.
- `packages/uri3/contracts/*` contains mirrored example contracts for the bundled
  weather demo.

Those are demo-generation defaults, not the generic chat router. They should be
converted into profile artifacts when `urigen` profiles are externalized.

## Generated Agent Provenance

Every generated agent README should expose:

- source contract URI/path,
- contract hash,
- exact generation command,
- runtime command,
- `log://` URIs,
- `markpact:agent_generation` and `markpact:run_log` blocks.

This makes generated output reproducible and inspectable without reading package
internals.

# Markpact With touri and uri2flow

`touri` and `uri2flow` can load declarations from Markdown README files through
`markpact://` registry references.

This keeps the execution boundary unchanged:

```txt
README.md -> markpact block -> validated manifest/flow -> runtime
```

The loaders only parse fenced code blocks. They do not execute `markpact`.

## Capability Blocks (touri)

Use a fenced block named `markpact:capability`:

````md
```markpact:capability weather.forecast.markpact
version: 1

capability:
  id: weather.forecast.markpact
  scheme: weather
  uri_template: weather://markpact/{place}/{days}/html
  operation: generate
  kind: command

backend:
  type: python
  target: python://touri_examples.weather:handler
```
````

Then use the README as the `touri` registry:

```bash
touri list markpact://examples/22_markpact_weather/README.md

touri call weather://markpact/Gdansk/14/html \
  --registry markpact://examples/22_markpact_weather/README.md
```

Fragments select one block:

```bash
touri list markpact://examples/22_markpact_weather/README.md#weather.forecast.markpact
```

## Flow Blocks (uri2flow)

Use a fenced block named `markpact:flow`:

````md
```markpact:flow weather-health
flow:
  id: weather-health
  description: Generate weather agent, run it locally and verify health in Chrome.

do:
  - agent://weather-generator
  - hypervisor://local/weather-agent/run
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```
````

Expand it with uri2flow:

```bash
uri2flow expand markpact://examples/22_markpact_weather/README.md#weather-health \
  --out output/weather-health.uri.graph.yaml

uri2flow validate markpact://examples/22_markpact_weather/README.md#weather-health
uri2flow print markpact://examples/22_markpact_weather/README.md#weather-health
```

When a README contains multiple `markpact:flow` blocks, specify `#flow.id` in the URI.

## Example

See [`examples/22_markpact_weather`](../examples/22_markpact_weather/README.md).

## Agent provenance blocks (generated agents)

Each README under `agents/generated/*/README.md` includes blocks for **export and audit** (parsed by `uri2pact`, not auto-executed by `touri list`):

````md
```markpact:agent_generation weather-map-agent
agent:
  id: agent://weather-map-agent
  package: agents.generated.weather_map_agent
source:
  contract: contracts/agents/weather_map_agent.yaml
  contract_hash: sha256:...
generator:
  command: PYTHONPATH=packages/resource-agent-factory python -m generator.agent_generator ...
runtime:
  default_run: uvicorn agents.generated.weather_map_agent.main:app ...
logs:
  hypervisor: log://hypervisor?grep=weather-map-agent.local
  process: log://file/output/logs/agents/weather-map-agent.local.process.log
```

```markpact:run_log weather-map-agent.local.latest
inspect:
  command: hypervisor inspect-agent weather-map-agent.local
  uri: view://process/agent/weather-map-agent.local/latest
logs:
  hypervisor: log://hypervisor?grep=weather-map-agent.local
  process: log://file/output/logs/agents/weather-map-agent.local.process.log
```
````

Extract in Python:

```python
from pathlib import Path
import yaml
from uri2pact import extract_markpact_blocks

markdown = Path("agents/generated/weather_map_agent/README.md").read_text(encoding="utf-8")
for block in extract_markpact_blocks(markdown, "agent_generation"):
    print(yaml.safe_load(block["body"]))
```

Use this to import into external CMDBs, CI pipelines, or documentation systems without copying the whole hypervisor tree.

## Deployment blocks (`markpact:deploy`)

[`deployments/README.md`](../deployments/README.md) exports each local deployment as a portable block:

````md
```markpact:deploy weather-map-agent.local
deployment:
  id: weather-map-agent.local
  health_uri: http://localhost:8118/health
runtime:
  run: hypervisor run-agent weather-map-agent.local --detach --wait-healthy
supervise:
  watch: hypervisor supervise weather-map-agent.local --watch --repair auto --interval 15
logs:
  watch: log://file/output/logs/hypervisor-watch.jsonl
markpact:
  agent_generation: markpact://agents/generated/weather_map_agent/README.md#weather-map-agent
```
````

Parse:

```python
from pathlib import Path
import yaml
from uri2pact import extract_markpact_blocks

for block in extract_markpact_blocks(Path("deployments/README.md").read_text(), "deploy"):
    data = yaml.safe_load(block["body"])
    print(data["deployment"]["id"], data["supervise"]["watch"])
```

## Import into another system (checklist)

| Goal | Markpact / URI | Command |
|------|----------------|---------|
| Capabilities | `markpact:capability` in README | `touri list markpact://path/README.md` |
| Workflows | `markpact:flow` in README | `uri2flow expand markpact://path/README.md#flow-id` |
| Agent reproduction | `markpact:agent_generation` | parse → run `generator.command` |
| Ops / logs | `markpact:run_log` | parse → wire `log://` URIs to your log stack |
| Office NL scenarios | `markpact:scenario` in [`domains/office/README.md`](../domains/office/README.md) | `load_markpact_scenario_dicts("markpact://domains/office/README.md")` |
| Deployments | `markpact:deploy` in [`deployments/README.md`](../deployments/README.md) | parse → CMDB / runbooks / external orchestrator |
| Live fleet | HTTP JSON | `GET /api/agents`, `/api/events` on dashboard |
| YAML manifests (no README) | `*.uri.capability.yaml` | `touri list examples/20_touri_capabilities` |

Full walkthrough: [`TUTORIAL_THREE_AGENTS.md`](./TUTORIAL_THREE_AGENTS.md).

## Scope

Implemented now:

```txt
markpact:capability     -> touri load_registry/call/list
markpact:flow           -> uri2flow load_flow/expand/validate/print
markpact:deploy         -> uri2pact.extract_markpact_blocks (deployments/README.md)
markpact:scenario       -> uri2pact.scenarios.load_markpact_scenario_dicts
markpact:scenario_registry -> uri2pact.scenarios + urish.scenario_registry loader
markpact:agent_generation, markpact:run_log -> uri2pact.extract_markpact_blocks (parse only)
```

Planned later:

```txt
markpact:scenario (full external runtime without urish)
uri3 scan markpact://...
```

## Security

- `markpact://` provides declarations only
- `touri` / `uri2flow` validate structure before execution
- Do not auto-run `markpact:run` blocks when loading registries

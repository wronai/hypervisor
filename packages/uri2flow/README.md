# uri2flow v0.1

`uri2flow` is a small compiler for compact URI flows.

It converts human/LLM-friendly YAML:

```yaml
flow:
  id: weather-agent-local-health

do:
  - agent://weather-generator
  - hypervisor://local/weather-agent/run
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```

into an expanded `workflow_graph` manifest for `uri3`.

## Why this exists

Full workflow YAML is useful for machines, debugging and audit, but it is too verbose for humans and LLMs. The preferred input format should be URI-first and compact. `uri2flow` handles the expansion step.

## Role in the system

```text
nl2uri    -> natural language -> compact URI flow / URI graph
uri2flow  -> compact URI flow -> expanded workflow graph
uri3      -> validate, plan, route and execute graph
uri2ops   -> execute UI/OS/browser operations
hypervisor -> lifecycle, deployment, policy, registry
```

## Install

```bash
pip install -e .
```

## Commands

```bash
uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
uri2flow print examples/15_compact_uri_flow/weather.uri.flow.yaml
```

## Example

See [`examples/15_compact_uri_flow`](examples/15_compact_uri_flow/README.md).

## Design rule

`uri2flow` does not execute anything. It only parses, normalizes and expands compact URI flows.

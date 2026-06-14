# Standards used by Resource Agent Hypervisor v0.3

This project uses a small set of public standards plus a project-local registry format.

## MCP-style resources

Resources are addressed with semantic URIs such as `resource://users/{user_id}`. The runtime exposes these resources through a read operation equivalent to `resources/read`.

## Protobuf

Protobuf files in `contracts/proto/` are the IDL for events, commands and read models. The compatibility policy requires additive evolution, reserved deleted fields and no field-number reuse.

## JSON Schema 2020-12

JSON Schema validates YAML/JSON contracts:

- `contracts/registry.yaml`
- `contracts/resources.yaml`
- `contracts/views.yaml`
- `contracts/agents/*.yaml`
- `examples/08_evolution/proposals/*.yaml`

Schemas live in `schemas/`.

## URI configuration (`*.uri.yaml`)

Files ending in `.uri.yaml` contain URI-valued fields resolved by `uri3` (no `_uri`
field suffix inside these files). They are URI3 config artifacts with
`$schema`, `apiVersion`, `kind`, `metadata`, `uri.self`, and semantic content under
`spec`.

```txt
config/llm.uri.yaml
```

Rules:

- use `env://` or future `secret://` for secrets — never raw API keys in YAML
- resolve with `uri3.config.uri_yaml.load_uri_yaml`; loaders receive `spec`
- inspect the raw artifact envelope with `load_uri_yaml(path, unwrap_spec=False)`
- select LLM profile via `DEFAULT_LLM_PROFILE`

See [`CONFIG_URI_YAML.md`](./CONFIG_URI_YAML.md).

## A2A Agent Card

Generated agents expose public capability metadata through Agent Card. The canonical path is `/.well-known/agent-card.json`, with `/.well-known/agent.json` as an alias.

## Controlled proposal pipeline

The meta-agent produces proposals. The hypervisor validates schema, cross-references, compatibility and policy decisions before generation or deployment.

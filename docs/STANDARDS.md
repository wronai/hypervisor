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
- `evolution/proposals/*.yaml`

Schemas live in `schemas/`.

## A2A Agent Card

Generated agents expose public capability metadata through Agent Card. The canonical path is `/.well-known/agent-card.json`, with `/.well-known/agent.json` as an alias.

## Controlled proposal pipeline

The meta-agent produces proposals. The hypervisor validates schema, cross-references, compatibility and policy decisions before generation or deployment.

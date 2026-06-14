# Monorepo packages (v0.6)

Physical Python packages live under `packages/`:

| Directory | Distribution | Modules |
|---|---|---|
| `packages/uri3/` | `uri3` | `uri3` |
| `packages/nl2uri/` | `nl2uri` | `nl2uri`, `nl2a` |
| `packages/uri2flow/` | `uri2flow` | `uri2flow` |
| `packages/uri2ops/` | `uri2ops` | `uri2ops` |
| `packages/touri/` | `touri` | `touri`, `touri_examples` |
| `packages/resource-agent-hypervisor/` | `resource-agent-hypervisor` | `hypervisor`, `meta_agent`, `runtime_client` |
| `packages/resource-agent-factory/` | `resource-agent-factory` | `generator` |

Shared repo assets remain at the repository root:

```txt
contracts/ schemas/ domains/ agents/ deployments/ config/ examples/ output/ tests/
```

## Install

From repo root:

```bash
pip install -e '.[dev]'
pip install -e '.[browser]'    # Playwright (uri2ops + uri3 workflow)
pip install -e '.[windows]'   # pywinauto (uri2ops pcwin adapter)
```

Or with uv workspace:

```bash
uv sync
```

## CLI entry points

```bash
uri3 --help
uri2flow --help
nl2uri --help
nl2a --help
hypervisor --help
uri2ops --help
touri --help
```

## Capability manifests

```txt
examples/*/*.uri.capability.yaml
packages/touri/touri/schemas/uri_capability.schema.json
```

See [`docs/TOURI.md`](../docs/TOURI.md).

## Operator config

```txt
config/operator_policy.uri.yaml
config/operator_registry.uri.yaml
config/extra_operator_registry.yaml
packages/uri2ops/uri2ops/operation_registry/registry.yaml
```

See [`README.md`](../README.md), [`docs/TOURI.md`](../docs/TOURI.md), [`docs/URI2FLOW.md`](../docs/URI2FLOW.md), [`docs/URI2OPS.md`](../docs/URI2OPS.md), and [`examples/README.md`](../examples/README.md).

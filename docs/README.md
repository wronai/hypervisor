# Documentation index

## Start here

- [`README.md`](../README.md) — instalacja, Makefile, przykłady
- [`examples/README.md`](../examples/README.md) — katalog `examples/*/*`
- [`CHANGELOG.md`](../CHANGELOG.md)

## v0.5 (aktualne)

| Dokument | Temat |
|----------|--------|
| [`HYPERVISOR_WORKFLOW.md`](./HYPERVISOR_WORKFLOW.md) | Generacja + run-agent + logi |
| [`CONFIG_URI_YAML.md`](./CONFIG_URI_YAML.md) | Konwencja `*.uri.yaml` |
| [`ARCHITECTURE_V0_5.md`](./ARCHITECTURE_V0_5.md) | Podział uri3 / nl2uri / hypervisor |
| [`URI3.md`](./URI3.md) | CLI uri3, log://, schema |
| [`NL2URI.md`](./NL2URI.md) | prompt → URI Tree |
| [`NL2A_DOMAIN_PACKS.md`](./NL2A_DOMAIN_PACKS.md) | Domain Pack pipeline |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | Lokalnie, Docker, hypervisor `run-agent` |
| [`META_AGENT.md`](./META_AGENT.md) | Meta-agent CLI/API |
| [`EVOLUTION.md`](./EVOLUTION.md) | Evolution proposals |
| [`AUTO_EVOLUTION_PIPELINE.md`](./AUTO_EVOLUTION_PIPELINE.md) | Kontrolowana autoewolucja |
| [`STANDARDS.md`](./STANDARDS.md) | MCP, Protobuf, JSON Schema |

## Kontrakty i generator

| Dokument | Temat |
|----------|--------|
| [`CONTRACTS.md`](./CONTRACTS.md) | Format YAML agentów |
| [`GENERATOR.md`](./GENERATOR.md) | Agent factory |
| [`CONTRACT_REGISTRY.md`](./CONTRACT_REGISTRY.md) | Registry kontraktów |
| [`COMPATIBILITY_GOVERNANCE.md`](./COMPATIBILITY_GOVERNANCE.md) | Zasady kompatybilności |
| [`CAPABILITY_VERIFICATION.md`](./CAPABILITY_VERIFICATION.md) | Weryfikacja capability |

## Historyczne

| Dokument | Uwaga |
|----------|--------|
| [`URI2LLM.md`](./URI2LLM.md) | → dziś `uri3.resolvers` |
| [`HYPERVISOR_V0_4.md`](./HYPERVISOR_V0_4.md) | nl2a, uri2llm |
| [`HYPERVISOR_V0_3.md`](./HYPERVISOR_V0_3.md) | contract registry v0.3 |
| [`HYPERVISOR_V0_2.md`](./HYPERVISOR_V0_2.md) | wczesna architektura |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | ogólna architektura |
| [`ARCHITECTURE_META_FACTORY.md`](./ARCHITECTURE_META_FACTORY.md) | meta-factory |
| [`ROADMAP.md`](./ROADMAP.md) | roadmap wersji |

## Makefile (skrót)

```bash
make uri-tree graph nl2a-weather test
make validate generate verify
make meta-repair meta-pipeline
make docker-ssh-up scan-http docker-ssh-down
make evolution-check
make run-weather-agent
```

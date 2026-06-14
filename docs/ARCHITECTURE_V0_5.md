# Architecture v0.5–v0.6

Skanowanie usług, graf URI, workflow executor i `nl2uri` są w paczkach `uri3` / `nl2uri`. Wykonanie operatora — w `uri2ops`. Hypervisor zarządza rejestrem, polityką i lifecycle.

## Podział odpowiedzialności

```txt
uri3       = discovery, routing, graph, validation, workflow MVP, log://, schema
nl2uri     = natural language -> URI plan (single, list, tree, task, graph)
uri2flow   = compact URI flow -> expanded workflow graph (no execution)
uri2ops    = operation registry, operator adapters, policy, artifacts, serve
nl2a       = prompt -> URI Tree -> Domain Pack -> agent
hypervisor = policy, registry, lifecycle, deployment, audit
generator  = deterministyczny kod cienkiego agenta
Domain Pack = logika domenowa (domains/*)
Generated Agent = cienki adapter (agents/generated/*)
```

**Zasada:** Hypervisor nie klika ani nie steruje OS. `uri2ops` wykonuje akcje operatora przez URI-addressed operations.

## Monorepo

```txt
packages/uri3/
packages/nl2uri/          (+ nl2a)
packages/uri2flow/
packages/resource-agent-hypervisor/
packages/resource-agent-factory/
packages/uri2ops/          (+ uri2ops module)
```

Wspólne zasoby repo: `contracts/`, `schemas/`, `domains/`, `agents/`, `deployments/`, `config/`, `tests/`.

Instalacja: [`packages/README.md`](../packages/README.md).

## Pipeline agenta

```txt
prompt -> nl2uri -> URI Tree -> uri3 validate/graph
       -> Domain Pack -> contracts/agents/*.yaml
       -> generator -> agents/generated/<agent>/
       -> deployment registry sync
       -> hypervisor run-agent
```

## Pipeline operatora (v0.6)

```txt
prompt -> nl2uri task|graph|compact flow
       -> uri2flow expand (optional, for *.uri.flow.yaml)
       -> uri3 validate-workflow / plan-workflow
       -> uri3 run-workflow (MVP)  OR  uri2ops run (full runtime)
       -> events JSONL + artifact://
```

Docelowo: uri3 deleguje wykonanie do uri2ops (jeden backend adapterów).

## Przykłady

Uporządkowane w [`examples/`](../examples/README.md):

- agent factory: quickstart, weather-map, meta repair, evolution,
- nl2uri multi-output + LLM graph: `13_nl2uri_multi_uri_graph`, `16_llm_graph_planner`,
- workflow: `14_workflow_executor_mock`, `15_playwright_browser`,
- uri2ops: `10`–`14` (browser, playwright, android, pcwin, serve).

## Dokumentacja

- [`docs/URI2FLOW.md`](./URI2FLOW.md)
- [`docs/URI3.md`](./URI3.md)
- [`docs/NL2URI.md`](./NL2URI.md)
- [`docs/URI2OPS.md`](./URI2OPS.md)
- [`docs/NL2A_DOMAIN_PACKS.md`](./NL2A_DOMAIN_PACKS.md)
- [`docs/DEPLOYMENT.md`](./DEPLOYMENT.md)
- [`docs/META_AGENT.md`](./META_AGENT.md)
- [`docs/ROADMAP.md`](./ROADMAP.md)

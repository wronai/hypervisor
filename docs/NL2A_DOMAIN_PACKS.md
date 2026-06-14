# nl2a domain pack generation

`nl2a` tworzy URI Tree, Domain Pack, kontrakt agenta i wygenerowany kod.

```txt
prompt
  -> LLM/deterministic domain planner (nl2uri)
  -> URI Tree
  -> Domain Pack
  -> Agent YAML
  -> Agent Factory
  -> Contract Registry validation
  -> Deployment registry sync
```

Logika domenowa nie jest w rdzeniu hypervisora — powstaje w `domains/<domain_id>/`.

## Przykład

```bash
nl2a --no-llm -p "generuj mape pogody dwa tygodnie do przodu w oparciu o miejscowosc i odpowiedni model przewidujacy pogode, generuj widok w formie html pod adresem url"
```

Skrót:

```bash
make nl2a-weather
```

Oczekiwane artefakty:

```txt
domains/weather_map/uri_tree.yaml
domains/weather_map/domain.yaml
domains/weather_map/proto/weather_map.proto
domains/weather_map/resources.yaml
domains/weather_map/views.yaml
domains/weather_map/commands.yaml
domains/weather_map/renderers.yaml
contracts/agents/weather_map_agent.yaml
agents/generated/weather_map_agent/
output/contract_registry.resolved.json
```

Walidacja URI Tree:

```bash
uri3 validate-tree domains/weather_map/uri_tree.yaml
uri3 graph domains/weather_map/uri_tree.yaml
```

Przykład katalogowy: [`examples/04_nl2a_weather_map/`](../examples/04_nl2a_weather_map/README.md).

## LLM configuration

`.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=openrouter/qwen/qwen3-coder-next
NL2A_USE_LLM=1
```

Gdy `NL2A_USE_LLM=0` lub `--no-llm`, używany jest planner deterministyczny (testy reprodukowalne).

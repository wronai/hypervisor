# nl2a domain pack generation

`nl2a -p` generates a URI Tree first, then a Domain Pack, then a thin generated agent.

```txt
prompt
  -> LLM/deterministic domain planner
  -> URI Tree
  -> Domain Pack
  -> Agent YAML
  -> Agent Factory
  -> Contract Registry validation
```

The domain layer is not hard-coded into the hypervisor. It is generated under `domains/<domain_id>/` and registered through contracts.

## Example

```bash
nl2a -p "generuj mape pogody dwa tygodnie do przodu w oparciu o miejscowosc i odpowiedni model przewidujacy pogode, generuj widok w formie html pod adresem url"
```

Expected generated artifacts:

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
```

## LLM configuration

Use `.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=openrouter/qwen/qwen3-coder-next
NL2A_USE_LLM=1
```

When `NL2A_USE_LLM=0`, the local deterministic planner is used. This makes tests reproducible.

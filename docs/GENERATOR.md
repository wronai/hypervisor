# Generator agentów

## Walidacja

```bash
make validate
```

Walidator sprawdza, czy capability mają wymagane pola.

Dla `resource_read` wymagane są:

```txt
name
type: resource_read
uri
output_schema
renderer
```

Dla `command` wymagane są:

```txt
name
type: command
command
input_schema
```

## Generowanie

```bash
make generate
```

Albo pojedynczy agent:

```bash
python -m generator.agent_generator contracts/agents/user_agent.yaml
```

## Weryfikacja

```bash
make verify
```

Weryfikator sprawdza, czy wygenerowany agent nadal pasuje do `contract_hash` źródłowego YAML.

Jeżeli zmienisz YAML, uruchom ponownie:

```bash
make generate
make verify
```

## Szablony

Szablony są w:

```txt
generator/templates/
```

Możesz dodać nowe szablony, np. dla:

- OpenAPI extensions,
- MCP server,
- A2A JSON-RPC transport,
- docker-compose service,
- Helm chart.

## Czego nie robić

Nie edytuj ręcznie:

```txt
agents/generated/<agent>/
```

Zamiast tego:

1. zmień YAML,
2. zmień szablon,
3. wygeneruj ponownie,
4. uruchom testy.

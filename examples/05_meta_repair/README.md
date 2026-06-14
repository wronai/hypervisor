# Example 05 — meta-agent repair

Naprawa uszkodzonego kontraktu agenta regułami `meta_agent.repair`.

## Plik wejściowy

```txt
examples/05_meta_repair/broken_agent.yaml
```

## Podgląd naprawy (bez zapisu)

```bash
python -m meta_agent.cli repair examples/05_meta_repair/broken_agent.yaml
```

## Zapis naprawionego kontraktu

```bash
python -m meta_agent.cli repair examples/05_meta_repair/broken_agent.yaml --write
make meta-repair
```

## Sprawdzenie

Po `--write` waliduj wygenerowany plik:

```bash
python -m generator.validate contracts/agents
```

Oczekiwany wynik `repair` (dry-run): `changed: true`, `errors_after: []`.

## Typ błędów w `broken_agent.yaml`

- brakujące `output_schema` / `renderer` w `resource_read`
- duplikat capability
- brakujące pola w `command` capability

Brak runtime — to przykład **kontraktu**, nie uruchomionego agenta.

# uri2flow drop-in package

Ta paczka jest przygotowana do wklejenia do istniejącego repozytorium hypervisora bez nadpisywania głównych plików projektu.

## Co zawiera

- `packages/uri2flow/` — osobna paczka Python `uri2flow`.
- `tests/uri2flow/` — testy paczki.
- `examples/15_compact_uri_flow/` — przykład krótkiego flow URI.
- `integration/uri2flow/` — opcjonalne snippety integracyjne dla root `pyproject.toml`, `Makefile`, `README.md`.

## Szybkie uruchomienie po wklejeniu do repo

```bash
pip install -e packages/uri2flow
uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
pytest tests/uri2flow -q
```

## Ważne

Ta paczka niczego nie wykonuje. `uri2flow` tylko rozwija compact URI flow do pełnego `workflow_graph`, który może potem przejąć `uri3`.

Docelowy pipeline:

```txt
nl2uri -> compact URI flow -> uri2flow -> expanded workflow graph -> uri3 -> uri2ops/hypervisor
```

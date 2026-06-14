# Resource Agent Hypervisor v0.2

Ta wersja łączy trzy wcześniejsze warstwy w jeden kontrolowany układ:

1. **Shared Resource Runtime** — wspólny rdzeń CQRS / Event Sourcing / URI / Renderer.
2. **Agent Factory** — generator cienkich agentów z `contracts/agents/*.yaml`.
3. **Meta-Agent / Hypervisor** — planowanie, walidacja, naprawa i kontrolowana ewolucja.

Najważniejsza zmiana w v0.2 to formalny **Contract Registry** oraz warstwa **Compatibility / Governance**.

## Dlaczego Contract Registry jest centrum

Contract Registry jest źródłem prawdy dla:

- URI zasobów,
- projekcji,
- schematów Protobuf,
- rendererów,
- capability agentów,
- wersji i stabilności kontraktów.

Generator agentów nie powinien zgadywać. Ma czytać registry i generować cienkie adaptery.

## Zasada architektoniczna

```txt
LLM / Meta-Agent generuje propozycję lub YAML.
Generator tworzy kod.
Contract Registry sprawdza spójność.
Policy Gate decyduje, czy zmiana wymaga zatwierdzenia.
Testy capability potwierdzają działanie.
```

## Komendy

```bash
make validate
make registry
make generate
make verify
make capability-tests
make evolution-check
make hypervisor-check
pytest -q
```

## Co generowany agent posiada

Generowany agent ma:

- trasy HTTP,
- Agent Card,
- aliasy well-known,
- routing capability,
- klienta do wspólnego runtime,
- test kontraktowy.

Nie ma własnego event store, własnego CQRS ani własnych projekcji. To nadal jest cienki agent.

# Architektura Resource Agent Factory

## Cel

Projekt umożliwia automatyczne tworzenie wielu agentów na podstawie kontraktów. Agent jest cienką warstwą wejściową, która wystawia capability i deleguje wykonanie do wspólnego Resource Runtime.

## Główna idea

```txt
Contract Registry
      ↓
Agent Specification YAML
      ↓
Agent Factory / Generator
      ↓
Generated Thin Agent
      ↓
Shared Resource Runtime
```

## Dlaczego cienki agent

Cienki agent:

- nie duplikuje logiki domenowej,
- nie ma własnego event store,
- nie ma własnych projekcji,
- deleguje odczyty do URI,
- deleguje zapis do command API,
- jest prosty do wygenerowania i zweryfikowania.

To pasuje do architektury, gdzie źródłem prawdy jest runtime zasobów, a nie pojedynczy agent.

## Warstwy

### 1. Contracts

Katalog `contracts/` zawiera specyfikacje:

```txt
contracts/
  agents/*.yaml
  proto/*.proto
```

Najważniejszy jest plik `contracts/agents/<agent>.yaml`, który opisuje:

- nazwę agenta,
- wersję,
- capability,
- URI zasobów,
- komendy,
- schematy wejścia/wyjścia.

### 2. Generator

Generator czyta YAML i tworzy kod:

```txt
agents/generated/<agent>/
  main.py
  routes.py
  agent_card.py
  Dockerfile
  README.md
  tests/test_contract.py
```

### 3. Runtime Client

`runtime_client/client.py` jest małym klientem HTTP do Resource Runtime.

Wygenerowany agent używa go do:

```txt
GET  /resources/read?uri=...
POST /commands
```

### 4. Generated Agent

Wygenerowany agent wystawia:

```txt
GET  /health
GET  /capabilities
GET  /.well-known/agent.json
GET  /.well-known/agent-card.json
GET  /resources/read?uri=...
POST /commands
GET/POST /skills/<capability>
```

### 5. Custom Handlers

Ręczna logika powinna trafiać do `agents/custom/`, a nie do `agents/generated/`.

## Zasada bezpieczeństwa architektonicznego

Agent generowany nie powinien samodzielnie zmieniać kontraktów ani kodu produkcyjnego. Może zostać wygenerowany ponownie z kontraktu albo rozszerzony przez zatwierdzony handler.

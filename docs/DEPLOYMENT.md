# Wdrożenie

## Lokalnie

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
make validate generate verify test
uvicorn agents.generated.user_agent.main:app --reload --port 8101
```

## Docker dla wygenerowanego agenta

Po wygenerowaniu:

```bash
docker build -f agents/generated/user_agent/Dockerfile -t user-agent:0.1.0 .
docker run -p 8101:8101 -e RESOURCE_RUNTIME_URL=http://host.docker.internal:8000 user-agent:0.1.0
```

## Zmienne środowiskowe

```txt
RESOURCE_RUNTIME_URL=http://localhost:8000
```

## Integracja z Resource Runtime

Agent oczekuje, że runtime ma endpointy:

```txt
GET  /resources/read?uri=resource://...
POST /commands
```

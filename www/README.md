# Hypervisor Chat (`www/`)

Prosty interfejs czatu z renderowaniem markdown, podłączony do realnego API `hypervisor-dashboard-agent`.
Strona jest statyczna, ale działa na tym samym FastAPI co dashboard systemowy, więc widzi realne
deploymenty, statusy i policy-gated URI calls.

## Uruchomienie

### Docker (zalecane)

```bash
make start          # build + uruchom kontener
make www-smoke      # test health / www / api/ask
make stop           # zatrzymaj kontener
make www-logs       # logi
```

Chat: http://localhost:8788/www/

### Lokalnie (bez Docker)

```bash
# z katalogu repo (wymaga editable install pakietów)
urish www serve
# lub
urish www open
```

### Tworzenie z NL

```bash
urish www create "stwórz prosty chat markdown połączony z API systemu" --plan-only
urish www create "stwórz dashboard agenta hypervisor-dashboard do procesów i napraw" --approve --open
```

## Jak to działa

| Akcja | Endpoint |
|-------|----------|
| Prompt NL | `POST /api/ask` → `urish.backends.ask.ask_prompt` |
| Preview URI | `POST /api/uri/preview` → policy preview |
| URI | `POST /api/uri/call` → policy gate + wykonanie |
| Agenci | `GET /api/agents` |
| Zdarzenia | `GET /api/events` |
| Status | `GET /health` |

- Wpisz naturalny język — dostaniesz plan URI i komendy `urish` jako markdown.
- Wklej URI — wykonanie przez policy (domyślnie dry-run).
- Panel boczny pokazuje zdrowie API, deploymenty agentów i ostatnie zdarzenia.
- Przy blokach kodu i URI: **Kopiuj**, **Podgląd URI**, **Dry-run URI**.

## Pliki

- `index.html` — chat (główna strona pod `/www/`)
- `app.js` — logika czatu i API
- `styles.css` — prosty layout
- `demo.html` — poprzednia statyczna wizualizacja Taskinity

## Tworzenie przez NL (CLI)

Chat to wizualizacja tego samego co:

```bash
urish ask "stwórz dashboard agenta hypervisor"
urish www create "stwórz prosty chat markdown połączony z API systemu" --plan-only
urish ecosystem plan --prompt "..."
```

Serwer musi działać w katalogu repo, aby `www/` było zamontowane i `find_repo_root()` działało.

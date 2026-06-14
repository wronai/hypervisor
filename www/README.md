# Hypervisor Chat (`www/`)

Prosty interfejs czatu z renderowaniem markdown, podłączony do realnego API dashboard-agent.

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

## Jak to działa

| Akcja | Endpoint |
|-------|----------|
| Prompt NL | `POST /api/ask` → `urish.backends.ask.ask_prompt` |
| URI | `POST /api/uri/call` → policy gate + wykonanie |
| Status | `GET /health` |

- Wpisz naturalny język — dostaniesz plan URI i komendy `urish` jako markdown.
- Wklej URI — wykonanie przez policy (domyślnie dry-run).
- Przy blokach kodu: **Kopiuj** / **Dry-run URI** gdy wykryto URI.

## Pliki

- `index.html` — chat (główna strona pod `/www/`)
- `app.js` — logika czatu i API
- `styles.css` — prosty layout
- `demo.html` — poprzednia statyczna wizualizacja Taskinity

## Tworzenie przez NL (CLI)

Chat to wizualizacja tego samego co:

```bash
urish ask "stwórz dashboard agenta hypervisor"
urish ecosystem plan --prompt "..."
```

Serwer musi działać w katalogu repo, aby `www/` było zamontowane i `find_repo_root()` działało.

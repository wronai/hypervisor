# Taskinity WWW (`www/`)

Strona produktowa + interfejs czatu podłączony do API `hypervisor-dashboard-agent`.

## Strony

| URL | Plik | Opis |
|-----|------|------|
| `/www/` | `index.html` | **Landing** — prezentacja produktu, slajdy, animacje |
| `/www/chat.html` | `chat.html` | **Chat na żywo** — NL → plan URI, wywołania API |
| `/www/demo.html` | `demo.html` | Demo techniczne URI (statyczne) |

## Uruchomienie

### Docker (zalecane)

```bash
make start          # build + uruchom kontener
make www-smoke      # test health / www / chat / api/ask
make stop           # zatrzymaj kontener
make www-logs       # logi
```

- Landing: http://localhost:8788/www/
- Chat: http://localhost:8788/www/chat.html

Compose montuje katalogi runtime z hosta (patrz `docker-compose.yml`).

### Lokalnie (bez Docker)

```bash
urish www serve
# lub
urish www open
```

## Landing page

Pliki:

- `index.html` — struktura sekcji (hero, problem, tour, oferta, FAQ)
- `landing.css` — styl, animacje, responsywność
- `landing.js` — interaktywna prezentacja 6 kroków (autoplay, pauza, nawigacja)

Sekcja **„Jak to działa w praktyce”** pokazuje scenariusz faktur → ERP 401 → chat → incident → ticket → proof techniczny.

Copy marketingowe: [`../market/LANDING_COPY.md`](../market/LANDING_COPY.md)

## Chat (`chat.html`)

| Akcja | Endpoint |
|-------|----------|
| Prompt NL | `POST /api/ask` |
| Preview URI | `POST /api/uri/preview` |
| URI | `POST /api/uri/call` |
| Agenci | `GET /api/agents` |
| Zdarzenia | `GET /api/events` |

Pliki: `app.js`, `styles.css`.

## Tworzenie przez NL (CLI)

```bash
urish ask "stwórz dashboard agenta hypervisor"
urish www create "stwórz prosty chat markdown połączony z API systemu" --plan-only
```

## Monitoring landingu

```bash
make www-monitor       # uruchom sprawdzenia teraz
make www-monitor-test  # testy monitoringu, webhooka i crona
make www-monitor-reset # nowa baseline cen po celowej zmianie
```

Cron:

```bash
bash scripts/www/install-cron.sh            # podgląd wpisu
bash scripts/www/install-cron.sh --install  # instalacja co 5 min
bash scripts/www/install-cron.sh --status   # status + ostatnie linie logu
bash scripts/www/install-cron.sh --remove   # usunięcie wpisu
```

`--install` przygotowuje `/tmp/taskinity-monitor.log`, więc `tail -f /tmp/taskinity-monitor.log`
nie powinien padać przed pierwszym przebiegiem crona. Dla n8n/Slack/Make podaj prawdziwy URL:

```bash
bash scripts/www/install-cron.sh --update --webhook "https://hooks.n8n.cloud/webhook/real-token"
```

Adresy przykładowe typu `twoja-instancja...`, `hooks.example...` albo `abc123` są traktowane jako placeholder i nie są wysyłane do webhooka.

# Demo 10 minut — slajdy + live

Scenariusz spotkania sprzedażowego: **historia biznesowa (7 min) + proof techniczny (3 min)**.

Powiązane: [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) (wersja rozszerzona), [STRATEGY.md](./STRATEGY.md).

---

## Struktura spotkania

| Min | Co | Forma |
|-----|-----|-------|
| 0–1 | Problem (ból 9:00) | Slajd |
| 1–2 | Co robi Taskinity (bez URI) | Slajd |
| 2–7 | Live: faktury → błąd → chat → incident → ticket | Ekran |
| 7–9 | Bonus tech: to samo URI w CLI/API + `urish proof` | Ekran |
| 9–10 | Oferta pilota + pytanie walidacyjne | Slajd |

---

## Slajd 1 — Problem (60 s)

**Tytuł:** Znasz ten poniedziałek o 9:00?

**Bullet points (cytaty klienta):**

- Automatyzacja faktur znowu nie działa — nie wiem, gdzie szukać
- n8n poszło, dane nie doszły do ERP
- Skrypt pisał ktoś, kto już nie pracuje
- Brak jednego widoku: cron, webhooki, pipeline, agenci

**Nie pokazuj:** URI, control plane, MCP.

**Mówisz:** „Dziś pokażę, jak w jednym chacie dostajecie odpowiedź: co padło, dlaczego i co dalej.”

---

## Slajd 2 — Rozwiązanie (60 s)

**Tytuł:** Taskinity — command center dla automatyzacji

**Jeden akapit:**

> Jeden chat i dashboard dla skryptów, webhooków, n8n, API, Dockera i agentów AI. Health, logi, incident, ticket i propozycja naprawy. **Nie zastępujemy** n8n ani GitHub Actions.

**3 ikony:**

1. **Widok** — co działa / co padło  
2. **Chat** — pytasz po polsku  
3. **Akcja** — incident → ticket → naprawa (z podglądem)

---

## Live 3–7 — Historia faktur (5 min)

### Setup (powiedz na głos)

> „Firma ma automatyzację faktur — codziennie o 7:00. Dziś 14 faktur nie weszło do ERP.”

### Krok 1: Chat (90 s)

1. Otwórz `http://localhost:8788/www/` (lub nagranie)
2. Wpisz: **„Dlaczego faktury nie weszły do systemu?”**
3. Pokaż odpowiedź: proces znaleziony, ostatni run failed, wskazówka przyczyny

**Mówisz:** „Użytkownik biznesowy nie zna URI — pyta normalnym językiem.”

### Krok 2: Szczegóły (60 s)

- Ostatnie wykonanie: **failed**
- Przyczyna: **API ERP → 401**
- Hipoteza: **wygasły token**
- Link do logów / health

### Krok 3: Incident (60 s)

- Pokaż utworzony **incident** (artifact lub UI)
- „Każdy błąd ma historię — nie ginie w Slacku.”

### Krok 4: Ticket + naprawa (90 s)

- „Utwórz ticket z incidentu”
- Pokaż **repair proposal**: odśwież token / sprawdź secret / retry
- **Dry-run** → „Najpierw podgląd, potem zatwierdzenie — bez autonomicznego chaosu”

### Krok 5: Zamknięcie biznesowe (30 s)

> „Zamiast 2–3 godzin w logach i pięciu narzędziach — jeden chat, jedna ścieżka: status → przyczyna → ticket → naprawa.”

---

## Live 7–9 — Proof techniczny (2 min)

**Tytuł slajdu:** Dla zespołu technicznego — to nie jest tylko chat

### Opcja A: `urish proof` (docelowo)

```bash
urish proof view://process/agent/weather-map-agent.local/latest
```

Output — [STRATEGY.md §7](./STRATEGY.md).

**Mówisz:** „Jeden identyfikator procesu przechodzi przez chat, API, CLI i runtime. Trudno to podrobić bez architektury.”

### Opcja B: ręczny proof (do czasu implementacji)

```bash
# Chat już pokazany
curl -s -X POST http://localhost:8788/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"health agenta faktur"}'

curl -s -X POST http://localhost:8788/api/uri/call \
  -H 'Content-Type: application/json' \
  -d '{"uri":"health://agent/...","dry_run":true}'

urish call health://agent/...
```

**Slajd podsumowujący:**

```text
Chat     →  POST /api/ask
API      →  POST /api/uri/call
CLI      →  urish call
Runtime  →  http / shell / docker
```

**vs LangSmith Engine (1 zdanie):**

> „Engine naprawia agentów LangChain z trace’ów. My spinamy webhooki, cron, n8n i agentów — jeden widok.”

---

## Slajd 10 — Oferta + CTA (60 s)

**Tytuł:** Pilot 7–14 dni, 3 procesy

| | |
|---|---|
| **Cena** | 8 000–15 000 zł netto |
| **Zakres** | webhook/API + cron/skrypt + docker (lub n8n) |
| **Deliverable** | chat + dashboard + health + incident + ticket + raport czasu |

**Pytanie walidacyjne:**

> „Czy zapłacilibyście ~10k zł za jedno miejsce, które mówi: który proces padł, dlaczego i co dalej — na trzech waszych realnych automatyzacjach?”

**CTA:** audyt 2 500 zł (1–3 dni) lub pilot od razu.

Oferty: [OFFERS.md](./OFFERS.md).

---

## Checklist przed spotkaniem

- [ ] Demo faktur działa end-to-end (host lub Docker z volume)
- [ ] Backup: nagranie wideo 3 min
- [ ] Slajdy 1–2–10 (PDF lub Notion)
- [ ] Znać 3 procesy prospecta (z LinkedIn / rozmowy wstępnej)
- [ ] Nie mówić „control plane” ani „URI-first” w pierwszych 7 minutach

---

## Warianty per ICP (co podkreślić)

| ICP | Historia live | Procesy w pilocie |
|-----|---------------|-------------------|
| Software house | webhook klienta + CI | GitHub Action, API, cron |
| Integrator n8n | n8n OK, ERP nie dostał | 3 scenariusze n8n klientów |
| E-commerce | zamówienia Allegro → ERP | zamówienia, faktury, zwroty |

Wiadomości: [SALES_MESSAGES.md](./SALES_MESSAGES.md).

# Go-to-market — Polska

Plan wejścia: **command center dla automatyzacji** (nie „URI-first control plane” na pierwszym ekranie).  
Strategia zaostrzona: [ASSESSMENT.md](./ASSESSMENT.md).

## Cel 30 dni (discovery first)

| Tydzień | Cel | Konkret |
|---------|-----|---------|
| 1 | Demo + lista leadów | 1 landing ([LANDING_COPY.md](./LANDING_COPY.md)), 1 demo wideo, 100 firm |
| 2 | Rozmowy | 30 wiadomości do software house’ów, 10 rozmów |
| 3 | Pilotaże | 3 darmowe/niskopłatne audyty |
| 4 | Sprzedaż | 2 płatne piloty, **1 partner wdrożeniowy (integrator)** |

**Zasada:** 30 dni discovery, nie dopisywanie funkcji.

## Cel 90 dni

| Metryka | Cel |
|---------|-----|
| Rozmowy discovery | 10+ |
| Pilotaże podpisane | 2 |
| Partner integrator | 1 |
| Demo nagrane | 1 techniczne + 1 sprzedażowe (faktury) |
| Product gaps domknięte | Docker repair + `urish proof` |

## Fazy

### Faza 1 — Proof (tygodnie 1–4)

**Deliverables:**

- Domknięcie demo E2E ([PRODUCT_READINESS.md](./PRODUCT_READINESS.md))
- Nagranie [DEMO_SCRIPT.md](./DEMO_SCRIPT.md)
- One-pager PL (PDF z `POSITIONING.md` + `MARKET_HYPOTHESIS.md`)
- Battlecard dla rozmów sprzedażowych ([BATTLECARD.md](./BATTLECARD.md))

**Techniczne:**

```bash
make start
make www-smoke
bash examples/30_golden_path/run.sh
```

- Volume `agents/generated` w docker-compose
- README pilota w `market/` (ten dokument + linki)

### Faza 2 — Discovery + pilot (tygodnie 5–12)

**ICP #1:** software house 10–80 os.  
**ICP #2 (kanał priorytetowy):** integratorzy n8n / Make / Power Automate.

**Kanały:**

| Kanał | Działanie |
|-------|-----------|
| Integratorzy n8n/Make | **#1** — oferta panelu serwisowego + SLA |
| Software house’y | Outreach PL, 1300+ firm ICT (PAIH) |
| Sieć własna | Tech leadów, CTO |
| Meetupy DevOps / AI | 15-min demo „faktury → błąd API” |
| LinkedIn PL | „Chaos automatyzacji → command center” (bez żargonu URI) |

**Oferty:** [OFFERS.md](./OFFERS.md)

| Pakiet | Cena | Czas |
|--------|------|------|
| Audyt automatyzacji | 2 500–5 000 zł | 1–3 dni |
| Pilot 3 procesów | 5 000–15 000 zł | 7–14 dni |
| Utrzymanie | 1 500–4 000 zł/mies. | ciągłe |

**Deliverable pilota:**

1. Działający dashboard + chat (self-host u klienta lub u Ciebie)
2. Health check na wskazanych procesach/agentach
3. Jeden przeprowadzony scenariusz repair (dry-run + approve)
4. Dokumentacja URI dla ich stacku (1 strona)
5. Opcjonalnie: eskalacja 1 ticket → evolution proposal

### Faza 3 — Productizacja (po pierwszym pilocie)

- Pakiet instalacyjny: `make start` + opcjonalnie uri2ops
- Cennik: OSS core + support / retainer (np. 2–4 tys. zł/mies. po pilocie)
- Case study publiczny (za zgodą klienta)
- Conformance `agent://` Level 1

## Pytania discovery

**Pytanie walidacyjne (każda rozmowa):**

> „Czy zapłacilibyście **X zł** za jedno miejsce, które mówi: **który proces padł, dlaczego i co dalej**?”

Notuj: słowa reakcji (health, incident, n8n, cron) + **3 procesy** kandydatów do pilota.

```text
Jakie automatyzacje macie dziś w firmie?
Co najczęściej się psuje?
Gdzie szukacie logów?
Ile trwa ustalenie przyczyny?
Kto odpowiada za naprawę?
Czy klient widzi status procesu?
Jakie 3 procesy podłączylibyście jako pierwsze?
```

## Messaging per kanał

Gotowce: [SALES_MESSAGES.md](./SALES_MESSAGES.md) (3 segmenty × 2 wersje). Demo: [DEMO_10MIN.md](./DEMO_10MIN.md).

### Cold outreach (software house)

> Taskinity — command center dla automatyzacji i skryptów. Nie zastępuje n8n ani GitHub Actions. Jeden widok: co działa, co padło, logi, incident, naprawa. Pilot 7–14 dni, 3 procesy. 10-min demo?

### Partner integrator (#1 kanał)

> Panel serwisowy dla wdrożeń n8n/Make — status, błędy, ticket, SLA dla klientów. Pilot 5–12k zł, potem abonament utrzymania.

### LinkedIn

> Automatyzacja faktur znowu nie działa? n8n OK, dane nie weszły? Taskinity pokazuje gdzie, dlaczego i co dalej — jeden chat i dashboard.

## Obiekcje i odpowiedzi

| Obiekcja | Odpowiedź |
|----------|-----------|
| „Mamy LangSmith / Engine” | Engine naprawia LangChain z trace’ów; my spinamy też cron, webhooki, n8n |
| „To brzmi zbyt technicznie (URI)” | Użytkownik widzi chat; URI jest dla devops i audytu |
| „Czy to nie duplikat n8n?” | n8n buduje workflow; my operujemy gdy workflow/agent padnie |
| „Czy mamy SOC2?” | Nie — policy gate i self-host; enterprise gov to inna kategoria |
| „Co jeśli nie mamy agentów LLM?” | Health/repair działa na deploymentach, skryptach, webhookach |

## KPI tygodniowe (Faza 2)

| Tydzień | Cel |
|---------|-----|
| 5–6 | 3 rozmowy discovery |
| 7–8 | 2 demo live |
| 9–10 | 1 propozycja pilota |
| 11–12 | 1 podpisany pilot lub iteracja oferty |

## Po pilocie — upsell

| Produkt | Opis |
|---------|------|
| Retainer support | 2–4 tys. zł/mies., SLA na repair playbooki |
| Integracja n8n | Webhook → `incident://` |
| Evolution workshop | Ticket → proposal → apply z zespołem klienta |
| Szkolenie URI | 1 dzień dla dev team |

## Dokumenty sprzedażowe

1. [ASSESSMENT.md](./ASSESSMENT.md) — strategia zaostrzona
2. [OFFERS.md](./OFFERS.md) — oferty i wiadomości
3. [LANDING_COPY.md](./LANDING_COPY.md) — strona www
4. [BATTLECARD.md](./BATTLECARD.md) — vs LangSmith Engine, n8n
5. [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) — demo techniczne + sprzedażowe
6. [PRODUCT_READINESS.md](./PRODUCT_READINESS.md) — scope MVP

## Ryzyka GTM

| Ryzyko | Mitigacja |
|--------|-----------|
| Demo pada na Docker | Naprawić przed outreach ([PRODUCT_READINESS.md](./PRODUCT_READINESS.md)) |
| Zbyt szeroki scope pilota | Max 3 deploymenty, fixed price |
| Brak case study | Wewnętrzny weather-map-agent przed pierwszym klientem |
| Konkurencja cenowa OSS | Sprzedawać efekt i czas, nie „platformę” |

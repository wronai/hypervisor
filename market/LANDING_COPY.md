# Landing page — copy (PL)

Teksty na stronę sprzedażową. **URI i „control plane” tylko w sekcji technicznej**, nie w nagłówku.

Strategia: [STRATEGY.md](./STRATEGY.md) · Demo: [DEMO_10MIN.md](./DEMO_10MIN.md).

---

## Hero

### Nagłówek

> **Automatyzacje i agenci AI przestali działać? Taskinity pokaże gdzie, dlaczego i co zrobić dalej.**

### Podtytuł

> Jeden chat i dashboard dla skryptów, webhooków, n8n, API, Dockera i agentów AI. Health, logi, incident, ticket i propozycja naprawy.

### Kompas (wewnętrzny — nie na hero)

> W jednym chacie widzisz, co działa, co padło, dlaczego i co z tym zrobić.

### CTA primary

> **Umów 10-min demo** · **Audyt automatyzacji od 2 500 zł**

### CTA secondary

> Zobacz: faktury nie weszły do ERP → chat → incident → naprawa

---

## Sekcja: Problem (język 9:00)

**Nagłówek:** Znasz ten poniedziałek o 9:00?

- Automatyzacja faktur znowu nie działa — nie wiem, gdzie tego szukać
- Scenario w n8n poszedł, ale dane nie doszły do ERP
- Agent miał zrobić ticket, a wysłał zły mail do klienta
- Skrypt pisał ktoś, kto już nie pracuje — nie wiemy, czy w ogóle działa
- Nie mam jednego miejsca na crony, webhooki, pipeline’y, agentów i status

**Nagłówek:** Taskinity daje odpowiedź w minutach, nie godzinach.

---

## Sekcja: Co dostajesz

| Funkcja | Opis biznesowy |
|---------|----------------|
| **Jeden widok** | Cron, API, Docker, n8n, agenci — bez pięciu narzędzi |
| **Chat po polsku** | „Co się stało z procesem faktur?” → status, przyczyna, logi |
| **Health** | Co działa, co nie |
| **Incident** | Błąd zapisany z kontekstem — nie ginie w Slacku |
| **Ticket** | Eskalacja do naprawy lub zmiany w systemie |
| **Naprawa** | Propozycja kroków — podgląd, potem zatwierdzenie |

**Nie obiecuj:** pełnego tracingu LLM (to LangSmith/Langfuse). **Obiecuj:** kontrolę nad chaosem automatyzacji.

---

## Sekcja: Dla kogo

| Segment | Korzyść |
|---------|---------|
| **Software house’y** | Panel procesów dla projektów i klientów; odsprzedaż utrzymania |
| **Integratorzy n8n / Make** | Warstwa SLA nad wdrożeniami — panel serwisowy |
| **E-commerce** | Zamówienia, faktury, ERP, marketplace — jeden chat przy awarii |
| **Biura i BPO** | Dokumenty, OCR, KSeF — widok od maila do systemu |

**Polska przewaga:** wdrożenie, język polski, wsparcie lokalne ([Trade.gov](https://www.trade.gov/country-commercial-guides/poland-digital-economy)).

---

## Sekcja: Jak to działa (3 kroki, bez URI)

1. **Podłączamy 3 procesy** — webhook/API, skrypt/cron, docker (lub n8n)
2. **Pytasz w chacie** — „dlaczego faktury nie weszły?”
3. **Dostajesz** — status, przyczynę, incident, ticket, propozycję naprawy

---

## Sekcja: Oferta

Ścieżka: audyt → pilot → utrzymanie.

| Pakiet | Cena | Czas |
|--------|------|------|
| Audyt automatyzacji | 2 500–5 000 zł | 1–3 dni |
| Pilot 3 procesów | 8 000–15 000 zł | 7–14 dni |
| Utrzymanie | 1 500–4 000 zł / mies. | ciągłe |

Szczegóły: [OFFERS.md](./OFFERS.md).

---

## Sekcja techniczna (scroll w dół)

**Nagłówek:** Dla zespołów technicznych

> Pod spodem każdy proces jest **URI**. To samo URI możesz uruchomić przez Web UI, API, CLI, workflow, shell, Docker, SSH albo innego agenta.

> Taskinity = **URI execution and repair layer** over agents, workflows and tools — zgodnie z kierunkiem MCP, A2A i `agent://` (IETF).

**Dowód (demo):**

```bash
urish proof view://process/agent/weather-map-agent.local/latest
```

**API:**

- `POST /api/ask` — pytanie NL → plan URI
- `POST /api/uri/call` — wykonanie URI (dry-run / approve)

**Integracje MVP:** `http://`, `shell://`, `docker://` — potem n8n, GitHub Actions, MCP.

**Observability LLM:** integracja Langfuse / Phoenix / LangSmith — nie duplikujemy deep trace.

---

## Sekcja: vs inne narzędzia (FAQ skrót)

**Czy zastępujecie n8n / Make / Zapier?**  
Nie. Masz już automatyzacje — my pokazujemy, które działają, które padły i co dalej.

**Czym różnicie się od LangSmith / LangSmith Engine?**  
[LangSmith Engine](https://www.langchain.com/blog/introducing-langsmith-engine) naprawia agentów LangChain z production traces. Taskinity spinamy **cały** chaos: skrypty, cron, webhooki, n8n, Docker i agentów — jeden command center.

**Czy to dla firm bez agentów AI?**  
Tak — skrypty, cron i webhooki często padają pierwsze.

**Czy macie SOC2 / enterprise governance?**  
Nie — produkt dla MŚP i software house’ów, self-host z policy gate.

**Czy budujecie własny Langfuse?**  
Nie — integrujemy jako źródło sygnałów do trace LLM.

---

## Social proof (placeholder)

- „Pilot 3 procesów — diagnoza z 2h do 15 min” (case study po kliencie)
- Polski support · wdrożenie · audyt od 2 500 zł

---

## Meta / SEO (propozycja)

**Title:** Taskinity — command center dla automatyzacji i agentów AI  
**Description:** Jeden chat i dashboard: co działa, co padło, incident, ticket, naprawa. Skrypty, n8n, API, Docker. Polski pilot 7–14 dni.

---

Powiązane: [SALES_MESSAGES.md](./SALES_MESSAGES.md), [DEMO_10MIN.md](./DEMO_10MIN.md).

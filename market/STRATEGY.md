# Strategia zaostrzona — Taskinity (PL market)

Kanoniczny dokument strategiczny. Wersja po korekcie researchu i feedbacku rynkowego (2026-06).

Powiązane: [ASSESSMENT.md](./ASSESSMENT.md) (krytyka pierwotnego researchu), [POSITIONING.md](./POSITIONING.md), [GTM_POLAND.md](./GTM_POLAND.md).

---

## 1. Nazwa kategorii: zewnątrz vs sekret techniczny

### 1.1 Unikamy tłoku „AI agent control plane”

Fraza **„AI control plane / AI agent control plane”** jest okopana przez graczy governance/security: Speakeasy, Datafi, referencyjne architektury enterprise (identity, policy, observability, approvals). [Speakeasy](https://www.speakeasy.com/resources/ai-control-plane) · [C# Corner — reference architecture](https://www.c-sharpcorner.com/article/reference-architecture-for-an-ai-control-plane-the-technical-blueprint-for-gove/) · [Treza Labs](https://www.trezalabs.com/blog/what-is-an-ai-control-plane)

**Ryzyko hasła „URI-first agent control plane” na pierwszym ekranie:**

- mylenie z narzędziami compliance/audytu,
- konkurencja enterprise-first od razu.

| Warstwa | Komunikat |
|---------|-----------|
| **Externally** (landing, sprzedaż, slajdy 1–3) | „Taskinity – prosty command center dla automatyzacji, skryptów i agentów AI. Pokazuje, co działa, co padło, dlaczego padło i co zrobić dalej.” |
| **Internally** (po kilku minutach z tech leadem) | „Pod spodem URI-first control plane: każdy proces jest URI wykonywalne z chatu, API, CLI, workflow, shell, Docker, SSH, MCP/A2A.” |
| **Docs / konferencje EN** | „URI execution and repair layer over agents, workflows and tools.” |

**URI = przewaga demo i architektura, nie pierwszy nagłówek.**

---

## 2. Konkurencja: odcinanie się od LangSmith Engine

### 2.1 Co robi LangSmith Engine

[LangSmith Engine](https://www.langchain.com/blog/introducing-langsmith-engine) · [observability docs](https://docs.langchain.com/langsmith/observability-llm-tutorial) · [production guide](https://www.abhishekchauhan.it/blog/langsmith-production-observability-evaluation-debugging)

- ogląda production traces,
- grupuje powtarzające się błędy w issues,
- diagnozuje root cause w kodzie/promptach,
- proponuje fix (PR), evaluator, dataset,
- zamyka pętlę: failure → issue → fix → eval.

**Claim „tylko my mamy observe → repair” jest nieaktualny.**

### 2.2 Bezpieczna różnica

> LangSmith Engine naprawia agentów zbudowanych na LangChain/LangGraph, wewnątrz ich ekosystemu. Taskinity spina **dowolne** procesy — skrypty, cron, API, Docker, SSH, n8n/Make, GitHub Actions, RPA, agenci w różnych frameworkach — jednym modelem URI i jednym widokiem health/incident/ticket.

| | LangSmith / observability | Taskinity |
|---|---------------------------|-----------|
| Zakres | Deep tracing jednego stosu agenta | Szeroki command center nad wieloma stosami |
| Legacy | Słabo | Skrypty, cron, webhooki, n8n |
| Biznes UX | MLOps | Chat po polsku: „co się stało z procesem X?” |
| Tracing LLM | ✅ core | Integracja Langfuse/Phoenix/LangSmith jako sygnał |

**Nie buduj własnego Langfuse.** Integruj jako źródło sygnałów. [Braintrust buyer guide 2026](https://www.braintrust.dev/articles/best-ai-observability-tools-2026)

Battlecard: [BATTLECARD.md](./BATTLECARD.md).

---

## 3. Value prop: ból o 9:00 rano

### 3.1 Jak klient nazywa problem

Pełna lista: [PAIN_LANGUAGE.md](./PAIN_LANGUAGE.md).

- „Automatyzacja faktur znowu nie działa – nie wiem, gdzie tego szukać.”
- „Scenario w n8n poszło, ale dane nie doszły do ERP.”
- „Agent miał zrobić ticket, a wysłał głupiego maila do klienta.”
- „Ten skrypt pisał ktoś, kto już tu nie pracuje.”
- „Nie mam jednego miejsca na crony, webhooki, pipeline’y, agentów i status.”

**Na landingu i w pitchu — te zdania. URI dopiero jako „jak my to robimy”.**

### 3.2 Kompas obietnicy

**Biznes:**

> Taskinity to prosty command center dla automatyzacji i agentów. W jednym chacie widzisz, co działa, co padło, dlaczego i co z tym zrobić.

**CTO:**

> Pod spodem każdy proces jest URI. To samo URI uruchomisz z chatu, API, CLI, workflow, shella czy Dockera — Taskinity pokaże health, logi, incident i ticket.

**Efekt, za który płaci:**

```text
wiem, co padło → dlaczego → mam ticket → propozycja naprawy → nie tracę 3h w logach
```

---

## 4. Polska: rynek, ICP, przewaga lokalna

### 4.1 Dlaczego PL na start

| Sygnał | Źródło |
|--------|--------|
| Gospodarka cyfrowa ~44 mld USD, popyt na automatyzację | [Trade.gov PL digital economy](https://www.trade.gov/country-commercial-guides/poland-digital-economy) |
| **90% firm IT to MŚP** (software house / integratorzy) | Trade.gov |
| Wymóg wsparcia PL i języka polskiego | Trade.gov |
| Setki software dev companies | [PAIH / trade.gov.pl](https://www.trade.gov.pl/en/news/the-information-communication-technology-sector-a-paih-report/) |
| Struktura branży IT, budżety MŚP | [PARP — sektor IT](https://www.parp.gov.pl/storage/publications/pdf/FINAL_IT-czesc-I_04_11_WCAG_25112025.pdf) |
| E-commerce rośnie, złożoność integracji | [Trade.gov e-commerce PL](https://www.trade.gov/country-commercial-guides/poland-ecommerce) |

**Model wygranej:** produkt + usługa + język polski + lokalna obecność.

### 4.2 ICP (priorytety)

Szczegóły: [MARKET_HYPOTHESIS.md](./MARKET_HYPOTHESIS.md).

| # | Segment | Pilot | Buyer |
|---|---------|-------|-------|
| 1 | Software house 10–80 os. | 8–15k zł | właściciel, CTO, Head of Delivery |
| 2 | Integrator n8n/Make/PA/RPA | 5–12k zł → 1,5–4k/mies. | właściciel firmy automatyzacyjnej |
| 3 | E-commerce 20–200 os. | 10–20k zł | COO, Head of E-commerce, IT Manager |
| 4 | BPO / księgowość | 7–15k zł | właściciel, dyrektor operacyjny |
| 5 | Produkcja / logistyka MŚP | 10–25k zł | dyrektor operacyjny, IT |

### 4.3 Komu NIE na początku

Administracja publiczna, banki, duże enterprise — AI Act, GRC, SIEM = długi cykl. [EU AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) · [gov.pl — transformacja cyfrowa MŚP](https://www.gov.pl/web/funds-regional-policy/new-digital-and-environmentally-friendly-transformation-fund-to-support-smes)

Mikrofirmy bez automatyzacji — brak bólu.

---

## 5. Kanał: integratorzy jako multiplikatorzy

**Kanał #1:** software house’y i integratorzy automatyzacji.

- widzą chaos u wielu klientów,
- mają zaufanie,
- sprzedają Taskinity jako „wdrożenie + utrzymanie”.

**Oferta integratora:**

- **Pilot:** 3 procesy (webhook/API, GitHub Action, cron) → health, błędy, incident, ticket w chacie.
- **Docelowo:** 1 500–4 000 zł/mies. za monitoring wielu procesów/klientów.

To **tooling dla integratorów** — „command center” w każdym projekcie.

---

## 6. Produkt: jeden ostry use case

### 6.1 Vertical slice MVP

> **Agent/Automation Health + Incident + Ticket + Repair**

```text
1. Rejestr procesów jako URI
2. Health + ostatnie wykonania + status
3. Błąd → incident (incident://...)
4. Incident → ticket (ticket://...)
5. Repair proposal (expired token, connection refused, timeout)
6. Chat PL, język biznesowy: „co się stało z procesem X?”
7. POST /api/uri/call + POST /api/ask (NL → plan URI)
```

**Później:** n8n://, github://actions, ssh://, mcp://, a2a://, jira://, slack://.

Implementacja: [PRODUCT_READINESS.md](./PRODUCT_READINESS.md).

### 6.2 Integracje MVP (3)

```text
http://     — webhooki, REST, n8n/Make
shell://    — skrypty, cron
docker://   — kontenery, health K8s/Docker
```

Typowy proces: pobierz → przetwórz → wyślij do API/ERP.

---

## 7. Demo: URI to nie tylko nazwa

### 7.1 Proof 30 s (tech)

```bash
urish proof view://process/agent/weather-map-agent.local/latest
```

```text
Chat layer           OK
Web API              OK
CLI                  OK
Runtime              OK
Transport: shell     OK
Transport: http      OK
Docker health        OK
Incident handling    OK
Ticket creation      OK
Repair proposal      OK
```

Status: roadmap — [PRODUCT_READINESS.md](./PRODUCT_READINESS.md).

### 7.2 Demo sprzedażowe + proof

- **Biznes:** historia faktur (10 min) — [DEMO_10MIN.md](./DEMO_10MIN.md)
- **Tech bonus:** `urish proof` na końcu

---

## 8. Landing i komunikacja

Copy: [LANDING_COPY.md](./LANDING_COPY.md).

**Hero:** „Automatyzacje i agenci AI przestali działać?…”  
**Tech niżej:** „Pod spodem każdy proces jest URI…”

---

## 9. Oferty i pricing

Ścieżka: audyt → pilot → utrzymanie. [OFFERS.md](./OFFERS.md).

| Pakiet | Cena | Czas |
|--------|------|------|
| Audyt automatyzacji | 2 500–5 000 zł | 1–3 dni |
| Pilot 3 procesów | 8 000–15 000 zł | 7–14 dni |
| Utrzymanie | 1 500–4 000 zł/mies. | ciągłe |

---

## 10. Następne 30 dni: discovery > funkcje

| Tydzień | Cel |
|---------|-----|
| 1 | Landing + demo wideo + 100 firm |
| 2 | 30 outreach, 10 rozmów |
| 3 | 3 audyty |
| 4 | 2 piloty + 1 partner wdrożeniowy |

**Pytanie walidacyjne w każdej rozmowie:**

> „Czy zapłacilibyście X za jedno miejsce, które mówi: który proces padł, dlaczego i co dalej?”

**Notuj:** słowa, na które reagują (health, incident, n8n, cron, chaos) oraz **3 procesy** kandydatów do pilota.

Plan: [GTM_POLAND.md](./GTM_POLAND.md).

---

## Najważniejszy wniosek

**Nie sprzedawaj platformy agentowej. Sprzedawaj kontrolę nad chaosem automatyzacji.**

| Warstwa | Treść |
|---------|--------|
| Techniczna przewaga | jedno URI → chat / API / CLI / runtime / repair / ticket |
| Klient kupuje | wiem co padło, dlaczego, mam ticket, nie tracę 3h w logach |
| Start PL | software house + integratorzy |
| Produkt startowy | health + incident + ticket + repair dla 3 procesów |

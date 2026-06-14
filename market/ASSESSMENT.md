# Ocena strategiczna: kierunek dobry, research do zaostrzenia

> **Aktualna strategia operacyjna:** [STRATEGY.md](./STRATEGY.md) (10 sekcji, kanoniczna).  
> Ten dokument = pierwotna krytyka researchu; szczegóły sprzedaży → [SALES_MESSAGES.md](./SALES_MESSAGES.md), [DEMO_10MIN.md](./DEMO_10MIN.md).

Pierwotny research trafnie zauważa, że obecne „AI agent control plane” są zwykle **enterprise/governance-first**, a nie URI/developer/runtime-first. Po własnym sprawdzeniu rynku — poniższe korekty.

---

## Korekta #1: „Agent control plane” jest zatłoczone

Sama fraza **„agent control plane”** robi się już zatłoczona. Astrix, Fiddler, Contro1, Speakeasy, Singulr, IBM i inni używają jej jako kategorii związanej z **governance, identity, policy, approvals, audit i bezpieczeństwem** agentów.

| Gracz | Co komunikuje |
|-------|---------------|
| [Astrix](https://astrix.security/product/deploy-and-provisions-ai-agent-discovery/) | Krótkotrwałe, politykami sterowane creds dla agentów |
| [Fiddler](https://www.fiddler.ai/) | AI Control Plane — telemetria, ewaluacje, monitoring, polityki, audytowalny governance |
| [Contro1](https://contro1.com/) | Approvals, escalation, signed callbacks, audit evidence |
| [Speakeasy](https://www.speakeasy.com/resources/ai-control-plane) | Connection, identity, policy, observability dla agentów |
| IBM | Deploy, operate, monitor, manage agentów w organizacji |

**Nie sprzedawać klientom jako „URI-first Agent Control Plane” na pierwszym ekranie.**

Technicznie tak, ale sprzedażowo lepiej:

> **Taskinity — prosty command center dla automatyzacji i agentów. Pokazuje, co działa, co padło, dlaczego padło i jak to naprawić.**

URI = **sekret architektoniczny i przewaga demo**, nie główne hasło dla pierwszego klienta.

---

## Największe luki w pierwotnym researchu

### 1. Brakuje brutalnej analizy: za co klient realnie zapłaci

Research dobrze opisuje architekturę, za mało odpowiada: **jaki ból ma klient o 9:00 w poniedziałek?**

Klient nie powie: „Potrzebuję URI-first control plane”. Powie:

> „Nie wiem, dlaczego automatyzacja faktur znowu nie działa.”  
> „n8n się wykonał, ale dane nie trafiły do systemu.”  
> „Agent miał zrobić ticket, ale wysłał zły mail.”  
> „Nie wiem, kto odpowiada za ten skrypt.”  
> „Nie mam jednego widoku automatyzacji, cronów, webhooków, API i agentów.”

**To jest język sprzedaży.** Zobacz [PAIN_LANGUAGE.md](./PAIN_LANGUAGE.md).

### 2. Zbyt słabo rozpoznana konkurencja: LangSmith Engine

Teza „konkurencja nie ma pełnego repair/ticket/evolution loop” — **częściowo nadal prawda**, ale trzeba ją osłabić.

**[LangSmith Engine](https://docs.langchain.com/langsmith/engine-overview)** jest bardzo blisko idei repair loop:

- pracuje na production traces,
- wykrywa powtarzalne błędy,
- diagnozuje root cause,
- proponuje fix,
- tworzy evaluator,
- może otworzyć pull request z poprawką.

**Lepsza przewaga:**

> **My nie naprawiamy tylko agentów LangGraph/LangChain. Spinamy dowolne procesy: skrypty, cron, API, Docker, SSH, n8n, Make, shell, workflow, agenty i tickety — jednym modelem URI.**

### 3. Za mało „Polski” w polskim planie sprzedaży

Brakowało konkretów: wielkość firmy, kto kupuje, jaki problem, jaki budżet, jak dotrzeć.

| Źródło | Sygnał |
|--------|--------|
| [Trade.gov — Poland Digital Economy](https://www.trade.gov/country-commercial-guides/poland-digital-economy) | Gospodarka cyfrowa ~44 mld USD; popyt na automatyzację, cloud, cyber; **90% firm IT to małe podmioty**; klienci wymagają **lokalnego wsparcia PL** |
| [PAIH / trade.gov.pl — ICT sector](https://www.trade.gov.pl/en/news/the-information-communication-technology-sector-a-paih-report/) | **1300+ software development companies** w Polsce |

**Taskinity może wygrać nie technologią globalną, tylko lokalnym wdrożeniem, językiem polskim, prostotą i pomocą usługową.**

### 4. Brakuje strategii wejścia przez integratorów

Najlepszy pierwszy kanał to niekoniecznie końcowi klienci, tylko firmy wdrażające automatyzacje:

- software house’y,
- integratorzy n8n / Make / Power Automate,
- firmy RPA,
- małe DevOps / IT support.

Oni mają klientów, widzą chaos automatyzacji i mogą używać Taskinity jako **narzędzia do obsługi, monitoringu i utrzymania wdrożeń**.

### 5. Brakuje dowodu, że URI nie jest tylko nazwą

Produkt musi to pokazać w **30 sekund**. Demo powinno mieć jeden przycisk:

```bash
urish proof view://process/agent/weather-map-agent.local/latest
```

Oczekiwany wynik:

```text
Chat layer        OK
Web API           OK
CLI               OK
Runtime           OK
Transport shell   OK
Transport http    OK
Docker check      OK
Incident          OK
Ticket            OK
Repair proposal   OK
```

Dopiero wtedy teza jest udowodniona. Zobacz [DEMO_SCRIPT.md](./DEMO_SCRIPT.md).

---

## Research rynku: gdzie faktycznie jest miejsce

### Enterprise control plane — zajęte

Rynek enterprise idzie w governance, identity, approvals, audyt. **Nie atakować najpierw enterprise governance** — długa sprzedaż, compliance, procurement.

### Standardy agentowe — potwierdzają URI, nie robią produktu

| Standard | Rola | Źródło |
|----------|------|--------|
| `agent://` draft-03 | Addressing/discovery | [IETF](https://www.ietf.org/archive/id/draft-narvaneni-agent-uri-03.html) |
| Google A2A | Agent–agent, uzupełnia MCP | [Google Developers Blog](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) |
| MCP | Narzędzia dla modeli, bez UX użytkownika | [MCP Tools spec](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) |

**Taskinity = warstwa nad MCP/A2A/agent://**, nie konkurencja.

Hasło techniczne:

> Taskinity = URI execution and repair layer over agents, workflows and tools.

### Observability — silne, pasywne

[Langfuse](https://langfuse.com/docs) i Phoenix — tracing, evals, API-first. **Nie budować własnego Langfuse od zera.**

> Taskinity zbiera status, health, logi i zdarzenia z procesów; do głębokiego tracingu LLM integruje Langfuse/Phoenix/LangSmith.

### Workflow automation — konkurencja i kanał sprzedaży

[n8n](https://docs.n8n.io/), Zapier Agents, Copilot Studio, UiPath — ogromny rynek workflow.

**Nie mówić:** „Zastępujemy n8n/Make/Zapier.”  
**Mówić:** „Masz już automatyzacje. My pokazujemy, które działają, które padły, gdzie jest błąd i jak to naprawić.”

---

## Najlepsze pozycjonowanie (zaostrzone)

### Nie (pierwszy ekran)

> Taskinity to URI-first agent control plane.

### Tak (pierwszy ekran)

> **Taskinity to prosty command center dla automatyzacji, skryptów i agentów AI. Daje jeden widok: co działa, co padło, dlaczego i co zrobić dalej.**

### Dla technicznego odbiorcy (drugi ekran / demo)

> **Pod spodem każdy proces jest URI. To samo URI można uruchomić z chatu, API, CLI, workflow, shella, Dockera, HTTP, SSH albo agenta.**

### Dla właściciela firmy

> **Zamiast szukać po logach, webhookach i Excelach, pytasz w chacie: „co się stało z procesem faktur?” — i dostajesz status, przyczynę, logi, ticket i propozycję naprawy.**

Pełna wersja: [POSITIONING.md](./POSITIONING.md).

---

## Komu sprzedawać najpierw

Szczegóły ICP, ceny, oferty: [MARKET_HYPOTHESIS.md](./MARKET_HYPOTHESIS.md), [OFFERS.md](./OFFERS.md).

| Priorytet | Segment | Pilot (netto) |
|-----------|---------|---------------|
| **1** | Software house 10–80 os. | 8 000–15 000 zł |
| **2** | Integratorzy n8n/Make/Power Automate | 5 000–12 000 zł → abonament 1 500–4 000 zł/mies. |
| **3** | E-commerce 20–200 os. | 10 000–20 000 zł |
| **4** | Biura rachunkowe / BPO dokumentowe | 7 000–15 000 zł |
| **5** | Produkcja / logistyka MŚP | 10 000–25 000 zł |

**Najlepszy pierwszy klient:** software house **albo** integrator automatyzacji (kanał sprzedaży).

### Komu nie sprzedawać na początku

- administracja publiczna, banki, duże enterprise, sektory mocno regulowane ([EU AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) — governance rośnie, ale długi procurement),
- mikrofirmy bez automatyzacji (brak bólu „control plane”).

---

## Co zrobić teraz

### Krok 1: Zawęzić produkt do jednego problemu

Nie „pełny ekosystem agentów”. Zbuduj:

> **Agent/Automation Health + Repair Dashboard**

Minimalny zakres MVP — [PRODUCT_READINESS.md](./PRODUCT_READINESS.md).

### Krok 2: 3 integracje na MVP, nie 15

**Teraz:**

```text
http:// / webhook / REST API
shell:// / local script / cron
docker:// / container health
```

**Potem:** n8n, GitHub Actions, ssh, mcp, a2a, jira, slack/teams.

### Krok 3: Demo sprzedażowe, nie tylko techniczne

Historia: automatyzacja faktur → 14 faktur nie przetworzonych → chat „dlaczego?” → API ERP 401 → incident → ticket → repair.  
Zobacz [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) — sekcja „Demo sprzedażowe”.

### Krok 4: Landing page

Copy: [LANDING_COPY.md](./LANDING_COPY.md).

### Krok 5: 30 dni discovery, nie dopisywanie funkcji

| Tydzień | Cel | Konkret |
|---------|-----|---------|
| 1 | Demo + lista leadów | 1 landing, 1 demo wideo, 100 firm |
| 2 | Rozmowy | 30 wiadomości do software house’ów, 10 rozmów |
| 3 | Pilotaże | 3 darmowe/niskopłatne audyty |
| 4 | Sprzedaż | 2 płatne piloty, 1 partner wdrożeniowy |

Pytania discovery — [GTM_POLAND.md](./GTM_POLAND.md).

---

## Najważniejszy wniosek

**Nie sprzedawaj platformy agentowej. Sprzedawaj kontrolę nad chaosem automatyzacji.**

Techniczna przewaga (URI):

```text
jedno URI → chat / API / CLI / workflow / runtime / repair / ticket
```

Klient kupi efekt:

```text
wiem, co padło,
wiem, dlaczego,
mam ticket,
mam propozycję naprawy,
nie tracę 3 godzin na szukanie po logach.
```

**Najlepszy start:** software house’y i integratorzy automatyzacji w Polsce.  
**Najlepszy produkt startowy:** health + incident + ticket + repair dla **3 realnych procesów**.

---

## Referencje

1. [Astrix — Agent Control Plane](https://astrix.security/product/deploy-and-provisions-ai-agent-discovery/)
2. [LangSmith Engine](https://docs.langchain.com/langsmith/engine-overview)
3. [Trade.gov — Poland Digital Economy](https://www.trade.gov/country-commercial-guides/poland-digital-economy)
4. [Speakeasy — AI control plane](https://www.speakeasy.com/resources/ai-control-plane)
5. [IETF draft-narvaneni-agent-uri-03](https://www.ietf.org/archive/id/draft-narvaneni-agent-uri-03.html)
6. [Google A2A announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
7. [MCP Tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
8. [Langfuse docs](https://langfuse.com/docs)
9. [n8n docs](https://docs.n8n.io/)
10. [PAIH ICT sector report (trade.gov.pl)](https://www.trade.gov.pl/en/news/the-information-communication-technology-sector-a-paih-report/)
11. [Mordor Intelligence — Poland e-commerce 2026](https://www.mordorintelligence.com/industry-reports/poland-ecommerce-market)
12. [SAIO — MŚP wdrażają AI](https://www.saio.com/newsroom/news/nie-tylko-korporacje-polskie-msp-coraz-chetniej-wdrazaja-ai)
13. [EU AI Act — digital strategy](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

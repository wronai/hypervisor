# Język bólu klienta — sprzedaż Taskinity

Klient **nie kupuje** „URI-first control plane”. Kupuje rozwiązanie konkretnego bólu o 9:00 w poniedziałek.

## Cytaty klienta (używaj w rozmowach i na landingu)

| Sytuacja | Co mówi klient |
|----------|----------------|
| Automatyzacja dokumentów | „Automatyzacja faktur znowu nie działa — nie wiem, gdzie tego szukać.” |
| n8n / workflow | „Scenario w n8n poszedł, ale dane nie doszły do ERP.” |
| Agenty AI | „Agent miał zrobić ticket, a wysłał zły mail do klienta.” |
| Skrypty / cron | „Ten skrypt pisał ktoś, kto już tu nie pracuje — nie wiemy, czy w ogóle działa.” |
| Chaos integracji | „Nie mam jednego miejsca na crony, webhooki, pipeline’y, agentów i status.” |
| E-commerce | „Zamówienia z Allegro nie weszły do ERP — gdzie to się urwało?” |
| Integrator | „Klient pisze ‘nie działa’, a my ręcznie sprawdzamy scenariusze, logi i API.” |
| Software house | „Mamy 12 projektów klientów — każdy ma inne webhooki i nikt nie widzi awarii centralnie.” |

## Mapowanie ból → funkcja Taskinity

| Ból | Odpowiedź Taskinity (język klienta) | Warstwa techniczna (nie na pierwszym slajdzie) |
|-----|-------------------------------------|------------------------------------------------|
| „Nie wiem co padło” | Jeden dashboard + chat: status procesu | `health://`, `view://process/...` |
| „Nie wiem dlaczego” | Przyczyna, ostatni błąd, logi | `log://`, `incident://` |
| „Kto ma naprawić?” | Ticket z incidentu | `ticket://bug/from-incident/...` |
| „Ile to kosztuje czasu?” | Raport pilota: czas diagnozy przed/po | artifact + metryki |
| „Czy mogę to naprawić bezpiecznie?” | Podgląd naprawy, potem zatwierdzenie | dry-run → `--approve` |
| „Mamy n8n i skrypty” | Nie zastępujemy — spinamy widok | URI nad http/shell/docker |

## Pytania discovery (30 rozmów)

W każdej rozmowie — **pytanie walidacyjne:**

> „Czy zapłacilibyście X zł za jedno miejsce, które mówi: który proces padł, dlaczego i co dalej?”

Plus:

```text
Jakie automatyzacje macie dziś w firmie?
Co najczęściej się psuje?
Gdzie szukacie logów?
Ile trwa ustalenie przyczyny?
Kto odpowiada za naprawę?
Czy klient widzi status procesu?
Czy płacilibyście za prosty dashboard health + ticket + repair?
Jakie 3 procesy warto byłoby podłączyć jako pierwsze?
```

## Efekt, za który klient płaci (nie architektura)

```text
wiem, co padło,
wiem, dlaczego,
mam ticket,
mam propozycję naprawy,
nie tracę 3 godzin na szukanie po logach.
```

## Antywzorce w pitchu

| Nie mów | Mów zamiast |
|---------|-------------|
| „URI-first control plane” | „Command center dla automatyzacji” |
| „Agentic ecosystem” | „Widok 3 procesów + chat” |
| „Zastępujemy n8n” | „Pokazujemy co z n8n i skryptów działa, a co padło” |
| „Konkurujemy z LangSmith” | „Spinamy skrypty, API, Docker i agentów — nie tylko LangChain” |

Powiązane: [ASSESSMENT.md](./ASSESSMENT.md), [POSITIONING.md](./POSITIONING.md), [OFFERS.md](./OFFERS.md).

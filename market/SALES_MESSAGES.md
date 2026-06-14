# Wiadomości sprzedażowe

Gotowce outreach + discovery. Narracja: **command center**, nie control plane.

Powiązane: [OFFERS.md](./OFFERS.md), [PAIN_LANGUAGE.md](./PAIN_LANGUAGE.md), [STRATEGY.md](./STRATEGY.md).

---

## Pytanie walidacyjne (każda rozmowa)

> „Czy zapłacilibyście **X zł** za jedno miejsce, które mówi: **który proces padł, dlaczego i co zrobić dalej**?”

Warianty X: 2 500 (audyt), 8 000, 10 000, 15 000 (pilot).

Notuj reakcję i słowa kluczowe: health, incident, ticket, n8n, cron, chaos, faktury, zamówienia.

---

## 1. Software house (10–80 osób)

### LinkedIn / email — wersja A (krótka)

```text
Cześć [Imię],

buduję Taskinity — prosty command center dla automatyzacji i skryptów.

Nie zastępuje n8n ani GitHub Actions. Jeden widok: co działa, co padło,
gdzie logi, incident i co można naprawić.

Szukam 5 polskich software house’ów do pilota (7–14 dni, 3 procesy).
10 min demo: webhook → błąd API → incident → ticket.

Masz 15 min w tym tygodniu?
```

### Wersja B (ból 9:00)

```text
Cześć [Imię],

ile trwa u Was ustalenie, dlaczego automatyzacja klienta „nagle nie działa”?
Logi w CI, webhook, n8n, skrypt na serwerze — i każdy patrzy gdzie indziej?

Taskinity daje jeden chat + dashboard: status procesu, przyczyna, ticket, propozycja naprawy.
Pilot: 3 realne procesy (np. GitHub Action + webhook + cron), 8–15k zł, 7–14 dni.

Chcesz zobaczyć 10-min demo na przykładzie faktur → API 401 → naprawa?
```

### Follow-up po demo

```text
Dzięki za czas. Jak ustaliliśmy — pilot to 3 procesy, chat + health + incident + ticket.
Kolejny krok: wskażecie 3 kandydatów (webhook/API, cron, docker/n8n)?
Mogę przygotować ofertę na [kwota] z harmonogramem 7–14 dni.
```

---

## 2. Integrator n8n / Make / Power Automate

### Wersja A — warstwa SLA

```text
Cześć [Imię],

wdrażacie n8n/Make u klientów — a potem „nie działa” i ręczne grzebanie w scenariuszach?

Taskinity to panel serwisowy nad wdrożeniami: status procesów, ostatnie błędy,
incident, ticket, rekomendacja naprawy. Możecie sprzedać to klientom jako utrzymanie/SLA.

Pilot integratora: 5–12k zł, 7–14 dni, potem abonament 1,5–4k/mies.

10 min demo — pokażę webhook + błąd ERP na żywo.
```

### Wersja B — partnerstwo

```text
Szukam 2 integratorów automatyzacji w PL jako partnerów wdrożeniowych.

Taskinity = „command center” w każdym projekcie klienta — health + chat + ticket.
Wy: wdrożenia. My: narzędzie + wsparcie. Wy: marża na utrzymaniu.

Zainteresowany 20-min rozmową o modelu partnerskim?
```

### Po pilocie — upsell abonament

```text
Po pilocie proponuję utrzymanie 1 500–4 000 zł/mies.:
monitoring procesów klientów, raport awarii, priorytety napraw, nowe URI w miarę potrzeb.
```

---

## 3. E-commerce (20–200 osób)

### Wersja A

```text
Cześć [Imię],

zamówienia z marketplace, ERP, magazyn, faktury — gdy coś się urwie w połowie,
trudno szybko powiedzieć „gdzie”.

Taskinity: jeden chat — „co się stało z procesem zamówień?” → status, przyczyna, logi, ticket.

14-dniowy pilot, 3 procesy (np. zamówienia, faktury, zwroty), 10–20k zł.
Warto 10 min na demo na jednym waszym procesie?
```

### Wersja B (COO / właściciel)

```text
Automatyzacje i integracje e-commerce przestają działać w najgorszym momencie.
Taskinity pokazuje w prostym języku: który krok padł i co zrobić — bez wchodzenia w logi serwera.

Szukam 2 firm e-commerce w PL do pilota. 10 min online — pokażę scenariusz faktur/ERP.
```

---

## 4. BPO / biuro rachunkowe (opcjonalny 4. segment)

```text
Cześć [Imię],

maile, faktury, OCR, KSeF — gdy proces dokumentu się zacina, trudno szybko wskazać krok.

Taskinity: widok procesu od maila do systemu księgowego + dashboard błędów + ticket
dla dokumentów, których automat nie obsłużył.

Pilot 7–15k zł, mapa procesu faktur + chat. 10 min demo?
```

---

## Obiekcje — szybkie odpowiedzi

| Obiekcja | Odpowiedź |
|----------|-----------|
| „Mamy LangSmith / Langfuse” | „Świetnie do trace LLM. My spinamy też cron, webhooki, n8n — jeden widok awarii.” |
| „To duplikat n8n” | „n8n buduje flow. My pokazujemy co padło i co dalej — gdy flow już macie.” |
| „Za drogo” | „Audyt od 2,5k — zobaczycie ROI zanim pilot. Ile kosztuje Was 1h diagnozy × miesiąc?” |
| „Nie mamy agentów AI” | „Skrypty i webhooki też — to często pierwsze, co pada.” |
| „SOC2?” | „Produkt MŚP, self-host. Enterprise governance to inna liga — nie udajemy.” |

---

## Notatnik discovery (szablon)

Po każdej rozmowie:

```text
Firma / segment:
Automatyzacje dziś:
Co najczęściej pada:
Czas diagnozy (szacunek):
Kto naprawia:
3 procesy kandydaci do pilota:
Reakcja na pytanie walidacyjne (tak/nie/może + kwota):
Słowa, które rezonowały:
Następny krok:
```

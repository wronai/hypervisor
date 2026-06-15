# Example 31 — dzień biurowy Marty

Pilot automatyzacji biurowej: portal WWW → raport CSV → faktury w ERP →
przygotowanie banku → STOP przed 2FA → podgląd telefonu Android.

Przykład jest mock-first. Można go uruchomić lokalnie bez prawdziwego portalu,
banku, Windowsa i telefonu. W produkcji te same URI można przepiąć z adaptera
`mock` na `playwright`, `uia` albo `adb`.

## Persona

Marta pracuje w administracji. Codziennie musi:

1. wejść do portalu dostawcy,
2. pobrać raport CSV,
3. porównać go z fakturami,
4. otworzyć system ERP w oknie Windows,
5. przygotować fakturę i zatrzymać się na podglądzie,
6. wejść do banku, przygotować przelew,
7. potwierdzić token na telefonie z Androidem,
8. zapisać raport audytowy z wykonanych kroków.

## Uruchomienie

```bash
bash examples/31_office_day/run.sh
```

Mock (bez urządzeń):

```bash
uri3 validate-workflow examples/31_office_day/task_graph.yaml
uri3 run-workflow examples/31_office_day/task_graph.yaml --dry-run
uri3 run-workflow examples/31_office_day/task_graph.yaml --approve --browser mock
```

Taski operatora:

```bash
python -m uri2ops.cli run examples/31_office_day/portal_report.browser.yaml --adapter mock --approve
python -m uri2ops.cli run examples/31_office_day/invoice_review.pcwin.yaml --adapter mock --approve
python -m uri2ops.cli run examples/31_office_day/bank_token.android.yaml --adapter mock --approve
```

## Chat NL (urish ask)

Polecenia biurowe z landing page mapują się na intent `office`:

```bash
uri ask "$(cat examples/31_office_day/prompt.txt)"
uri ask "wystaw faktury za wczoraj i pokaż podgląd przed wysyłką"
uri ask "pobierz raport CSV z portalu dostawcy"
uri ask "przygotuj przelewy i zatrzymaj się przed autoryzacją w banku"
uri ask "co się stało z procesem faktur?"
```

Planowane URI: `workflow://invoices/batch/dry-run`, `workflow://bank/batch-transfer/dry-run`, itd.

## Human-in-the-loop

Krok banku **zatrzymuje się przed autoryzacją** — Marta akceptuje token na telefonie
(`android://` screenshot/tap). Bez omijania 2FA.

## Pliki

- [`prompt.txt`](./prompt.txt) — polecenie użytkownika.
- [`task_graph.yaml`](./task_graph.yaml) — graf `uri3` dla pełnego dnia.
- [`portal_report.browser.yaml`](./portal_report.browser.yaml) — portal dostawcy i raport CSV.
- [`invoice_review.pcwin.yaml`](./invoice_review.pcwin.yaml) — faktura w systemie ERP / Windows UI.
- [`bank_token.android.yaml`](./bank_token.android.yaml) — token lub push approval na Androidzie.

## Wariant produkcyjny

```bash
# Portal / bank przez realną przeglądarkę:
python -m uri2ops.cli run examples/31_office_day/portal_report.browser.yaml \
  --adapter playwright --approve

# Windows ERP przez UI Automation:
python -m uri2ops.cli run examples/31_office_day/invoice_review.pcwin.yaml \
  --adapter uia --approve

# Telefon przez ADB:
python -m uri2ops.cli run examples/31_office_day/bank_token.android.yaml \
  --adapter adb --approve
```

W realnym banku krok wysyłki powinien być rozdzielony na: przygotowanie
przelewu, podgląd, jawny human approval i dopiero potem autoryzację.

## Powiązane

- WWW: [`www/index.html#przyklady-biuro`](../../www/index.html#przyklady-biuro)
- Docs: `www/docs/examples.html#ex-31_office_day`
- [`07_invoices_agent`](../07_invoices_agent/) — agent faktur

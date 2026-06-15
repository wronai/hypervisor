# Office domain — markpact scenarios

Canonical YAML registry: [`scenario_registry.yaml`](./scenario_registry.yaml)

Import individual landing-card scenarios into another system:

```bash
python - <<'PY'
from pathlib import Path
import yaml
from uri2pact.scenarios import load_markpact_scenario_dicts

ref = "markpact://domains/office/README.md"
for scenario in load_markpact_scenario_dicts(ref):
    print(scenario["id"], scenario.get("chat_prompt", "")[:50])
PY
```

Registry block (includes YAML by reference):

```markpact:scenario_registry office-automation
include: domains/office/scenario_registry.yaml
kind: urish.scenario_registry
metadata:
  id: office-automation
  markpact_readme: domains/office/README.md
```

## Landing cards (exportable scenarios)

```markpact:scenario website_report
scenario:
  id: website_report
  subtype: portal_report
  chat_prompt: Wejdź na stronę dostawcy, pobierz raport CSV za ten miesiąc i zapisz w rozliczeniach.
  needles:
    - "stron[aęe]\\s+dostawc"
    - "raport\\s+csv"
  planned_uris:
    - browser://chrome/page/open
    - workflow://office/supplier-report/monthly
  next_steps:
    - uri run workflow://office/supplier-report/monthly --dry-run
  human_in_the_loop: false
```

```markpact:scenario portal_zus_form
scenario:
  id: portal_zus_form
  subtype: portal_form
  chat_prompt: Zaloguj się do portalu klienta, uzupełnij formularz ZUS i wyślij — najpierw pokaż podgląd.
  planned_uris:
    - workflow://portal/zus-form/dry-run
    - workflow://portal/zus-form
  human_in_the_loop: true
```

```markpact:scenario erp_subiekt
scenario:
  id: erp_subiekt
  subtype: erp_pcwin
  chat_prompt: Otwórz Subiekta, wklej dane z Excela do faktury i zapisz jako szkic.
  planned_uris:
    - pcwin://window/Subiekt GT/focus
    - pcwin://control/NumerFaktury/set_text
  human_in_the_loop: false
```

```markpact:scenario invoice_batch_woo
scenario:
  id: invoice_batch_woo
  subtype: invoice_batch
  deployment_id: invoices-agent.local
  chat_prompt: Wystaw faktury za zamówienia z WooCommerce, pokaż listę do akceptacji i wyślij tylko zatwierdzone.
  planned_uris:
    - workflow://invoices/batch/dry-run
    - view://process/agent/invoices-agent.local/latest
  human_in_the_loop: true
```

```markpact:scenario bank_batch
scenario:
  id: bank_batch
  subtype: bank_transfer
  chat_prompt: Przygotuj przelewy do dostawców z listy — zatrzymaj się przed autoryzacją.
  planned_uris:
    - workflow://bank/batch-transfer/dry-run
  human_in_the_loop: true
```

```markpact:scenario android_2fa
scenario:
  id: android_2fa
  subtype: android_2fa
  chat_prompt: Bank czeka na potwierdzenie w aplikacji — pokaż mi ekran telefonu.
  planned_uris:
    - android://device/pixel-7/screenshot
    - android://device/pixel-7/tap
  human_in_the_loop: true
```

See [`docs/MARKPACT_WITH_TOURI.md`](../docs/MARKPACT_WITH_TOURI.md) · [`docs/DOMAIN_SEPARATION.md`](../docs/DOMAIN_SEPARATION.md).

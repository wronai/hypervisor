# Compatibility i Governance

Warstwa compatibility opisuje, które zmiany są bezpieczne, a które wymagają zatwierdzenia.

## Bezpieczne zmiany

- dodanie nowego zasobu,
- dodanie nowej capability,
- dodanie opcjonalnego pola Protobuf,
- dodanie nowego renderera.

## Zmiany wymagające zatwierdzenia

- usunięcie zasobu,
- usunięcie capability,
- zmiana stabilnego URI,
- usunięcie pola Protobuf,
- breaking change bez bumpu wersji.

## Policy Gate

`hypervisor/policy_gate/gate.py` dostaje raport zmiany i zwraca decyzję:

```txt
allowed: true/false
requires_approval: true/false
reasons: [...]
```

Na tym etapie to lekki moduł, ale jest miejscem na przyszłe reguły produkcyjne.

# Capability Verification

Każda capability zadeklarowana w agencie powinna mieć test.

## Generowanie planu testów

```bash
make capability-tests
```

Plan testów powstaje z Contract Registry.

Dla `resource_read` sprawdzane jest:

- czy URI istnieje,
- czy schema capability zgadza się z zasobem,
- czy renderer capability zgadza się z zasobem.

Dla `command` sprawdzane jest:

- czy komenda ma input schema,
- czy deklaruje emitowane eventy,
- czy capability jest poprawnie opisana.

# Desktop Ops domain

Canonical YAML registry: [`scenario_registry.yaml`](./scenario_registry.yaml)

This domain pack describes generic desktop-operation routing. It does not
execute UI actions directly. Execution stays in `uri2ops`, lifecycle stays in
`hypervisor`, and the generic operator contract stays in
[`agents/operators/desktop_operator.yaml`](../../agents/operators/desktop_operator.yaml).

## Files

| File | Purpose |
|------|---------|
| [`domain.yaml`](./domain.yaml) | Boundary and ownership contract |
| [`operator_registry.yaml`](./operator_registry.yaml) | Browser, screen, input, pcwin and Android cards |
| [`scenario_registry.yaml`](./scenario_registry.yaml) | NL routing to operator URIs |

## Approval boundary

`desktop_ops` is an orchestration domain, not the executor. Mutating desktop
URIs are policy-gated in `urish.policy` and require either dry-run planning or
explicit approval:

| Read URI examples | Mutation URI examples |
|-------------------|-----------------------|
| `screen://desktop/observe` | `browser://chrome/page/open` |
| `browser://chrome/page/active/dom` | `browser://chrome/page/active/click` |
| `browser://chrome/page/active/screenshot` | `input://keyboard/type` |
| `android://device/{id}/screenshot` | `pcwin://window/{id}/focus` |
| `android://device/{id}/dump_ui` | `android://device/{id}/tap` |

The domain may plan these URIs and attach human-in-the-loop metadata. Actual UI
execution remains in `uri2ops`; lifecycle and approval stay in `hypervisor` /
`urish`.

## Load from markpact

```markpact:scenario_registry desktop-ops
include: domains/desktop_ops/scenario_registry.yaml
kind: urish.scenario_registry
metadata:
  id: desktop-ops
  markpact_readme: domains/desktop_ops/README.md
```

## Exportable scenarios

```markpact:scenario desktop_operator_status
scenario:
  id: desktop_operator_status
  subtype: desktop_status
  chat_prompt: Sprawdz desktop operator i pokaz stan runtime.
  planned_uris:
    - health://agent/desktop-operator.local
    - view://process/agent/desktop-operator.local/latest
  human_in_the_loop: false
```

```markpact:scenario browser_operator_capture
scenario:
  id: browser_operator_capture
  subtype: browser_capture
  chat_prompt: Otworz strone testowa w chrome operator i pobierz DOM oraz obraz.
  planned_uris:
    - browser://chrome/page/open
    - browser://chrome/page/active/dom
    - browser://chrome/page/active/screenshot
  human_in_the_loop: true
```

```markpact:scenario pcwin_operator_control
scenario:
  id: pcwin_operator_control
  subtype: pcwin_control
  chat_prompt: Sprawdz pcwin operator na oknie systemowym w trybie mock.
  planned_uris:
    - pcwin://window/{id}/focus
    - pcwin://control/{id}/click
  human_in_the_loop: true
```

```markpact:scenario android_operator_device
scenario:
  id: android_operator_device
  subtype: android_device
  chat_prompt: Sprawdz android device przez adb operator w trybie mock.
  planned_uris:
    - android://device/{id}/screenshot
    - android://device/{id}/dump_ui
  human_in_the_loop: true
```

See [`docs/DESKTOP_AUTONOMY.md`](../../docs/DESKTOP_AUTONOMY.md) and
[`docs/DOMAIN_SEPARATION.md`](../../docs/DOMAIN_SEPARATION.md).

# Konfiguracja `*.uri.yaml`

Pliki kończące się na `.uri.yaml` oznaczają, że **wartości pól mogą być URI** rozwiązywane przez `uri3`.

## Konwencja nazewnictwa

```txt
*.uri.yaml       = wartości pól mogą być URI (env://, llm://, python://, …)
*.schema.json    = walidacja struktury
*.yaml           = zwykły kontrakt bez automatycznego resolvingu URI
```

Nie stosujemy sufiksów `_uri` w nazwach pól w plikach `.uri.yaml`:

```yaml
# config/llm.uri.yaml
$schema: schemas/config/config_base.schema.json
apiVersion: uri3.io/v1
kind: LlmConfig
metadata:
  id: llm
uri:
  self: config://llm
spec:
  profiles:
    default:
      model: llm://openrouter/qwen/qwen3-coder-next?temp=0.1
      api_key: env://OPENROUTER_API_KEY
```

Zamiast:

```yaml
model_uri: llm://...
api_key_uri: env://...
```

## Envelope

Każdy `config/*.uri.yaml` jest artefaktem URI3 i ma:

```yaml
$schema: schemas/config/config_base.schema.json
apiVersion: uri3.io/v1
kind: RuntimeConfig
metadata:
  id: runtime
uri:
  self: config://runtime
spec:
  version: 1
  defaults: {}
```

Kod aplikacji używa `load_uri_yaml()`, które dla kompatybilności zwraca zawartość
`spec`. Raw envelope jest dostępny przez `load_uri_yaml(path, unwrap_spec=False)`.

## Pliki w repo

```txt
config/llm.uri.yaml
config/deployments.uri.yaml
config/runtime.uri.yaml
config/ssh.uri.yaml
config/docker.uri.yaml
config/operator_policy.uri.yaml
config/operator_registry.uri.yaml
config/flow_defaults.uri.yaml
config/touri.uri.yaml
config/uri3.uri.yaml
config/cli_shortcuts.uri.yaml
```

SSH testenv (Docker example 03):

```bash
uri3 call 'env://HYPERVISOR_SSH_PASSWORD?action=set&value=deploy&persist=1'
uri3 scan ssh
make scan-ssh
```

Alternatywnie ręcznie w `.env` lub `export HYPERVISOR_SSH_PASSWORD=deploy`.

## Bezpieczeństwo

OK:

```yaml
api_key: env://OPENROUTER_API_KEY
```

Nie OK:

```yaml
api_key: sk-or-v1-...
```

Docelowo: `secret://vault/openrouter/api-key`.

## API uri3

```python
from uri3.config.uri_yaml import is_uri, load_uri_yaml, resolve_uri_values

data = load_uri_yaml("config/llm.uri.yaml")
resolved = resolve_uri_values(data, resolve_secrets=True)

raw = load_uri_yaml("config/llm.uri.yaml", unwrap_spec=False)
assert raw["kind"] == "LlmConfig"
```

## Integracja z hypervisor

`hypervisor.config.loader` ładuje `config/llm.uri.yaml` i mapuje aktywny profil na sekcję `llm` (zachowana kompatybilność z `model_uri` / `api_key_uri`).

Zmiana profilu:

```bash
export DEFAULT_LLM_PROFILE=domain_planner
```

## Powiązane

- [`docs/HYPERVISOR_WORKFLOW.md`](./HYPERVISOR_WORKFLOW.md)
- [`docs/STANDARDS.md`](./STANDARDS.md)

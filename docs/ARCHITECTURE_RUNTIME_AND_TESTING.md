# Runtime, moduły i testy architektury hypervisora

## 1. Cel dokumentu

Ten dokument opisuje, gdzie w aktualnej architekturze powinien znajdować się neutralny runtime wykonawczy, jak ma się on do istniejących modułów oraz jakie testy warto uruchamiać, aby wykrywać błędy architektury zanim projekt ponownie urośnie w kierunku monolitu.

Aktualny stan projektu pokazuje, że architektura została mocno uporządkowana: istnieją już pakiety `uri2voice`, `uri2pact`, `uri2verify`, rozdzielone loadery `markpact://`, `uri3 doctor`, `uri3 explain`, `ServiceResult`, `ErrorEnvelope`, `workflow statuses`, `touri` jako capability runtime oraz `uri2flow` jako compiler compact flow do graph. Nadal jednak brakuje jednej wyraźnej warstwy neutralnego runtime'u transportowego.

---

## 2. Obecny podział modułów

### `nl2uri`

Rola:

```txt
prompt / tekst / komenda użytkownika
  -> URI
  -> compact URI flow
  -> workflow graph
  -> uri_tree / domain proposal
```

`nl2uri` nie powinno wykonywać operacji. Jego zadaniem jest planowanie i naprawa struktury wyjścia LLM. Obecnie ma rozdzielone pliki dla flow extraction, sanitation, step ids, plannerów i repair, co jest dobrym kierunkiem.

Ryzyko:

```txt
LLM wygeneruje coś, co wygląda poprawnie, ale nie ma wykonawczego kontraktu.
```

Ochrona:

```txt
validate flow
repair flow
expand flow
uri3 explain
uri3 doctor
```

---

### `uri2flow`

Rola:

```txt
compact *.uri.flow.yaml
  -> expanded workflow graph
```

To jest compiler, nie runtime. Nie powinien wykonywać kroków. Powinien rozumieć tylko strukturę flow, zależności, domyślne operacje i ewentualnie `markpact://...#flow` przez `uri2pact`.

Ryzyko:

```txt
flow zostanie rozszerzony do graph, który ma złe domyślne operation/kind.
```

Testy:

```bash
pytest tests/uri2flow -q
uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out /tmp/weather.uri.graph.yaml
uri3 validate-workflow /tmp/weather.uri.graph.yaml
```

---

### `uri3`

Rola:

```txt
URI core
scheme registry
resolver
workflow graph
execution orchestration
event log
replay facade
explain
doctor
```

`uri3` powinien być centrum rozumienia URI i grafów, ale nie powinien mieć zbyt wielu konkretnych runtime adapterów. Jeśli `uri3` wykonuje browser, shell, http, python, docker itd. bezpośrednio, zaczyna przejmować rolę runtime'u i grozi mu rozrost.

Powinno zostać w `uri3`:

```txt
URI parser/resolver
workflow graph models
workflow validator
workflow executor/orchestrator
event emitter
result envelope
explain/doctor
```

Powinno wychodzić poza `uri3`:

```txt
browser Playwright runtime
shell runtime
HTTP call runtime
WS/SSE runtime
MCP/A2A transport
provider-specific execution
```

---

### `touri`

Rola:

```txt
URI -> capability manifest -> backend -> ServiceResult
```

`touri` jest rejestrem i wykonawcą capability. Dobrze, że manifesty definiują nowe URI bez pisania nowej biblioteki dla każdego schematu.

Ale `touri` nie powinno docelowo być niskopoziomowym runtime'em dla wszystkich transportów. Obecnie ma backend dispatch dla Python, shell, `uri_flow`, `uri_graph`, `uri2ops`. To działa, ale w dłuższej perspektywie backend execution powinien zostać wydzielony.

Docelowo:

```txt
touri
  match URI
  validate manifest
  build payload
  apply policy/redaction/fallbacks
  call uri2run
  apply uri2verify data_quality
```

---

### `uri2ops`

Rola:

```txt
operator runtime dla OS/UI/browser/android/pcwin
```

`uri2ops` nie jest ogólnym runtime'em. To runtime operacji użytkownika i środowiska graficznego:

```txt
browser.open
browser.screenshot
browser.click
android.tap
pcwin.window
screen.capture
input.type
```

Powinien być wywoływany przez `touri`, `uri3` lub przyszłe `uri2run`, ale nie powinien stać się głównym runtime'em całego systemu.

---

### `uri2voice`

Rola:

```txt
stt://
tts://
voice://
audio://
```

To jest pakiet wykonawczy dla głosu. Dobrze, że `touri` trzyma manifesty, a `uri2voice` wykonuje handlery. To jest właściwa separacja:

```txt
touri = capability registry
uri2voice = implementation/runtime for voice handlers
```

---

### `uri2pact`

Rola:

```txt
markpact:// loader
capability blocks
flow blocks
README contract import
```

To jest dobry kierunek, bo usuwa duplikaty loaderów z `touri` i `uri2flow`.

Docelowo `uri2pact` może też obsłużyć:

```txt
pactown://workspace/...
README discovery
contract import
publication metadata
```

---

### `uri2verify`

Rola:

```txt
data quality
replay
capability test plan
result checks
technical vs business status
```

To jest warstwa chroniąca przed problemami znanymi z tellm: technicznie `ok`, ale biznesowo źle.

Powinno zostać tutaj:

```txt
ServiceResult enrichment
DataQuality validators
Replay from workflow logs
Capability test plan
Regression test generation
Status separation
```

Nie powinno tu być:

```txt
runtime execution
LLM planning
provider implementation
deployment lifecycle
```

---

### `hypervisor`

Rola:

```txt
policy
registry
lifecycle
deployment
agent status
logs
deploy/verify
approval gate
```

Hypervisor nie powinien być ani plannerem, ani runtime'em transportowym. Powinien decydować:

```txt
czy wolno wykonać?
gdzie uruchomić?
w jakim deployment target?
z jaką polityką?
jak zweryfikować?
```

---

## 3. Brakująca warstwa: `uri2run`

### Problem

Runtime jest obecnie rozproszony:

```txt
touri/backends/python_backend.py
touri/backends/shell_backend.py
touri/backends/uri_flow_backend.py
touri/backends/uri_graph_backend.py
touri/backends/uri2ops_backend.py
uri3/graph/adapters/*
uri2ops/server/*
hypervisor/deployment_registry/*
runtime_client/client.py
```

To działa, ale brakuje jednego kontraktu:

```txt
jak wykonać backend niezależnie od środowiska i transportu?
```

### Proponowany pakiet

```txt
packages/uri2run
```

### Rola

```txt
uri2run = neutralny runtime transportowy
```

Obsługiwane transporty docelowo:

```txt
python
shell
http
websocket
sse
stdio
docker
ssh
mcp
a2a
uri_flow
uri_graph
uri2ops
```

### Docelowa relacja

```txt
nl2uri
  planuje

uri2flow
  kompiluje flow

uri3
  orkiestruje graph

touri
  mapuje URI na capability

uri2run
  wykonuje backend przez transport

uri2verify
  weryfikuje wynik

hypervisor
  kontroluje policy/lifecycle/deployment
```

---

## 4. Proponowana struktura `uri2run`

```txt
packages/uri2run/
  pyproject.toml
  uri2run/
    __init__.py
    models.py
    context.py
    runner.py
    result.py
    cli.py
    transports/
      __init__.py
      python_transport.py
      shell_transport.py
      http_transport.py
      ws_transport.py
      sse_transport.py
      stdio_transport.py
      docker_transport.py
      ssh_transport.py
      mcp_transport.py
      a2a_transport.py
      flow_transport.py
      graph_transport.py
      uri2ops_transport.py
```

Minimalny MVP:

```txt
python_transport
shell_transport
http_transport
flow_transport
graph_transport
uri2ops_transport
```

---

## 5. Jak `uri2run` ma się do obecnych modułów

### `touri -> uri2run`

Obecnie:

```txt
touri backend_dispatch -> python/shell/flow/graph/uri2ops backend
```

Docelowo:

```txt
touri backend_dispatch -> uri2run.run_backend(...)
```

`touri` zostawia:

```txt
manifest
matching
fallbacks
redaction
policy hints
```

`uri2run` przejmuje:

```txt
real execution
transport errors
timeouts
process output
HTTP status mapping
WS/SSE handling
```

---

### `uri3 -> uri2run`

Obecnie `uri3` ma własne graph adapters i częściowo deleguje do `uri2ops`.

Docelowo:

```txt
uri3 step_runner
  -> adapter_for_uri
  -> uri2run for executable transport nodes
```

`uri3` powinien zostać orkiestratorem grafu, a nie runtime'em każdej technologii.

---

### `uri2ops -> uri2run`

`uri2ops` może działać jako:

```txt
local Python dispatcher
HTTP server
MCP wrapper
A2A wrapper
```

`uri2run` może wywołać `uri2ops` przez:

```txt
python transport
http transport
mcp transport
a2a transport
```

---

### `hypervisor -> uri2run`

Hypervisor nie powinien używać `uri2run` do zarządzania całym lifecycle, ale może go używać do pojedynczych kontroli:

```txt
health check
remote command
log probe
verification call
```

Deployment lifecycle nadal zostaje w hypervisorze.

---

## 6. Deficyty widoczne w architekturze

### Deficyt 1: brak jednego neutralnego runtime'u

Objaw:

```txt
kilka paczek ma własne backend/execute/call logic
```

Skutek:

```txt
różne formaty błędów
różne timeouty
różne result envelopes
trudniejszy replay
trudniejszy doctor
```

Rozwiązanie:

```txt
uri2run
```

---

### Deficyt 2: browser runtime nadal częściowo w `uri3`

Objaw:

```txt
uri3/graph/adapters/browser_playwright.py
uri3/graph/adapters/browser_router.py
```

Problem:

```txt
browser to operator layer, powinien być w uri2ops
```

Rozwiązanie:

```txt
oznaczyć jako legacy/deprecated
ustawić domyślnie URI3_USE_LEGACY_BROWSER=0
wymusić delegację przez Uri2OpsAdapter
```

---

### Deficyt 3: brak testów kontraktowych między paczkami

Obecne testy jednostkowe przechodzą, ale warto mieć testy granic między paczkami:

```txt
touri -> uri2run
uri3 -> uri2run
uri3 -> uri2ops
uri2flow -> uri3
touri -> uri2verify
hypervisor -> uri2verify
```

---

### Deficyt 4: brak chaos/failure matrix

Trzeba testować nie tylko sukcesy, ale:

```txt
timeout
bad JSON
HTTP 500
WS disconnect
SSE partial event
shell exit code != 0
missing backend
wrong capability match
low confidence data
stale artifact
old replay log
```

---

### Deficyt 5: generated artifacts i legacy shims

W repo widać stare zerowe shimy i wygenerowane artefakty w kilku miejscach. Trzeba utrzymać zasadę:

```txt
packages/* = biblioteki
agents/generated = output generated agents
examples/* = demonstracje
output/* = artefakty runtime, gitignored
legacy/* = stare shimy
```

---

## 7. Testy wykrywające błędy architektury

### 7.1. Test granic paczek

Cel: wykryć, czy paczki nie zaczynają wykonywać cudzych ról.

Przykłady reguł:

```txt
nl2uri nie importuje hypervisor deployment_registry
uri2flow nie importuje uri3 graph_executor
uri2verify nie importuje LLM plannerów
uri2pact nie importuje hypervisor
uri2voice nie importuje touri executor
uri3 nie importuje Playwright jako domyślnego runtime'u
```

Przykładowy test:

```python
FORBIDDEN_IMPORTS = {
    "packages/nl2uri": ["hypervisor.deployment_registry"],
    "packages/uri2flow": ["uri3.graph.graph_executor"],
    "packages/uri2verify": ["nl2uri.planner_llm", "hypervisor.deployment_registry"],
}
```

---

### 7.2. Test result envelope consistency

Każdy runtime i backend powinien zwracać pola:

```txt
ok
result_type
data
errors
warnings
meta
execution_status
service_result_status
```

Test:

```bash
pytest tests/architecture/test_result_envelope_contract.py -q
```

Przypadki:

```txt
touri call mock
touri call python backend
touri call uri_flow backend
uri3 run-workflow dry-run
uri2ops run mock operation
hypervisor verify-agent dry-run
uri2voice tts mock
```

---

### 7.3. Test technical OK vs business failed

Cel: upewnić się, że system nie powtórzy błędu `workflow / ok`, gdy dane są złe.

Przykład:

```txt
backend zwraca HTTP 200 i ceny, ale data_quality odrzuca wynik
```

Oczekiwane:

```json
{
  "workflow_status": "completed",
  "execution_status": "completed",
  "service_result_status": "failed",
  "data_quality_status": "failed",
  "ok": false
}
```

---

### 7.4. Test replay regression

Cel: każdy problem z runtime'u da się odtworzyć.

Scenariusz:

```bash
uri3 run-workflow examples/14_workflow_executor_mock/task_graph.yaml
uri2verify replay output/events/<workflow>.jsonl
uri2verify replay output/events/<workflow>.jsonl --create-test
pytest tests/regression/generated/test_<workflow>.py -q
```

---

### 7.5. Test transport matrix dla `uri2run`

Po dodaniu `uri2run` trzeba testować każdy transport tym samym kontraktem.

Macierz:

| Transport | Success | Timeout | Bad payload | Error envelope |
|---|---:|---:|---:|---:|
| python | yes | yes | yes | yes |
| shell | yes | yes | yes | yes |
| http | yes | yes | yes | yes |
| ws | yes | yes | yes | yes |
| sse | yes | yes | yes | yes |
| flow | yes | yes | yes | yes |
| graph | yes | yes | yes | yes |
| uri2ops | yes | yes | yes | yes |

---

### 7.6. Test `uri3 explain` completeness

Dla każdego ważnego URI:

```bash
uri3 explain weather://forecast/Gdansk/14/html
uri3 explain browser://chrome/page/open
uri3 explain stt://mock/transcribe
uri3 explain hypervisor://local/weather-agent/run
```

Oczekiwane pola:

```txt
scheme
matched_by
capability
backend
operation
policy
result_contract
runtime_transport
verification
```

---

### 7.7. Test `uri3 doctor`

`uri3 doctor` powinien wykrywać:

```txt
brak configów
brak touri registry
brak uri2ops registry
brak result envelope
brak capability plan
stare workflow logs z błędami
brak .registry index
```

Test:

```bash
uri3 doctor --json
```

Oczekiwane:

```json
{
  "ok": true,
  "checks": [...]
}
```

---

### 7.8. Test import graph / dependency graph

Cel: wykryć cykle i niepożądane zależności.

Narzędzia:

```bash
python -m pip install grimp import-linter
```

Przykładowe kontrakty:

```ini
[importlinter:contract:uri2verify-no-runtime]
type = forbidden
source_modules = uri2verify
forbidden_modules = uri2run, uri2ops.server, hypervisor.deployment_registry

[importlinter:contract:uri2flow-no-execution]
type = forbidden
source_modules = uri2flow
forbidden_modules = uri3.graph.graph_executor, hypervisor, touri.executor
```

---

### 7.9. Mutation tests na statusy

Cel: sprawdzić, czy testy złapią błędną interpretację `ok`.

Przykłady mutacji:

```txt
service_result_status failed -> succeeded
ok false -> true
errors [] mimo błędu
timeout jako warning zamiast error
```

Narzędzie:

```bash
mutmut run
```

---

### 7.10. Contract golden tests

Dla ważnych flow i capability trzymać golden outputs:

```txt
tests/golden/
  weather_flow.expanded.yaml
  browser_open.service_result.json
  voice_command.uri_flow.yaml
  doctor.ok.json
  explain.weather.json
```

Test porównuje wynik z golden file po normalizacji dynamicznych pól.

---

## 8. Proponowany plan wdrożenia testów

### Sprint A: architektura bez `uri2run`

```txt
1. tests/architecture/test_import_boundaries.py
2. tests/architecture/test_result_envelope_contract.py
3. tests/architecture/test_explain_contract.py
4. tests/architecture/test_doctor_contract.py
```

### Sprint B: `uri2run` MVP

```txt
1. packages/uri2run
2. przenieść python/shell/http/flow/graph backend execution
3. touri deleguje backend execution do uri2run
4. tests/uri2run/test_transport_matrix.py
```

### Sprint C: failure matrix

```txt
1. timeout tests
2. bad JSON tests
3. shell exit code tests
4. HTTP 500 tests
5. WS/SSE disconnect tests
```

### Sprint D: replay/golden/mutation

```txt
1. replay creates regression tests
2. golden files dla examples
3. mutmut dla statusów
```

---

## 9. Minimalny zestaw komend CI

```bash
pytest tests/uri2flow -q
pytest tests/touri -q
pytest tests/uri2voice -q
pytest tests/uri2pact -q
pytest tests/uri2verify -q
pytest tests/uri3 -q
pytest tests/hypervisor -q
pytest tests/integration -q

uri3 doctor --json
uri3 explain weather://forecast/Gdansk/14/html
uri2verify capability-plan .
uri2verify replay --help
```

Po dodaniu `uri2run`:

```bash
pytest tests/uri2run -q
uri2run call python://uri2voice.tts:speak --payload '{"text":"test"}'
uri2run call http://localhost:8101/health --timeout 2
```

---

## 10. Ostateczna rekomendacja

Największy obecny deficyt to brak `uri2run` jako neutralnego runtime'u transportowego. Projekt ma już dobrze wydzielone warstwy planowania, flow, capability, voice, pact, verify i doctor. Teraz trzeba usunąć rozproszenie wykonania.

Najlepsza kolejność:

```txt
1. Dodać testy architektoniczne granic paczek.
2. Dodać `uri2run` MVP.
3. Przenieść backend execution z `touri` do `uri2run` przez wrappery kompatybilności.
4. Użyć `uri2verify` do testów data_quality, replay i statusów.
5. Rozszerzyć `uri3 doctor` i `uri3 explain` o runtime_transport.
```

Najważniejsza zasada:

```txt
Planner nie wykonuje.
Compiler nie wykonuje.
Capability registry nie implementuje transportu.
Runtime nie decyduje o policy.
Verifier nie naprawia.
Hypervisor nie jest runtime'em transportowym.
```


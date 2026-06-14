# URI Runtime / `uri2run` — miejsce w architekturze, deficyty i testy architektoniczne

Status 2026-06-14: MVP istnieje w `packages/uri2run` i obsługuje `python`,
`shell`, `http`, `stdio`, `sse`, `ws`, `docker`, `ssh`, `mcp`, `a2a`,
`uri_flow`, `uri_graph`, `uri2ops` oraz `mock`.
`touri` deleguje wykonanie backendów do `uri2run` przez wrappery kompatybilności.

## 1. Cel dokumentu

Ten dokument opisuje, jak powinna działać brakująca warstwa runtime niezależna od środowiska wykonania, roboczo nazwana `uri2run`, oraz jak ma się ona do istniejących modułów:

- `uri3`
- `uri2flow`
- `touri`
- `uri2ops`
- `uri2voice`
- `uri2pact`
- `uri2verify`
- `resource-agent-hypervisor`
- `nl2uri`

Celem `uri2run` jest wydzielenie wspólnego mechanizmu uruchamiania backendów przez różne transporty:

```txt
python
shell
http
websocket/ws
sse
stdio
docker
ssh
mcp
a2a
uri_flow
uri_graph
```

Obecnie te odpowiedzialności są częściowo rozproszone między `touri/backends`, `uri3/graph`, `uri2ops/server`, `hypervisor/deployment_registry` i `runtime_client`.

---

## 2. Problem, który rozwiązuje `uri2run`

Obecna architektura ma już dobre rozdzielenie planowania, capability, flow, operatorów i weryfikacji, ale wykonanie nadal pojawia się w kilku miejscach.

### Obecny stan uproszczony

```txt
nl2uri
  prompt -> uri_flow / graph / uri_tree

uri2flow
  compact flow -> workflow graph

uri3
  resolve / explain / graph execution / replay / doctor

touri
  URI -> capability manifest -> backend dispatch

uri2ops
  operation registry + browser/OS/operator execution

uri2voice
  STT/TTS/voice handlers

uri2pact
  markpact:// loader / pactown-style import

uri2verify
  data quality / replay / result checks

hypervisor
  lifecycle / deployment / contract registry / policy
```

### Brakujący element

Brakuje jednego neutralnego wykonawcy:

```txt
URI/capability/backend -> transport runtime -> ServiceResult
```

Dlatego proponowana paczka:

```txt
packages/uri2run
```

---

## 3. Zasada podstawowa

`uri2run` nie planuje, nie decyduje o domenie i nie zarządza lifecycle agentów.

`uri2run` tylko wykonuje pojedynczy backend call.

```txt
Planner decyduje CO zrobić.
Registry decyduje CZYM to zrobić.
Runtime decyduje JAK technicznie to uruchomić.
Verifier decyduje CZY wynik jest poprawny.
Hypervisor decyduje CZY wolno i gdzie to uruchomić.
```

---

## 4. Docelowy podział odpowiedzialności

| Moduł | Odpowiedzialność | Czego nie powinien robić |
|---|---|---|
| `nl2uri` | prompt -> URI / flow / graph | wykonywać backendów |
| `uri2flow` | compact flow -> workflow graph | odpalać HTTP/shell/python |
| `uri3` | URI core, graph orchestration, explain, doctor | posiadać własnych transportów dla wszystkiego |
| `touri` | capability registry, manifest matching, fallback policy | implementować wszystkie transporty |
| `uri2run` | wykonanie backendów przez transporty | planować, walidować domenowo, zarządzać agentami |
| `uri2ops` | OS/UI/browser/operator actions | być ogólnym runtime dla shell/http/ws |
| `uri2voice` | STT/TTS/audio/wake handlers | planować workflow |
| `uri2pact` | markpact/pactown import/export | wykonywać capability |
| `uri2verify` | data quality, replay, regression tests | wykonywać runtime call jako źródło prawdy |
| `hypervisor` | lifecycle, deployment, policy, registry | być niskopoziomowym runtime transportowym |

---

## 5. Gdzie `uri2run` wchodzi w pipeline

### 5.1. Capability execution

```txt
touri call weather://forecast/Gdansk/14/html
  ↓
touri znajduje capability
  ↓
touri waliduje manifest i payload
  ↓
touri przekazuje backend do uri2run
  ↓
uri2run wykonuje python/http/shell/...
  ↓
uri2run zwraca ServiceResult
  ↓
touri nakłada fallback/data quality/redaction
```

### 5.2. Workflow execution

```txt
uri3 run-workflow workflow.uri.graph.yaml
  ↓
uri3 ustala kolejność kroków
  ↓
uri3 dla każdego node wybiera adapter
  ↓
adapter przekazuje call do touri / uri2ops / hypervisor / uri2run
  ↓
wynik wraca jako StepExecutionResult
  ↓
uri3 agreguje workflow_status i service_result_status
```

### 5.3. Voice command

```txt
audio://mic/default
  ↓
stt://mock/transcribe
  ↓
uri2voice handler
  ↓
nl2uri flow
  ↓
uri2flow expand
  ↓
uri3 run-workflow
  ↓
tts://mock/speak
```

`uri2voice` może być wywoływany jako Python backend przez `uri2run`.

### 5.4. Operator execution

```txt
browser://chrome/page/open
  ↓
uri3 graph node
  ↓
uri2ops adapter
  ↓
uri2ops operation registry
  ↓
Playwright / mock / remote operator
```

`uri2ops` nie powinno być zastępowane przez `uri2run`. `uri2run` może jednak obsługiwać transport do zdalnego `uri2ops`, np. HTTP/WS.

---

## 6. Proponowana struktura `uri2run`

```txt
packages/uri2run/
├── pyproject.toml
├── uri2run/
│   ├── __init__.py
│   ├── models.py
│   ├── context.py
│   ├── result.py
│   ├── runner.py
│   ├── cli.py
│   ├── transports/
│   │   ├── python_transport.py
│   │   ├── shell_transport.py
│   │   ├── http_transport.py
│   │   ├── ws_transport.py
│   │   ├── sse_transport.py
│   │   ├── stdio_transport.py
│   │   ├── docker_transport.py
│   │   ├── ssh_transport.py
│   │   ├── mcp_transport.py
│   │   ├── a2a_transport.py
│   │   ├── uri_flow_transport.py
│   │   └── uri_graph_transport.py
│   └── servers/
│       ├── http_server.py
│       ├── ws_server.py
│       └── sse_server.py
└── tests/
```

Minimalny Sprint:

```txt
python_transport
shell_transport
http_transport
uri_flow_transport
uri_graph_transport
```

Dopiero potem:

```txt
ws
sse
stdio
docker
ssh
mcp
a2a
```

---

## 7. API proponowane dla `uri2run`

### Python API

```python
from uri2run import run_backend

result = run_backend(
    backend={
        "type": "python",
        "target": "python://uri2voice.stt:transcribe",
    },
    payload={"text": "sprawdź health agenta"},
    context={"root": "."},
)
```

### CLI

```bash
uri2run call python://uri2voice.stt:transcribe \
  --payload '{"text":"sprawdź health agenta"}'

uri2run call shell://scripts/check.sh \
  --payload '{"args":["--dry-run"]}'

uri2run call http://localhost:8101/health

uri2run call ws://localhost:8090/ws \
  --payload '{"type":"ping"}'

uri2run call sse://localhost:8090/events --listen
```

---

## 8. Format wyniku

Każdy transport musi zwracać ujednolicony `ServiceResult` albo wynik zgodny z envelope `uri3.results`.

Przykład:

```json
{
  "ok": true,
  "execution_status": "completed",
  "service_result_status": "succeeded",
  "result_type": "json",
  "data": {
    "message": "ok"
  },
  "errors": [],
  "warnings": [],
  "meta": {
    "transport": "http",
    "target": "http://localhost:8101/health",
    "duration_ms": 42
  }
}
```

Błąd biznesowy i błąd techniczny nie mogą być tym samym.

Przykład:

```json
{
  "ok": false,
  "execution_status": "completed",
  "service_result_status": "failed",
  "data_quality_status": "failed",
  "errors": [
    {
      "code": "PRICE_RESULT_NOT_RELEVANT",
      "source": "uri2verify.data_quality",
      "recoverable": true,
      "detail": "Visible prices found, but not for requested product"
    }
  ]
}
```

---

## 9. Deficyty widoczne w architekturze

### 9.1. Brak jednego runtime transportowego

Obecnie wiele paczek ma własny sposób wykonania:

```txt
touri/backends
uri3/graph/adapters
uri2ops/dispatcher
hypervisor/deployment_registry
runtime_client
```

To może prowadzić do:

```txt
różnych formatów błędów,
różnych timeoutów,
różnego redaction,
różnych retry policy,
różnego statusowania.
```

`uri2run` powinien ujednolicić transporty.

---

### 9.2. Ryzyko powrotu do problemów typu tellm

Jeżeli każdy backend sam decyduje, czy wynik jest OK, system może znowu mieszać:

```txt
workflow ok
execution ok
service result failed
business result failed
```

Dlatego `uri2verify` i wspólny result envelope są krytyczne.

---

### 9.3. Duplikacja adapterów browser/operator

Wciąż istnieją ślady browser adapterów w `uri3`, mimo że docelowo operator powinien żyć w `uri2ops`.

Zasada:

```txt
uri3 orchestrates.
uri2ops operates.
uri2run transports.
```

---

### 9.4. `touri` może znowu urosnąć

`touri` powinno zostać registry/capability runtime, ale nie powinno zbierać coraz większej liczby backendów.

Docelowo:

```txt
touri/backend_dispatch.py
  ↓
deleguje do uri2run
```

---

### 9.5. Brak testów granic pakietów

Największe ryzyko nie leży już w jednej funkcji, ale w błędnych granicach:

```txt
Czy touri nie wykonuje za dużo?
Czy uri3 nie steruje browserem bezpośrednio?
Czy uri2verify nie wykonuje runtime?
Czy hypervisor nie parsuje capability?
Czy uri2run nie planuje workflow?
```

To trzeba testować architektonicznie.

---

## 10. Testy wykrywające błędy architektury

### 10.1. Test granic importów

Cel: wykryć niepożądane zależności między paczkami.

Przykładowe reguły:

```txt
uri2run nie importuje hypervisor
uri2run nie importuje nl2uri
uri2run nie importuje uri2verify
uri2verify nie importuje uri2run
uri2flow nie importuje hypervisor
touri nie importuje hypervisor
uri2voice nie importuje uri3 graph executor
hypervisor nie importuje Playwright
```

Przykładowy test:

```python
FORBIDDEN_IMPORTS = {
    "uri2run": ["hypervisor", "nl2uri", "uri2verify"],
    "uri2verify": ["uri2run", "uri2ops.server"],
    "touri": ["hypervisor"],
    "uri2flow": ["hypervisor"],
    "uri2voice": ["uri3.graph"],
}

def test_forbidden_imports():
    ...
```

---

### 10.2. Test single responsibility przez CLI smoke

Każda paczka musi mieć CLI smoke, które robi tylko swoją rolę.

```bash
nl2uri flow -p "sprawdź health agenta" --validate
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml
touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
uri2voice mock-stt albo touri call stt://mock/transcribe
uri2verify replay output/events/sample.jsonl
uri3 explain weather://forecast/Gdansk/14/html
uri3 doctor
```

Fail, jeśli CLI zaczyna wymagać nie swojej warstwy.

---

### 10.3. Test result envelope

Każdy publiczny call powinien zwracać pola:

```txt
ok
execution_status
service_result_status
result_type
data
errors
warnings
meta
```

Test:

```python
def assert_service_result_shape(result):
    required = {
        "ok",
        "execution_status",
        "service_result_status",
        "result_type",
        "data",
        "errors",
        "warnings",
        "meta",
    }
    assert required <= set(result)
```

Stosować do:

```txt
touri call
uri2run call
uri2ops dispatch
uri3 step result
hypervisor lifecycle result
uri2verify data_quality
```

---

### 10.4. Test technicznie OK, biznesowo failed

To najważniejszy test przeciw błędom typu tellm.

Fixture:

```json
{
  "ok": true,
  "execution_status": "completed",
  "service_result_status": "succeeded",
  "data": {
    "confidence": 0.2
  }
}
```

Po `uri2verify.apply_data_quality` wynik powinien być:

```json
{
  "ok": false,
  "execution_status": "completed",
  "service_result_status": "failed",
  "data_quality_status": "failed"
}
```

---

### 10.5. Test replay jako regresja

Każdy błąd z event logu powinien dać się zamienić w test.

```bash
uri2verify replay output/events/workflow_failed.jsonl --create-test
pytest tests/regression/test_replay_*.py
```

Test sprawdza:

```txt
czy workflow_id został odtworzony,
czy kroki są te same,
czy failed_nodes są te same,
czy error_code jest zachowany.
```

---

### 10.6. Test fallback capability

Dla `touri`:

```txt
primary backend returns PRICE_RESULT_NOT_RELEVANT
fallback backend executes
result contains fallback metadata
original error is preserved
```

---

### 10.7. Test markpact boundary

Dla `uri2pact`:

```txt
README contains markpact:capability
uri2pact extracts dict
touri loads manifest
touri executes capability
```

Dla `markpact:flow`:

```txt
README contains markpact:flow
uri2pact extracts flow
uri2flow expands graph
uri3 validates workflow
```

---

### 10.8. Test operator delegation

Dla `uri3`:

```txt
browser://chrome/page/open
```

nie powinien używać legacy browser adapter, tylko `uri2ops_adapter`, chyba że jawnie ustawiono legacy flag.

Test:

```txt
URI3_USE_LEGACY_BROWSER=0
uri3 run-workflow browser workflow
assert adapter == uri2ops
```

---

### 10.9. Test runtime transport matrix

Dla `uri2run`:

| Transport | Test |
|---|---|
| `python` | funkcja handler zwraca ServiceResult |
| `shell` | skrypt zwraca JSON |
| `http` | local test server `/health` |
| `ws` | local echo websocket |
| `sse` | local event stream |
| `stdio` | subprocess echo protocol |
| `uri_flow` | flow expands and dry-runs |
| `uri_graph` | graph validates and dry-runs |

Na początku wystarczy:

```txt
python
shell
http
uri_flow
uri_graph
```

---

### 10.10. Test `doctor`

`uri3 doctor` powinien wykrywać:

```txt
brak configu touri
brak operation registry uri2ops
niepoprawny ServiceResult
brak capability plan
nieudany replay
duplikaty URI
niezgodne dependencies
```

Minimalny test:

```bash
uri3 doctor --json
```

i asercja:

```txt
summary.ok == true
checks include:
  config
  contract_registry
  touri_registry
  uri2ops_registry
  result_envelope
  capability_plan
```

---

## 11. Testy architektury na poziomie repo

### 11.1. Test braku cykli importów

```bash
pydeps packages --show-cycles
```

albo własny AST parser importów.

Warunek:

```txt
cycles == []
```

---

### 11.2. Test fan-out / complexity budget

Budżety:

```txt
CC average <= 4.0
critical <= 5
fan-out pojedynczej funkcji <= 25
plik <= 250 linii, wyjątki jawnie opisane
```

Obecnie projekt ma dobry trend, bo średnie CC spadło do okolic 3.3. Ten trend należy utrzymać.

---

### 11.3. Test boundaries z manifestu

Dodać plik:

```txt
docs/PACKAGE_BOUNDARIES.yaml
```

Przykład:

```yaml
packages:
  uri2run:
    allowed_imports:
      - uri3.results
      - yaml
      - json
      - subprocess
      - requests
    forbidden_imports:
      - hypervisor
      - nl2uri
      - uri2verify

  uri2verify:
    forbidden_imports:
      - uri2run
      - hypervisor.deployment_registry

  touri:
    allowed_imports:
      - uri2pact
      - uri2verify
      - uri3.results
    forbidden_imports:
      - hypervisor
```

Test czyta YAML i skanuje importy.

---

## 12. Rekomendowany plan wdrożenia `uri2run`

### Sprint 3c.1 — scaffold

```txt
packages/uri2run
  models.py
  runner.py
  result.py
  cli.py
  transports/python_transport.py
  transports/shell_transport.py
  transports/http_transport.py
```

### Sprint 3c.2 — integracja z `touri`

```txt
touri/backend_dispatch.py
  deleguje python/shell/http do uri2run
```

Stare importy zostają jako wrappery.

### Sprint 3c.3 — transporty workflow

```txt
uri_flow_transport
uri_graph_transport
```

Wykorzystują istniejące `uri2flow` i `uri3`.

### Sprint 3c.4 — transporty streamingowe

```txt
ws_transport
sse_transport
stdio_transport
```

### Sprint 3c.5 — transporty agentowe

```txt
mcp_transport
a2a_transport
docker_transport
ssh_transport
```

---

## 13. Kolejność testów przed merge

```bash
pytest tests/uri2run -q
pytest tests/touri -q
pytest tests/uri2verify -q
pytest tests/uri2flow -q
pytest tests/uri3 -q
pytest tests/hypervisor -q
pytest -q
```

Dodatkowo:

```bash
uri3 doctor --json
uri3 explain weather://forecast/Gdansk/14/html
touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities
uri2verify capability-plan .
```

---

## 14. Decyzja końcowa

`uri2run` jest brakującą warstwą między capability a środowiskiem wykonania.

Bez `uri2run` system będzie działał, ale runtime będzie rozproszony:

```txt
touri wykonuje backendy,
uri3 wykonuje adaptery,
uri2ops wykonuje operacje,
hypervisor wykonuje deploymenty.
```

Z `uri2run`:

```txt
touri wybiera capability,
uri2run wykonuje backend,
uri2verify ocenia wynik,
uri3 orkiestruje graph,
hypervisor zarządza lifecycle.
```

To jest czystszy model i lepsza ochrona przed monolitem podobnym do `tellm`.

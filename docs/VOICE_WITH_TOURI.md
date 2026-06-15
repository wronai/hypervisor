# Voice with touri

STT/TTS from `tellm` are implemented as a **touri capability pack** backed by
`packages/uri2voice`, not a monolithic server.

```txt
Current:
  examples/21_touri_voice — capability manifests
  packages/uri2voice      — Python handlers for mock STT/TTS, voice planning and Whisper STT
  www/chat.html           — microphone button, transcript → normal NL planning

Next:
  richer audio profiles, real TTS output engines, wake-word / hands-free profile
```

## Architecture

```txt
microphone / text
    → stt://...           (touri capability)
    → voice://command/... (nl2uri flow)
    → uri2flow expand
    → uri3 validate/run
    → tts://...           (touri capability)
```

`touri` resolves URIs through `*.uri.capability.yaml` — same pattern as weather or browser operator capabilities.

## Capability pack

| URI | Capability | Backend |
|-----|------------|---------|
| `stt://mock/transcribe` | `stt.mock.transcribe` | `uri2voice.stt:transcribe` |
| `stt://local/whisper` | `stt.local.whisper` | `uri2voice.stt_whisper:transcribe_whisper` |
| `tts://mock/speak` | `tts.mock.speak` | `uri2voice.tts:speak` |
| `voice://command/from-text` | `voice.command.from_text` | `uri2voice.voice_command:plan_voice_command` |

Location: [`examples/21_touri_voice/`](../examples/21_touri_voice/README.md)

## Commands

```bash
touri call stt://mock/transcribe \
  --registry examples/21_touri_voice \
  --payload '{"text":"otwórz Chrome i sprawdź health"}'

touri call voice://command/from-text \
  --registry examples/21_touri_voice \
  --payload '{"text":"wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome"}'

touri call tts://mock/speak \
  --registry examples/21_touri_voice \
  --payload '{"text":"Agent działa poprawnie"}'
```

## Pipeline after voice planning

```bash
uri2flow expand output/artifacts/voice/voice_command.uri.flow.yaml \
  --out output/artifacts/voice/voice_command.uri.graph.yaml

uri3 validate-workflow output/artifacts/voice/voice_command.uri.graph.yaml
uri3 run-workflow output/artifacts/voice/voice_command.uri.graph.yaml --dry-run
```

## WWW chat microphone

The browser chat has a microphone control:

```text
MediaRecorder audio/webm
  → POST /api/voice/transcribe
  → transcript text
  → POST /api/ask
  → user clicks URI / Run plan action
```

Execution is intentionally not hands-free: the transcript becomes a normal chat
prompt, then policy and approval rules apply exactly as they do for typed text.

API examples:

```bash
curl -s -X POST http://localhost:8788/api/voice/transcribe \
  -H 'Content-Type: application/json' \
  -d '{"engine":"mock","text":"zdiagnozuj agenta invoices-agent.local"}'
```

## What we took from tellm

| tellm concept | touri equivalent |
|---------------|------------------|
| `TellmBot.transcribe` | `stt://...` capability handler |
| `TellmBot.speak` | `tts://...` capability handler |
| `service_result` | shared `uri3.results.ServiceResult` envelope |
| `generate_test_audio` | mock STT with `text` / `transcript_file` |
| `TellmServer.process_request` | **not ported** — too monolithic |

## Real STT/TTS

### Whisper STT

`stt://local/whisper` is already declared in
[`examples/21_touri_voice/stt_whisper.uri.capability.yaml`](../examples/21_touri_voice/stt_whisper.uri.capability.yaml)
and implemented by `uri2voice.stt_whisper:transcribe_whisper`.

Runtime selection:

| Mode | Requirements |
|------|--------------|
| `engine=openai` or `OPENAI_API_KEY` set | OpenAI audio transcription API |
| `engine=local` or no API key | optional local `openai-whisper` Python package |
| no audio, text supplied | deterministic text fallback for tests and demos |

### Local piper

Real TTS remains a manifest-level target for a future engine:

```yaml
capability:
  id: tts.local.piper
  scheme: tts
  uri_template: tts://local/piper
backend:
  type: python
  target: python://your_voice_runtime.piper:speak
```

### Cloud (secrets by URI)

Never embed API keys in manifests:

```yaml
backend:
  type: python
  target: python://uri2voice.stt_whisper:transcribe_whisper
  extra:
    model: gpt-4o-transcribe
    api_key: env://OPENAI_API_KEY
```

Or reference `config/llm.uri.yaml` profiles from handler code.

## Anti-tellm rules

- Mock STT must not pretend to read real audio without validation
- TTS artifacts are metadata mocks until real audio engines are wired
- `voice://command/from-text` produces **flow proposals** — validate with `uri2flow` / `uri3` before execution
- Use `ServiceResult` with structured `errors[].code`, not bare `ok=true`

See [`ANTI_TELLM.md`](./ANTI_TELLM.md) and [`TOURI.md`](./TOURI.md).

## Tests

```bash
pytest tests/touri/test_voice_capabilities.py -q
make voice-demo
```

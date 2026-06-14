# uri2run

Neutral runtime layer for executing URI backends through concrete transports.

`uri2run` does not plan workflows and does not own capability registries. It only
executes one backend call and returns the shared `uri3.results.ServiceResult`
envelope.

## Initial transports

```txt
python     python://module:function
shell      shell command
http       http:// / https:// target
uri_flow   compact URI flow file
uri_graph  workflow graph file
uri2ops    operator registry dispatch
mock       test/runtime fixture transport
```

## CLI

```bash
uri2run call python://uri2voice.stt:transcribe --payload '{"text":"test"}'
uri2run call shell://echo --payload '{"args":["hello"]}'
uri2run call http://localhost:8101/health
```

See `docs/PACKAGE_BOUNDARIES.md` for the package split roadmap.

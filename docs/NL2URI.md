# nl2uri

`nl2uri` tłumaczy query w języku naturalnym na `URI Tree`.

```bash
nl2uri generate --no-llm -p "generuj mape pogody dwa tygodnie do przodu ..." --out domains/weather_map/uri_tree.yaml
```

Domyślnie używa LLM przez `.env`, a bez klucza robi fallback do plannera regułowego.

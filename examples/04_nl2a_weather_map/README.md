# Example 04 — prompt do weather-map Domain Pack

Przykład docelowego przepływu:

```bash
nl2a generate --no-llm -p "generuj mape pogody dwa tygodnie do przodu w oparciu o miejscowosc i odpowiedni model przewidujacy pogode, generuj widok w formie html pod adresem url"
```

W tej wersji najważniejszym artefaktem pośrednim jest:

```txt
domains/weather_map/uri_tree.yaml
```

Potem można go sprawdzić:

```bash
uri3 validate-tree domains/weather_map/uri_tree.yaml
uri3 graph domains/weather_map/uri_tree.yaml
```

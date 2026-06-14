## Compact URI Flow

Projekt obsługuje kompaktowy zapis flow oparty głównie na URI:

```yaml
flow:
  id: weather-agent-local-health

do:
  - agent://weather-generator
  - hypervisor://local/weather-agent/run
  - browser://chrome/page/open:
      url: http://localhost:8101/health
```

Rozwinięcie do pełnego grafu:

```bash
uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml
```

`uri2flow` nie wykonuje workflow. Wykonanie należy do `uri3`, `uri2ops` albo `hypervisor`.

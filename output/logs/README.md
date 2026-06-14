# Log streams (`output/logs/`)

JSON-lines log files used by `uri3 logs log://…`.

| Stream | File | Writers |
|--------|------|---------|
| `hypervisor` | `output/logs/hypervisor.log` | hypervisor CLI, deployment registry |
| `nl2a` | `output/logs/nl2a.log` | nl2a / nl2uri pipeline |
| `nl2uri` | `output/logs/nl2uri.log` | nl2uri planner |
| `factory` | `output/logs/factory.log` | generator / verify |
| `uri3` | `output/logs/uri3.log` | uri3 tools |
| `meta_agent` | `output/logs/meta_agent.log` | meta-agent |

Pliki powstają po pierwszym uruchomieniu pipeline (`nl2a`) lub `hypervisor run-agent`.

Przykłady:

```bash
uri3 logs 'log://hypervisor?limit=20'
uri3 logs 'log://nl2a?grep=pipeline' --summary
uri3 logs 'log://hypervisor?level=ERROR&limit=50'
```

Jeśli plik nie istnieje, użyj `--summary` lub sprawdź pole `hint` w odpowiedzi JSON.

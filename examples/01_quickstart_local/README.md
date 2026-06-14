# Example 01 — lokalny quickstart

Minimalny przepływ bez Dockera i bez LLM.

```bash
pip install -e .[dev]
make uri-tree
make validate
make graph
pytest -q
```

Wynikowy URI Tree znajdziesz w:

```txt
domains/weather_map/uri_tree.yaml
```

Ten przykład pokazuje podstawowy łańcuch:

```txt
prompt -> nl2uri -> URI Tree -> uri3 validate/graph
```

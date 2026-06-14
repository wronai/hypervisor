# CLI reference — urish first

**User-facing:** `uri` / `urish`  
**Backends:** uri3, uri2run, urigen, hypervisor, uri2ops, touri

Full package map: [`CLI_MAP.md`](./CLI_MAP.md)

## urish / uri

```bash
uri ask "…"                    # NL → intent + next steps (no mutation)
uri call <uri> [--payload …]   # execute URI via uri2run
uri explain <uri>              # uri3 explain
uri plan <uri>                 # dry-run call
uri run <workflow-uri>         # uri2ops / workflow
uri logs / watch / stream      # observation
uri doctor [--strict]          # uri3 + artifact gates
uri select data.text           # pipe envelope fields

uri agent status|health|run|inspect …
uri ecosystem plan|generate|verify|apply …
uri dashboard create|open
uri repair diagnose|apply|learn …
uri ticket list|show|import|plan …
uri evolve from-ticket|from-incident …
uri proposal verify|apply …
uri shell                      # REPL
```

## Policy flags

```bash
--dry-run          # plan only, no mutation
--approve          # allow side effects
--sandbox          # evolution/proposal dry apply
--readonly         # block mutating URIs
--policy dev|safe|prod
```

Exit codes: `0=ok`, `1=failed`, `2=execution`, `3=validation`, `4=policy blocked`, `5=not found`, `6=dependency missing`

## Level 3+ (direct backends)

```bash
uri3 explain …
uri3 doctor
uri2run call …
urigen plan|generate|verify|apply …
hypervisor inspect-agent …
hypervisor artifacts check
```

Prefer **`uri`** until you need backend-specific flags.

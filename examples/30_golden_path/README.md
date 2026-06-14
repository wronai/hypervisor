# Example 30 — Golden path (15 min tutorial)

End-to-end mental model without mutating the repo:

```text
weather agent → observe → diagnose → dashboard view → ticket/evolution (dry-run)
```

## Run

```bash
bash examples/30_golden_path/run.sh
```

## What you learn

1. **Call URI** — shell echo via uri2run  
2. **Check agent** — status + health URIs  
3. **Plan ecosystem** — `urish ask` + ecosystem plan (dry)  
4. **Repair loop** — diagnose (read-only)  
5. **Dashboard** — ask for dashboard-agent profile + next steps  

## Full story (when agents are running)

```text
Create weather agent → run → break port/health → incident →
dashboard shows timeline → repair → ticket → evolution proposal
```

See [`docs/GETTING_STARTED.md`](../../docs/GETTING_STARTED.md) and [`docs/AUTONOMY_LOOP.md`](../../docs/AUTONOMY_LOOP.md).

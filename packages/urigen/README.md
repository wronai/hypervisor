# urigen

`urigen` is the URI Ecosystem Generator. It creates proposal and ecosystem
artifacts, then delegates validation to existing packages:

```txt
urigen generates.
touri registers capabilities.
uri2flow compiles flows.
uri3 explains and diagnoses.
uri2verify checks result contracts.
hypervisor deploys and manages lifecycle.
```

It is not a runtime transport and it does not execute backends directly.

## CLI

```bash
urigen plan -p "stworz agenta pogodowego z healthcheckiem" --out output/proposals/weather.ecosystem.proposal.yaml
urigen generate output/proposals/weather.ecosystem.proposal.yaml --out output/ecosystems/weather
urigen verify output/ecosystems/weather/ecosystem.yaml
urigen explain output/ecosystems/weather/ecosystem.yaml
```

`plan` and `verify` are side-effect safe. `generate` writes only the requested
output directory. `apply --plan` writes `apply_plan.yaml` and a diff preview.
`apply --approve` mutates the repo transactionally, writes `apply_result.json`,
and auto-rolls back on failure. Use `--rollback` to restore from
`rollback/manifest.json`.

## Current MVP

The first implementation is intentionally deterministic and repo-local:

```txt
plan      builds a proposal from a prompt and profile
generate  assembles a weather/voice ecosystem from existing repo artifacts
verify    validates capabilities, flows, sample URI explain output and doctor
explain   renders domains, agents, capabilities, flows, deployments and risks
apply     --plan shows diff; --approve executes ApplyPlan; failure auto-rolls back
          --rollback restores from rollback/manifest.json
schema    check validates ecosystem YAML envelopes and apply artifacts
```

`urigen` imports high-level validators from `touri`, `uri2flow` and `uri3`.
It must not import `uri2run.transports`, `uri2ops.server` or low-level
hypervisor process runtime modules.

## Artifact Contract

Every generated ecosystem directory contains:

```txt
ecosystem.yaml
README.md
capabilities/
flows/
contracts/
deployments/
tests/
```

`ecosystem.yaml` is the source of truth for verification and explain output.
Generated proposal and ecosystem YAML files are canonical URI3 artifacts:
`$schema`, `apiVersion`, `kind`, `metadata`, `uri.self` and `spec` are emitted
at the top of the document, while legacy-compatible fields remain available for
existing readers.

Generated capability manifests receive a default, non-failing `data_quality`
policy so `uri3 explain` and `urigen explain` can distinguish an intentionally
checked generated path from an ungoverned capability.

## Profiles

The planner accepts these profile names:

- `minimal` — weather demo ecosystem
- `voice` — weather + voice capabilities
- `dashboard-agent` — hypervisor dashboard system agent (view/repair/ticket UI)
- `agent`, `operator`, `provider`, `full` — extended profiles (partial)

Friendly aliases are accepted for onboarding:

- `dashboard` → `dashboard-agent`
- `voice-agent` → `voice`
- `operator-agent` → `operator`
- `ecosystem` / `full-ecosystem` → `full`

```txt
minimal
agent
voice
operator
provider
full
dashboard-agent
```

List profiles from the CLI:

```bash
urigen profiles
uri ecosystem profiles
```

The MVP uses `minimal` and `voice` paths directly. The other profiles are
reserved in the proposal contract and should be expanded without moving runtime
execution into `urigen`.

## Verification

`urigen verify` checks:

```txt
touri manifest validation
uri2flow validation and workflow graph validation
uri3 explain for each sample_uri
uri3 doctor against the generated capability registry
```

When report writing is enabled, it writes `verify_report.json` next to
`ecosystem.yaml`.

## Next Work

```txt
JSON Schema validation on plan/generate
dashboard app/ generation inside ecosystem output
profile-specific generators (agent, operator, provider, full)
markpact README export with capability/flow/deploy/test blocks
recovery reports and uri2verify replay integration
```

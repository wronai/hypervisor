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
output directory. `apply` is approval-gated and currently reports the idempotent
plan instead of mutating repository registries.

## Current MVP

The first implementation is intentionally deterministic and repo-local:

```txt
plan      builds a proposal from a prompt and profile
generate  assembles a weather/voice ecosystem from existing repo artifacts
verify    validates capabilities, flows, sample URI explain output and doctor
explain   renders domains, agents, capabilities, flows, deployments and risks
apply     blocks without --approve; with --approve returns skipped MVP actions
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

## Profiles

The planner accepts these profile names:

```txt
minimal
agent
voice
operator
provider
full
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
JSON Schema enforcement for proposal/ecosystem files
profile-specific generators
idempotent apply that can copy/merge artifacts safely
markpact README export with capability/flow/deploy/test blocks
recovery reports and uri2verify replay integration
```

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
hypervisor deployments | grep -q weather-map-agent
hypervisor run-agent weather-map-agent.local --dry-run | grep -q uvicorn

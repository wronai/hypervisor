#!/usr/bin/env bash
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../tellmesh/resource-agent-hypervisor/scripts/ci" && pwd)/ensure_editable_install.sh" "$@"

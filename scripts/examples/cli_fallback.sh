#!/usr/bin/env bash
_TELLMESH_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../tellmesh/resource-agent-hypervisor/scripts/examples" && pwd)/cli_fallback.sh"
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  exec bash "$_TELLMESH_SCRIPT" "$@"
else
  # shellcheck source=/dev/null
  source "$_TELLMESH_SCRIPT"
fi

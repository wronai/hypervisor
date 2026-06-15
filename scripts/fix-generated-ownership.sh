#!/usr/bin/env bash
# Fix ownership on agents/generated/* after Docker/root uvicorn runs.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-$ROOT/agents/generated}"
if [[ ! -d "$TARGET" ]]; then
  echo "Missing directory: $TARGET" >&2
  exit 1
fi
if [[ "$(id -u)" -ne 0 ]]; then
  echo "Re-run with sudo to fix ownership under $TARGET"
  echo "  sudo bash scripts/fix-generated-ownership.sh"
  exit 1
fi
OWNER="${SUDO_USER:-$USER}"
GROUP="$(id -gn "$OWNER")"
chown -R "$OWNER:$GROUP" "$TARGET"
echo "Fixed ownership: $TARGET -> $OWNER:$GROUP"

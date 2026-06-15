#!/usr/bin/env bash
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../tellmesh/www/scripts" && pwd)/install-cron.sh" "$@"

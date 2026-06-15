#!/usr/bin/env bash
# E-commerce integration mock — WooCommerce → BaseLinker → ERP
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "== 32_ecommerce_integrations =="
echo "1) explain workflow URI"
uri explain workflow://order/woocommerce-to-erp

echo "2) dry-run plan"
uri run workflow://order/woocommerce-to-erp --dry-run

echo "3) approved mock run"
uri run workflow://order/woocommerce-to-erp --approve

echo "PASS examples/32_ecommerce_integrations"

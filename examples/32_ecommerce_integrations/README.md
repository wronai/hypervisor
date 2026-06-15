# E-commerce integrations (mock)

WooCommerce, BaseLinker and Allegro order flows registered as `workflow://order/*` capabilities in `examples/20_touri_capabilities/`.

## Quick start

```bash
bash examples/32_ecommerce_integrations/run.sh
```

## URIs

| URI | Description |
|-----|-------------|
| `workflow://order/woocommerce-to-erp` | Woo → BaseLinker → ERP mock graph |
| `workflow://order/woocommerce-to-erp/dry-run` | Dry-run plan only |

```bash
uri explain workflow://order/woocommerce-to-erp
uri run workflow://order/woocommerce-to-erp --dry-run
uri run workflow://order/woocommerce-to-erp --approve
```

Natural-language routing (via `uri ask`):

```bash
uri ask "połącz WooCommerce, BaseLinker i ERP; pokaż błędy w chacie"
uri ask "dlaczego zamówienie z Allegro nie trafiło do ERP?"
```

Both map to `ecommerce_sync` with planned URI `workflow://order/woocommerce-to-erp/dry-run`.

from __future__ import annotations

import os
import warnings
from typing import Any

from uri3.graph.adapters.browser_mock import BrowserMockAdapter
from uri3.graph.adapters.browser_playwright import PlaywrightBrowserAdapter, close_playwright_session
from uri3.graph.execution_models import ExecutionContext
from uri3.graph.models import GraphNode

_PLAYWRIGHT_READY: bool | None = None


def _playwright_ready() -> bool:
    global _PLAYWRIGHT_READY
    if _PLAYWRIGHT_READY is not None:
        return _PLAYWRIGHT_READY
    try:
        from playwright.sync_api import sync_playwright

        playwright = sync_playwright().start()
        try:
            browser = playwright.chromium.launch(headless=True)
            browser.close()
            _PLAYWRIGHT_READY = True
        finally:
            playwright.stop()
    except Exception:
        _PLAYWRIGHT_READY = False
    return _PLAYWRIGHT_READY


def resolve_browser_mode(context: ExecutionContext) -> str:
    mode = (context.browser_mode or os.getenv("URI3_BROWSER_ADAPTER", "auto")).lower()
    if mode == "mock":
        return "mock"
    if mode == "playwright":
        return "playwright"
    return "playwright" if _playwright_ready() else "mock"


class BrowserRouterAdapter:
    """Deprecated: uri3 delegates operator schemes to uri2ops (see Uri2OpsAdapter)."""

    schemes = frozenset({"browser", "dom", "screen"})

    def __init__(self) -> None:
        self._mock = BrowserMockAdapter()
        self._playwright = PlaywrightBrowserAdapter()

    def execute(self, node: GraphNode, context: ExecutionContext) -> dict[str, Any]:
        warnings.warn(
            "BrowserRouterAdapter is deprecated; operator schemes delegate to uri2ops",
            DeprecationWarning,
            stacklevel=2,
        )
        mode = resolve_browser_mode(context)
        if mode == "playwright":
            return self._playwright.execute(node, context)
        return self._mock.execute(node, context)


def cleanup_browser_adapters(context: ExecutionContext) -> None:
    if context.adapter_state.get("playwright"):
        close_playwright_session(context)

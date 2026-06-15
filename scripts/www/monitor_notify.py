"""Compatibility shim — forwards imports to tellmesh/www/scripts/monitor_notify.py."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parent / "../../../../tellmesh/www/scripts/monitor_notify.py"
).resolve()

_spec = importlib.util.spec_from_file_location("monitor_notify", _TARGET)
if _spec is None or _spec.loader is None:
    raise ImportError(f"missing tellmesh monitor_notify: {_TARGET}")
_module = importlib.util.module_from_spec(_spec)
sys.modules[__name__] = _module
_spec.loader.exec_module(_module)

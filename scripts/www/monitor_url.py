#!/usr/bin/env python3
"""Compatibility shim — runs tellmesh/www/scripts/monitor_url.py."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parent / "../../../../tellmesh/www/scripts/monitor_url.py"
).resolve()

if __name__ == "__main__":
    sys.argv[0] = str(_TARGET)
    runpy.run_path(str(_TARGET), run_name="__main__")

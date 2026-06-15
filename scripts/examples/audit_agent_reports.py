#!/usr/bin/env python3
"""Compatibility shim — runs tellmesh/resource-agent-hypervisor/scripts/examples/audit_agent_reports.py."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_root_str = str(_ROOT)
if _root_str in sys.path:
    sys.path.remove(_root_str)
sys.path.insert(0, _root_str)

_TARGET = (
    Path(__file__).resolve().parent
    / "../../../../tellmesh/resource-agent-hypervisor/scripts/examples/audit_agent_reports.py"
).resolve()

if __name__ == "__main__":
    sys.argv[0] = str(_TARGET)
    runpy.run_path(str(_TARGET), run_name="__main__")

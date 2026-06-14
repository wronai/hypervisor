"""
Hypervisor command-line interface.

Usage:
    hypervisor --version
    hypervisor status
    hypervisor config
    hypervisor start
    hypervisor stop
"""

from __future__ import annotations

import argparse
import json
import sys

from ._version import __version__
from .config import get_config, load_config
from .core import Hypervisor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hypervisor",
        description="WronAI Hypervisor — AI desktop orchestration control plane",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--config", "-c", metavar="PATH", default=None,
        help="Path to nlp2uri.yaml / hypervisor config override"
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON where applicable"
    )

    sub = parser.add_subparsers(dest="command", required=False)

    # status
    p_status = sub.add_parser("status", help="Show hypervisor status")
    p_status.add_argument("--agents", action="store_true", help="Include registered agents")
    p_status.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    # config
    p_config = sub.add_parser("config", help="Inspect or dump configuration")
    p_config.add_argument("--show", action="store_true", default=True, help="Print effective config")
    p_config.add_argument("--path", action="store_true", help="Only print resolved config file path")
    p_config.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    # start / stop (stubs for now)
    sub.add_parser("start", help="Start the hypervisor (foreground stub)")
    sub.add_parser("stop", help="Stop the hypervisor")

    # agent management (future)
    p_agent = sub.add_parser("agent", help="Agent subcommands")
    p_agent.add_argument("action", choices=["list", "register"], help="Agent action")
    p_agent.add_argument("name", nargs="?", help="Agent name for register")

    args = parser.parse_args(argv)

    # Load config early for most commands
    cfg = load_config(args.config) if args.config else get_config()

    if args.command in (None, "status"):
        hv = Hypervisor(config=cfg)
        info = hv.status()
        if args.json:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(f"hypervisor {__version__}")
            print(f"  running : {info['running']}")
            print(f"  profile : {info['profile']}")
            print(f"  platform: {info.get('platform')}")
            print(f"  agents  : {len(info['registered_agents'])}/{info['max_agents']}")
            print(f"  config  : {info['config_path']}")
        return 0

    if args.command == "config":
        if args.path:
            print(cfg.get("_config_path", "<embedded-defaults>"))
            return 0
        if args.json:
            print(json.dumps(cfg, indent=2, ensure_ascii=False))
        else:
            # human friendly
            import yaml  # local import to avoid hard dep for --json path
            print(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True))
        return 0

    if args.command == "start":
        hv = Hypervisor(config=cfg)
        hv.start()
        # In real impl this would block on event loop / supervisor
        print("Hypervisor running. Press Ctrl+C to stop (stub).")
        try:
            # naive keep-alive for demo
            import time
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            hv.stop()
        return 0

    if args.command == "stop":
        hv = Hypervisor(config=cfg)
        hv.stop()
        return 0

    if args.command == "agent":
        hv = Hypervisor(config=cfg)
        if args.action == "list":
            print("Registered agents:")
            for a in hv.agents or ["(none)"]:
                print(f"  - {a}")
            return 0
        if args.action == "register" and args.name:
            try:
                hv.register_agent(args.name)
                print(f"Registered agent: {args.name}")
            except RuntimeError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            return 0
        parser.error("agent register requires <name>")
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

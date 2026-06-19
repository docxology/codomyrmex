#!/usr/bin/env python3
"""Print read-only Codex access status for Codomyrmex."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from codomyrmex.agents.codex.access import (
    codex_access_is_ready,
    get_codex_access_status,
    get_codex_dispatch_catalog,
)


def _print_text(payload: dict[str, Any]) -> None:
    print(f"Status: {payload.get('status')}")
    print(f"Repo: {payload.get('repo_root')}")
    if "surfaces" in payload:
        print("Surfaces:")
        for name, surface in payload["surfaces"].items():
            print(f"  {name}: {surface.get('status', 'unknown')}")
        dispatch = payload.get("dispatch", {})
    else:
        dispatch = payload
    summary = dispatch.get("summary", {})
    if summary:
        print("Dispatch:")
        print(f"  total: {summary.get('total')}")
        print(f"  available: {summary.get('available')}")
        print(f"  by_classification: {summary.get('by_classification')}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Codomyrmex Codex access probe"
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--dispatch-only",
        action="store_true",
        help="Only print the multiagent dispatch catalog",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit nonzero if any access surface is not ready",
    )
    args = parser.parse_args()

    payload = (
        get_codex_dispatch_catalog(REPO_ROOT)
        if args.dispatch_only
        else get_codex_access_status(REPO_ROOT)
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_text(payload)
    if args.check and not args.dispatch_only and not codex_access_is_ready(payload):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

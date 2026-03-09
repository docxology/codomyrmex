#!/usr/bin/env python3
"""Meta — Thin Script Orchestrator.

Introspects the meta-agents subpackage.

Usage:
    python scripts/agents/meta/run_meta.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("Meta — introspecting meta-agents...")

    try:
        import codomyrmex.agents.meta as meta_mod
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    exports = [n for n in dir(meta_mod) if not n.startswith("_")]
    print_success(f"Meta module: {len(exports)} exports")
    for name in exports[:10]:
        obj = getattr(meta_mod, name)
        print_info(f"  {name}: {type(obj).__name__}")
    print_success("Meta probe complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

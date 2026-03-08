#!/usr/bin/env python3
"""Every Code — Thin Script Orchestrator.

Probes the Every Code CLI wrapper and integration adapter.

Usage:
    python scripts/agents/every_code/run_every_code.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("Every Code — probing CLI wrapper...")

    try:
        from codomyrmex.agents.every_code import (
            EveryCodeClient,
            EveryCodeIntegrationAdapter,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    import shutil
    ec_bin = shutil.which("every-code") or shutil.which("everycode")
    if ec_bin:
        print_success(f"  every-code CLI found: {ec_bin}")
    else:
        print_info("  every-code CLI not found in PATH")

    client = EveryCodeClient()
    print_success(f"  EveryCodeClient: name={getattr(client, 'name', 'N/A')}")
    print_info(f"  Adapter: {EveryCodeIntegrationAdapter.__name__}")
    print_success("Every Code probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

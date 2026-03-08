#!/usr/bin/env python3
"""OpenClaw — Thin Script Orchestrator.

Probes the OpenClaw CLI wrapper.

Usage:
    python scripts/agents/openclaw/run_openclaw.py
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
    print_info("OpenClaw — probing CLI wrapper...")

    try:
        from codomyrmex.agents.openclaw import (
            OpenClawClient,
            OpenClawIntegrationAdapter,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    import shutil
    oc_bin = shutil.which("openclaw")
    if oc_bin:
        print_success(f"  openclaw CLI found: {oc_bin}")
    else:
        print_info("  openclaw CLI not found in PATH")

    client = OpenClawClient()
    print_success(f"  OpenClawClient: name={getattr(client, 'name', 'N/A')}")
    print_info(f"  Adapter: {OpenClawIntegrationAdapter.__name__}")
    print_success("OpenClaw probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

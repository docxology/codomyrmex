#!/usr/bin/env python3
"""Google Workspace — Thin Script Orchestrator.

Checks gws CLI installation and exercises the GoogleWorkspaceRunner wrapper.

Usage:
    python scripts/agents/google_workspace/run_google_workspace.py
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
    print_info("Google Workspace — probing gws CLI...")

    try:
        from codomyrmex.agents.google_workspace import (
            HAS_GWS,
            GoogleWorkspaceRunner,
            get_config,
            get_gws_version,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_info(f"  HAS_GWS: {HAS_GWS}")
    if HAS_GWS:
        version = get_gws_version()
        print_success(f"  gws version: {version}")
    else:
        print_info("  gws CLI not installed (npm install -g @googleworkspace/cli)")

    config = get_config()
    print_info(f"  Config: {config}")
    print_success("Google Workspace probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

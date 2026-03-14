#!/usr/bin/env python3
"""Mistral Vibe — Thin Script Orchestrator.

Probes the Mistral Vibe CLI wrapper.

Usage:
    python scripts/agents/mistral_vibe/run_mistral_vibe.py
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
    print_info("Mistral Vibe — probing CLI wrapper...")

    try:
        from codomyrmex.agents.mistral_vibe import (
            MistralVibeClient,
            MistralVibeIntegrationAdapter,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    import shutil

    mv_bin = shutil.which("mistral-vibe") or shutil.which("vibe")
    if mv_bin:
        print_success(f"  mistral-vibe CLI found: {mv_bin}")
    else:
        print_info("  mistral-vibe CLI not found in PATH")

    client = MistralVibeClient()
    print_success(f"  MistralVibeClient: name={getattr(client, 'name', 'N/A')}")
    print_info(f"  Adapter: {MistralVibeIntegrationAdapter.__name__}")
    print_success("Mistral Vibe probe complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

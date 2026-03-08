#!/usr/bin/env python3
"""Perplexity — Thin Script Orchestrator.

Probes the PerplexityClient and checks API key availability.

Usage:
    python scripts/agents/perplexity/run_perplexity.py
"""

import os
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
    print_info("Perplexity — probing client...")

    try:
        from codomyrmex.agents.perplexity import PerplexityClient, PerplexityError
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    has_key = bool(os.environ.get("PERPLEXITY_API_KEY"))
    print_info(f"  PERPLEXITY_API_KEY: {'set' if has_key else 'not set'}")
    print_info(f"  PerplexityClient: {PerplexityClient.__name__}")
    print_info(f"  PerplexityError: {PerplexityError.__name__}")
    print_success("Perplexity probe complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

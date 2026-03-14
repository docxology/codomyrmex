#!/usr/bin/env python3
"""agenticSeek — Thin Script Orchestrator.

Exercises the AgenticSeekClient configuration and plan validation.

Usage:
    python scripts/agents/agentic_seek/run_agentic_seek.py
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
    print_info("agenticSeek — probing client...")

    try:
        from codomyrmex.agents.agentic_seek import (
            SUPPORTED_LANGUAGES,
            AgenticSeekClient,
            AgenticSeekConfig,
            classify_language,
            validate_plan,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    print_success(f"Supported languages: {len(SUPPORTED_LANGUAGES)}")
    print_info(f"  Sample: {list(SUPPORTED_LANGUAGES)[:5]}")

    lang = classify_language("print('hello')")
    print_info(f"  classify_language('print(...)') = {lang}")

    config = AgenticSeekConfig()
    print_success(f"Config created: {config}")
    print_success("agenticSeek probe complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

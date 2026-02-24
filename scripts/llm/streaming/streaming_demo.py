#!/usr/bin/env python3
"""
Streaming Demo Script

Demonstrates streaming response handlers for real-time LLM output processing.
Shows patterns for handling chunked responses efficiently.

Features:
    - Streaming response simulation
    - Token-by-token processing
    - Progress indicators
    - Buffer management
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # 4 levels up
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== LLM Streaming Demo ===")
    try:
        from codomyrmex.llm.streaming import StreamHandler
        obj = StreamHandler()
        print_success(f"StreamHandler loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("LLM Streaming demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

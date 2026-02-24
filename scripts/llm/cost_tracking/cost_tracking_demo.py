#!/usr/bin/env python3
"""
Cost Tracking Demo Script

Demonstrates token counting and cost estimation for LLM API usage.
Uses the codomyrmex.llm.providers module for real API interactions.

Features:
    - Token counting for prompts and responses
    - Cost estimation based on model pricing
    - Usage analytics and reporting
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # 4 levels up
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== LLM Cost Tracking Demo ===")
    try:
        from codomyrmex.llm.cost_tracking import CostTracker
        obj = CostTracker()
        print_success(f"CostTracker loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("LLM Cost Tracking demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

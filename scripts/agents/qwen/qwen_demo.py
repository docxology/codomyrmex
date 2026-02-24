#!/usr/bin/env python3
"""
Qwen Demo Script

Demonstrates functionality of the qwen submodule.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== Qwen Agent Demo ===")
    try:
        from codomyrmex.agents.qwen import QwenClient
        obj = QwenClient()
        print_success(f"QwenClient loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("Qwen Agent demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

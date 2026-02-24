#!/usr/bin/env python3
"""
O1 Demo Script

Demonstrates functionality of the o1 submodule.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== O1 Agent Demo ===")
    try:
        from codomyrmex.agents.o1 import O1Client
        obj = O1Client()
        print_success(f"O1Client loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("O1 Agent demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

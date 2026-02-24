#!/usr/bin/env python3
"""
Agentic Memory Demo Script

Demonstrates functionality of the agentic_memory module.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent  # 3 levels up
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== Agentic Memory Demo ===")
    try:
        from codomyrmex.agentic_memory import AgentMemory
        obj = AgentMemory()
        print_success(f"AgentMemory loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("Agentic Memory demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

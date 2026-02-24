#!/usr/bin/env python3
"""
Audit Demo Script

Demonstrates functionality of the audit submodule.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # 4 levels up for submodules
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== DB Audit Demo ===")
    try:
        import codomyrmex.database_management.audit as audit
        print_success(f"audit module loaded: version={audit.__version__}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("DB Audit demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

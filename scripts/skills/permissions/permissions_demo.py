#!/usr/bin/env python3
"""
Permissions Demo Script

Demonstrates functionality of the permissions submodule.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # 4 levels up
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


def main() -> int:
    setup_logging()
    print_info("=== Skills Permissions Demo ===")
    try:
        from codomyrmex.skills.permissions import SkillPermissionManager
        obj = SkillPermissionManager()
        print_success(f"SkillPermissionManager loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("Skills Permissions demo complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

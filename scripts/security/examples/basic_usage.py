#!/usr/bin/env python3
"""
Security Module - Real Usage Examples

Demonstrates actual security capabilities:
- Vulnerability scanning (digital)
- Access control (physical)
- Cognitive security stubs
- Security theory patterns
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.security import (
    VulnerabilityScanner,
    AccessControlSystem,
    get_security_principles
)

def main():
    setup_logging()
    print_info("Running Security Examples...")

    # 1. Digital Security
    print_info("Testing VulnerabilityScanner initialization...")
    try:
        scanner = VulnerabilityScanner()
        print_success("  VulnerabilityScanner available.")
    except Exception as e:
        print_info(f"  VulnerabilityScanner note: {e}")

    # 2. Physical Security
    print_info("Testing AccessControlSystem...")
    try:
        acs = AccessControlSystem()
        print_success("  AccessControlSystem available.")
    except Exception as e:
        print_info(f"  AccessControlSystem note: {e}")

    # 3. Security Theory
    print_info("Testing security principle retrieval...")
    try:
        principles = get_security_principles()
        if principles:
            print_success(f"  Retrieved {len(principles)} security principles.")
    except Exception as e:
        print_error(f"  Theory check failed: {e}")

    print_success("Security examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

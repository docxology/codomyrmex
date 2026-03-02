#!/usr/bin/env python3
"""
System Discovery - Real Usage Examples

Demonstrates actual discovery capabilities:
- SystemDiscovery engine initialization
- Capability scanning stubs
- Status reporting stubs
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.system_discovery import (
    SystemDiscovery,
    CapabilityScanner,
    StatusReporter,
    get_system_context
)

def main():
    setup_logging()
    print_info("Running System Discovery Examples...")

    # 1. System Discovery Engine
    print_info("Initializing SystemDiscovery and scanning system...")
    try:
        discovery = SystemDiscovery()
        inventory = discovery.scan_system()
        print_success("  System scan completed.")
        
        # Show some stats from the real scan
        modules_count = len(inventory.get("modules", []))
        health = inventory.get("health_status", "Unknown")
        print_success(f"  Discovered {modules_count} modules.")
        print_success(f"  System health status: {health}")
        
    except Exception as e:
        print_error(f"  SystemDiscovery scan failed: {e}")

    # 2. Capability Scanner
    print_info("Initializing CapabilityScanner...")
    try:
        scanner = CapabilityScanner()
        print_success("  CapabilityScanner initialized successfully.")
    except Exception as e:
        print_error(f"  CapabilityScanner failed: {e}")

    # 3. Status Reporter
    print_info("Initializing StatusReporter...")
    try:
        reporter = StatusReporter()
        print_success("  StatusReporter initialized successfully.")
    except Exception as e:
        print_error(f"  StatusReporter failed: {e}")

    # 4. System Context
    print_info("Retrieving system context...")
    try:
        context = get_system_context()
        if context:
            print_success(f"  System context retrieved. Keys: {', '.join(context.keys())[:50]}...")
    except Exception as e:
        print_info(f"  System context demo: {e}")

    print_success("System discovery examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

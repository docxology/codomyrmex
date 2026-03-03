#!/usr/bin/env python3
"""
Module Health Check Script

Quick diagnostic script that checks the health of all Codomyrmex modules
by attempting to import them and reporting any issues.

Usage:
    python scripts/check_module_health.py
    python scripts/check_module_health.py --verbose
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    print_warning,
    setup_logging,
)

CORE_MODULES = [
    "codomyrmex.agents",
    "codomyrmex.api",
    "codomyrmex.auth",
    "codomyrmex.cache",
    "codomyrmex.cerebrum",
    "codomyrmex.coding",
    "codomyrmex.config_management",
    "codomyrmex.data_visualization",
    "codomyrmex.database_management",
    "codomyrmex.documentation",
    "codomyrmex.events",
    "codomyrmex.fpf",
    "codomyrmex.git_operations",
    "codomyrmex.llm",
    "codomyrmex.logging_monitoring",
    "codomyrmex.metrics",
    "codomyrmex.orchestrator",
    "codomyrmex.performance",
    "codomyrmex.security",
    "codomyrmex.serialization",
    "codomyrmex.static_analysis",
    "codomyrmex.utils",
    "codomyrmex.validation",
]


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "utils"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/utils/config.yaml")

    setup_logging()
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_info("Codomyrmex Module Health Check")
    print_info(f"Checking {len(CORE_MODULES)} core modules...")
    print()

    healthy = 0
    unhealthy = 0

    for module_name in CORE_MODULES:
        try:
            __import__(module_name)
            if verbose:
                print_success(f"  ✓ {module_name}")
            healthy += 1
        except ImportError as e:
            print_error(f"  ✗ {module_name}: {e}")
            unhealthy += 1
        except Exception as e:
            print_warning(f"  ⚠ {module_name}: {type(e).__name__}: {e}")
            unhealthy += 1

    print()
    print_info("Summary:")
    print(f"  Healthy: {healthy}/{len(CORE_MODULES)}")
    print(f"  Unhealthy: {unhealthy}/{len(CORE_MODULES)}")

    if unhealthy == 0:
        print_success("All modules healthy!")
        return 0
    else:
        print_error(f"{unhealthy} module(s) have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())

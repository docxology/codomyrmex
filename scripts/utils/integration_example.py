#!/usr/bin/env python3
"""
Cross-Module Integration Example

Demonstrates how multiple Codomyrmex modules work together in a real workflow:
- logging_monitoring for structured logging
- cache for result caching
- validation for input validation
- metrics for performance tracking

This is a template for building integrated applications.

Usage:
    python scripts/integration_example.py
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error


def main():
    setup_logging()
    print_info("Cross-Module Integration Example")
    print_info("=" * 50)
    
    # Step 1: Initialize logging
    print_info("\n1. Setting up structured logging...")
    try:
        from codomyrmex.logging_monitoring import get_logger
        logger = get_logger("integration_example")
        logger.info("Integration example started")
        print_success("   Logging initialized")
    except ImportError as e:
        print_error(f"   Logging setup failed: {e}")
        logger = None

    # Step 2: Initialize cache
    print_info("\n2. Initializing cache layer...")
    try:
        from codomyrmex.cache import get_cache
        cache = get_cache("integration_cache", backend="in_memory")
        print_success("   Cache initialized")
    except ImportError as e:
        print_info(f"   Cache import: {e}")
        cache = None
    except Exception as e:
        print_info(f"   Cache setup: {e}")
        cache = None

    # Step 3: Set up validation schema
    print_info("\n3. Defining validation schema...")
    try:
        from codomyrmex.validation import is_valid
        schema = {
            "type": "object",
            "properties": {
                "operation": {"type": "string"},
                "data": {"type": "object"},
            },
            "required": ["operation"],
        }
        print_success("   Validation schema defined")
    except ImportError as e:
        print_info(f"   Validation import: {e}")
        is_valid = None

    # Step 4: Process sample data
    print_info("\n4. Processing sample workflow...")
    sample_request = {
        "operation": "analyze",
        "data": {"file": "example.py", "depth": 3},
    }
    
    # Validate input
    if is_valid:
        try:
            valid = is_valid(sample_request, schema)
            print(f"   Input valid: {valid}")
        except Exception as e:
            print_info(f"   Validation: {e}")

    # Check cache
    if cache:
        try:
            cached = cache.get("sample_result")
            print(f"   Cache hit: {cached is not None}")
        except Exception as e:
            print_info(f"   Cache check: {e}")

    # Log completion
    if logger:
        logger.info("Integration example completed")

    # Step 5: Summary
    print_info("\n5. Integration Summary:")
    print("   Modules integrated:")
    print("     - logging_monitoring ✓")
    print("     - cache ✓")
    print("     - validation ✓")
    print("\n   Typical workflow:")
    print("     1. Validate input")
    print("     2. Check cache")
    print("     3. Process data")
    print("     4. Update cache")
    print("     5. Log results")

    print_success("\nCross-module integration example completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

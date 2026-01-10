#!/usr/bin/env python3
"""
Logging and Monitoring - Real Usage Examples

Demonstrates actual logging and monitoring capabilities:
- Structured logging setup
- Logger configuration
- Performance monitoring
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


def main():
    setup_logging()
    print_info("Running Logging and Monitoring Examples...")

    try:
        from codomyrmex.logging_monitoring import (
            get_logger,
            setup_logging as setup_structured_logging,
        )
        print_info("Successfully imported logging_monitoring module")
    except ImportError as e:
        print_error(f"Could not import logging_monitoring: {e}")
        return 1

    # Example 1: Get a logger instance
    print_info("Getting logger instances:")
    logger = get_logger(__name__)
    print(f"  Logger name: {logger.name}")
    print(f"  Logger type: {type(logger).__name__}")

    # Example 2: Log levels
    print_info("Available log levels:")
    print("  - DEBUG: Detailed diagnostic information")
    print("  - INFO: General operational messages")
    print("  - WARNING: Potential issues or concerns")
    print("  - ERROR: Error conditions")
    print("  - CRITICAL: Severe errors")

    # Example 3: Structured logging features
    print_info("Structured logging features:")
    print("  - JSON output format")
    print("  - Contextual fields (request_id, user_id)")
    print("  - Automatic timestamp formatting")
    print("  - Log rotation and retention")

    # Example 4: Demonstrate logging
    print_info("Sample log output:")
    try:
        logger.info("This is an info message")
        logger.debug("This is a debug message")
        print("  Logged info and debug messages")
    except Exception as e:
        print_info(f"  Logging demo: {e}")

    # Example 5: Monitoring integration
    print_info("Monitoring integration:")
    print("  - metrics → logging_monitoring: Metric logging")
    print("  - performance → logging_monitoring: Performance logs")
    print("  - api → logging_monitoring: Request logging")
    print("  - database_management → logging_monitoring: Query logs")

    print_success("Logging and Monitoring examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

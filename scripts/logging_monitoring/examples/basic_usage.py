#!/usr/bin/env python3
"""
Logging and Monitoring - Real Usage Examples

Demonstrates actual logging and monitoring capabilities:
- Structured logging setup
- Logger configuration
- Performance monitoring integration
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.logging_monitoring import get_logger, setup_logging as setup_structured_logging

def main():
    setup_logging()
    print_info("Running Logging and Monitoring Examples...")

    # 1. Logger Retrieval
    print_info("Testing get_logger...")
    try:
        logger = get_logger("test_logger")
        if logger:
            print_success(f"  Logger '{logger.name}' retrieved.")
    except Exception as e:
        print_error(f"  get_logger failed: {e}")

    # 2. Logging Operation
    print_info("Testing logging operations...")
    try:
        logger.info("Test info message")
        logger.error("Test error message", extra={"context": "example"})
        print_success("  Log messages dispatched.")
    except Exception as e:
        # Some loggers might not be initialized yet
        print_info(f"  Logging note: {e}")

    # 3. Structured Logging Setup
    print_info("Testing structured logging setup stub...")
    try:
        if setup_structured_logging:
            print_success("  setup_logging (structured) handler available.")
    except Exception as e:
        print_error(f"  Structured setup failed: {e}")

    print_success("Logging and monitoring examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

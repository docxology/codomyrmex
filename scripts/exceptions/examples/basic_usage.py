#!/usr/bin/env python3
"""
Exceptions Module - Real Usage Examples

Demonstrates actual exception capabilities:
- Custom exception types
- Exception context
- Exception chaining and formatting
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.exceptions import (
    CodomyrmexError,
    ConfigurationError,
    create_error_context,
    format_exception_chain,
)
from codomyrmex.utils.cli_helpers import print_info, print_success, setup_logging


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "exceptions"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/exceptions/config.yaml")

    setup_logging()
    print_info("Running Exception Examples...")

    # 1. Basic Exception
    print_info("Testing custom exception with context...")
    try:
        ctx = create_error_context(param="test", value=123)
        raise ConfigurationError("Missing setting", context=ctx)
    except ConfigurationError as e:
        print_success(f"  Caught expected exception: {e}")
        if "param=test" in str(e):
            print_success("  Exception context verified.")

    # 2. Exception Chaining
    print_info("Testing exception chaining and formatting...")
    try:
        try:
            raise ValueError("Root cause")
        except ValueError as cause:
            raise CodomyrmexError("Wrapper error") from cause
    except CodomyrmexError as e:
        chain = format_exception_chain(e)
        if "Root cause" in chain:
            print_success("  Exception chain formatting verified.")

    print_success("Exceptions examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

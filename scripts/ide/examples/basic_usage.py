#!/usr/bin/env python3
"""
IDE Integration - Real Usage Examples

Demonstrates actual IDE capabilities:
- IDEClient/CursorClient initialization
- Command and FileInfo models
- IDEStatus enumeration
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ide import CursorClient, FileInfo, IDECommand
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "ide" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/ide/config.yaml")

    setup_logging()
    print_info("Running IDE Integration Examples...")

    # 1. Cursor Client
    print_info("Testing CursorClient initialization...")
    try:
        client = CursorClient()
        print_success(f"  CursorClient initialized. Current Status: {client.status.value}")
    except Exception as e:
        print_error(f"  CursorClient failed: {e}")

    # 2. Command Models
    print_info("Testing IDE command and file models...")
    try:
        cmd = IDECommand(name="openFile", args={"path": "README.md"})
        print_success(f"  IDECommand instance created for: {cmd.name}")

        info = FileInfo(path="src/README.md", name="README.md", language="markdown")
        print_success(f"  FileInfo model instance created: {info.name}")
    except Exception as e:
        print_error(f"  Models check failed: {e}")

    print_success("IDE integration examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

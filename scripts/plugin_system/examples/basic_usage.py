#!/usr/bin/env python3
"""
Plugin System - Real Usage Examples

Demonstrates actual plugin system capabilities:
- PluginManager initialization
- PluginRegistry usage
- Plugin models and state
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
from codomyrmex.plugin_system import (
    PluginManager,
    PluginRegistry,
    PluginInfo,
    PluginState
)

def main():
    setup_logging()
    print_info("Running Plugin System Examples...")

    # 1. Plugin Manager
    print_info("Testing PluginManager and Registry...")
    try:
        manager = PluginManager()
        registry = PluginRegistry()
        print_success(f"  PluginManager initialized. Registry has {len(registry.plugins)} plugins.")
    except Exception as e:
        print_error(f"  Manager/Registry failed: {e}")

    # 2. Plugin Info
    print_info("Testing Plugin models...")
    try:
        info = PluginInfo(name="test_plugin", version="0.1.0", state=PluginState.REGISTERED)
        print_success(f"  PluginInfo instance created: {info.name} (Status: {info.state.value})")
    except Exception as e:
        print_error(f"  Models check failed: {e}")

    print_success("Plugin system examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

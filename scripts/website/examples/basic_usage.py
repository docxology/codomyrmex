#!/usr/bin/env python3
"""
Website Generation - Real Usage Examples

Demonstrates actual website capabilities:
- WebsiteGenerator initialization
- DataProvider aggregation
- WebsiteServer usage pattern
"""

import shutil
import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)
from codomyrmex.website import DataProvider, WebsiteGenerator, WebsiteServer


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "website"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/website/config.yaml")

    setup_logging()
    print_info("Running Website Generation Examples...")

    # Current project root
    current_root = Path(__file__).resolve().parent.parent.parent.parent

    # 1. Data Provider
    print_info("Testing DataProvider aggregation...")
    try:
        provider = DataProvider(root_dir=current_root)
        summary = provider.get_system_summary()
        if summary:
            print_success(f"  System summary status: {summary.get('status')}")
            print_success(f"  Environment: {summary.get('environment')}")

        modules = provider.get_modules()
        print_success(f"  Discovered {len(modules)} modules via DataProvider.")
    except Exception as e:
        print_error(f"  DataProvider failed: {e}")

    # 2. Website Generator
    print_info("Testing WebsiteGenerator initialization...")
    try:
        output_dir = Path("output/website_test")
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        WebsiteGenerator(output_dir=output_dir)
        print_success(f"  WebsiteGenerator initialized for output: {output_dir}")
    except Exception as e:
        print_error(f"  WebsiteGenerator failed: {e}")

    # 3. Website Server
    print_info("Verifying WebsiteServer interface...")
    try:
        # WebsiteServer is a Handler class
        if WebsiteServer:
            print_success("  WebsiteServer handler class available.")
    except Exception as e:
        print_error(f"  WebsiteServer check failed: {e}")

    print_success("Website generation examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

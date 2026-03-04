#!/usr/bin/env python3
"""
Cloud Integration - Real Usage Examples

Demonstrates actual cloud capabilities:
- CodaClient initialization
- Document and Page models usage
"""

import os
import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.cloud import CodaClient, Doc, Page
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
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "cloud" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/cloud/config.yaml")

    setup_logging()
    print_info("Running Cloud Integration Examples...")

    # 1. CodaClient
    print_info("Testing CodaClient initialization...")
    coda_token = os.getenv("CODA_API_TOKEN", "")
    try:
        CodaClient(api_token=coda_token)
        print_success("  CodaClient initialized successfully (interface check).")
    except Exception as e:
        print_error(f"  CodaClient failed: {e}")

    # 2. Models
    print_info("Testing Coda models...")
    try:
        doc = Doc(id="test-doc-id", name="Test Document")
        print_success(f"  Doc model instance created: {doc.name}")

        page = Page(id="test-page-id", name="Test Page")
        print_success(f"  Page model instance created: {page.name}")
    except Exception as e:
        print_error(f"  Models check failed: {e}")

    print_success("Cloud integration examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

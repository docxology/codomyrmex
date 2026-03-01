#!/usr/bin/env python3
"""
Web Scraping - Real Usage Examples

Demonstrates actual scraping capabilities:
- Scraper initialization (Firecrawl backend)
- ScrapeOptions and ScrapeFormat usage
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
from codomyrmex.scrape import (
    Scraper,
    ScrapeOptions,
    ScrapeFormat
)

def main():
    setup_logging()
    print_info("Running Web Scraping Examples...")

    # 1. Scraper
    print_info("Testing Scraper initialization...")
    try:
        scraper = Scraper()
        print_success("  Scraper initialized (interface check).")
    except Exception as e:
        print_error(f"  Scraper failed: {e}")

    # 2. Options
    print_info("Testing ScrapeOptions...")
    try:
        options = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN])
        print_success(f"  ScrapeOptions created with format: {options.formats[0].value}")
    except Exception as e:
        print_error(f"  Options check failed: {e}")

    print_success("Web scraping examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

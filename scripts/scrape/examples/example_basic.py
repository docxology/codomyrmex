#!/usr/bin/env python3
"""
Example: Scrape System - Basic Scraping Functionality

This example demonstrates the Codomyrmex scrape system.

CORE FUNCTIONALITY:
- Initialize Scraper with configuration
- Scrape a URL with options
- Handle results and errors

USAGE EXAMPLES:
    # Basic scrape
    from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat
    scraper = Scraper()
    result = scraper.scrape("https://example.com")
"""
import sys
from pathlib import Path

# Setup paths for importing Codomyrmex modules and shared utilities
root_dir = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))
sys.path.insert(0, str(root_dir / "scripts" / "tools" / "_common"))

# Import common utilities
try:
    from tools._common.config_loader import load_config
    from tools._common.example_runner import ExampleRunner
    from tools._common.utils import print_section, print_results, print_success, print_error
except ImportError:
    # Fallback - define minimal utilities inline
    def load_config(path):
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    
    def print_section(text):
        print(f"\n{'='*50}\n{text}\n{'='*50}")
    
    def print_results(data, title="Results"):
        import json
        print(f"\n{title}:")
        print(json.dumps(data, indent=2, default=str))
    
    def print_success(msg):
        print(f"✓ {msg}")
    
    def print_error(msg):
        print(f"✗ {msg}")
    
    class ExampleRunner:
        def __init__(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def validate_results(self, *args):
            pass
        def save_results(self, *args):
            pass
        def complete(self):
            pass
        def error(self, msg, e):
            print_error(f"{msg}: {e}")

# Import scrape module
try:
    from codomyrmex.scrape import Scraper, ScrapeOptions, ScrapeFormat
    SCRAPE_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Scrape module import warning: {e}")
    SCRAPE_AVAILABLE = False


def main():
    """Run the scrape system example."""
    print_section("Scrape System Example")
    print("Demonstrating scrape functionality")

    # Load configuration
    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        if not SCRAPE_AVAILABLE:
            print_error("Scrape module not available")
            operations_summary = {"scrape_available": False}
            print_results(operations_summary, "Operations Summary")
            runner.complete()
            return

        # Initialize scraper with test adapter for demo
        # In real usage, this would use Firecrawl with API key
        operations_summary = {
            "scrape_module_imported": True,
            "scraper_class_available": True,
            "scrape_options_available": True,
            "scrape_format_available": True,
        }

        # Demonstrate ScrapeOptions
        options = ScrapeOptions(
            formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML],
            timeout=30.0,
        )
        print_success(f"ScrapeOptions created: formats={[f.value for f in options.formats]}")
        operations_summary["options_created"] = True

        # Show available formats
        print("\nAvailable ScrapeFormat values:")
        for fmt in ScrapeFormat:
            print(f"  - {fmt.name}: {fmt.value}")
        operations_summary["formats_listed"] = True

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Scrape System example completed successfully!")
        print("\nNote: To actually scrape URLs, set FIRECRAWL_API_KEY and use:")
        print("  scraper = Scraper()")
        print('  result = scraper.scrape("https://example.com")')

    except Exception as e:
        runner.error("Scrape System example failed", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

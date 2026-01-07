#!/usr/bin/env python3
"""
Example: Networking System - Networking Functionality

This example demonstrates the Codomyrmex networking system.

CORE FUNCTIONALITY:
- networking operations

USAGE EXAMPLES:
    # Basic networking
    from codomyrmex.networking import HTTPClient, WebSocketClient
    instance = HTTPClient()
"""
import sys
from pathlib import Path

# Add src to path for importing Codomyrmex modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import common utilities
sys.path.insert(0, str(project_root / "examples" / "_common"))
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error

try:
    from codomyrmex.networking import HTTPClient, WebSocketClient
except ImportError:
    print("Module networking not yet fully implemented")

def main():
    """Run the networking system example."""
    print_section("Networking System Example")
    print("Demonstrating networking functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize httpclient
        instance = HTTPClient()
        print_success(f"✓ {instance.__class__.__name__} initialized")

        operations_summary = {
            "networking_initialized": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Networking System example completed successfully!")
    except Exception as e:
        runner.error("Networking System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

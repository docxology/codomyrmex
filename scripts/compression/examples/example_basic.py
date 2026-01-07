#!/usr/bin/env python3
"""
Example: Compression System - Compression Functionality

This example demonstrates the Codomyrmex compression system.

CORE FUNCTIONALITY:
- File compression
- Archive management
- Compression algorithms

USAGE EXAMPLES:
    # Basic compression
    from codomyrmex.compression import Compressor, ArchiveManager
    compressor = Compressor()
    result = compressor.compress("file.txt")
"""
import sys
from pathlib import Path

# Add src to path for importing Codomyrmex modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
# Setup paths
root_dir = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))

# Import common utilities
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error

from codomyrmex.compression import Compressor, ArchiveManager

def main():
    """Run the compression system example."""
    print_section("Compression System Example")
    print("Demonstrating compression functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize compressor
        compressor = Compressor()
        print_success("✓ Compressor initialized")

        # Initialize archive manager
        archive_manager = ArchiveManager()
        print_success("✓ Archive manager initialized")

        operations_summary = {
            "compressor_initialized": True,
            "archive_manager_initialized": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Compression System example completed successfully!")
    except Exception as e:
        runner.error("Compression System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()


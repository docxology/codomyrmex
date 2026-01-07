#!/usr/bin/env python3
"""
Example: Metrics System - Metrics Functionality

This example demonstrates the Codomyrmex metrics system.

CORE FUNCTIONALITY:
- metrics operations

USAGE EXAMPLES:
    # Basic metrics
    from codomyrmex.metrics import Metrics, Counter
    instance = Metrics()
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

try:
    from codomyrmex.metrics import Metrics, Counter
except ImportError:
    print("Module metrics not yet fully implemented")

def main():
    """Run the metrics system example."""
    print_section("Metrics System Example")
    print("Demonstrating metrics functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize metrics
        instance = Metrics()
        print_success(f"✓ {instance.__class__.__name__} initialized")

        operations_summary = {
            "metrics_initialized": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Metrics System example completed successfully!")
    except Exception as e:
        runner.error("Metrics System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

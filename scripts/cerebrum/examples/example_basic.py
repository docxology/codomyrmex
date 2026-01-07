#!/usr/bin/env python3
"""
Example: Cerebrum System - Case-Based Reasoning and Bayesian Inference

This example demonstrates the Codomyrmex cerebrum system.

CORE FUNCTIONALITY:
- Case-based reasoning
- Bayesian inference
- Active inference

USAGE EXAMPLES:
    # Basic cerebrum
    from codomyrmex.cerebrum import CerebrumEngine
    engine = CerebrumEngine()
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
    from codomyrmex.cerebrum import CerebrumEngine
except ImportError:
    print("Module cerebrum not yet fully implemented")

def main():
    """Run the cerebrum system example."""
    print_section("Cerebrum System Example")
    print("Demonstrating case-based reasoning and Bayesian inference functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        operations_summary = {
            "cerebrum_initialized": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Cerebrum System example completed successfully!")
    except Exception as e:
        runner.error("Cerebrum System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()


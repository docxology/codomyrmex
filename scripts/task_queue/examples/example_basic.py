#!/usr/bin/env python3
"""
Example: Task Queue System - Task Queue Functionality

This example demonstrates the Codomyrmex task queue system.

CORE FUNCTIONALITY:
- task queue operations

USAGE EXAMPLES:
    # Basic task_queue
    from codomyrmex.logistics.task import Queue, Job
    instance = Queue()
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
    from codomyrmex.logistics.task import Queue, Job
except ImportError:
    print("Module task_queue not yet fully implemented")

def main():
    """Run the task_queue system example."""
    print_section("Task Queue System Example")
    print("Demonstrating task queue functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize queue
        instance = Queue()
        print_success(f"✓ {instance.__class__.__name__} initialized")

        operations_summary = {
            "task_queue_initialized": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Task Queue System example completed successfully!")
    except Exception as e:
        runner.error("Task Queue System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

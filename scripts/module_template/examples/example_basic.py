#!/usr/bin/env python3
"""
Example: Module Template System - Module Template Functionality

This example demonstrates the Codomyrmex module template system.

CORE FUNCTIONALITY:
- module template operations

USAGE EXAMPLES:
    # Basic module_template
    from codomyrmex.module_template import ModuleGenerator
    instance = ModuleGenerator()
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
    from codomyrmex.module_template import ModuleGenerator
except ImportError:
    print("Module module_template not yet fully implemented")

def main():
    """Run the module_template system example."""
    print_section("Module Template System Example")
    print("Demonstrating module template functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize modulegenerator
        instance = ModuleGenerator()
        print_success(f"✓ {instance.__class__.__name__} initialized")

        operations_summary = {
            "module_template_initialized": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Module Template System example completed successfully!")
    except Exception as e:
        runner.error("Module Template System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

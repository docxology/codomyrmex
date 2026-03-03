#!/usr/bin/env python3
"""
scripts/demos/run_demos.py

Orchestrator script to run system demonstrations using the 'demos' module.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.demos.registry import get_registry
from codomyrmex.utils.cli_helpers import (
    format_table,
    print_error,
    print_info,
    print_section,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "demos" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    parser = argparse.ArgumentParser(description="Codomyrmex Demo Orchestrator")
    parser.add_argument("--list", action="store_true", help="List available demos")
    parser.add_argument("--module", help="Filter demos by module")
    parser.add_argument("--demo", help="Run a specific demo by name")
    parser.add_argument("--all", action="store_true", help="Run all discovered demos")

    args = parser.parse_args()
    setup_logging()

    registry = get_registry()

    # Discover scripts in the same directory
    demo_dir = Path(__file__).parent
    registry.discover_scripts(demo_dir)

    if args.list:
        demos = registry.list_demos(module=args.module)
        print_section("Available Demonstrations")
        table_data = [
            {"Name": d.name, "Module": d.module or "N/A", "Category": d.category, "Description": d.description}
            for d in demos
        ]
        print(format_table(table_data, ["Name", "Module", "Category", "Description"]))
        return

    if args.demo:
        print_info(f"Running demo: {args.demo}")
        result = registry.run_demo(args.demo)
        if result.success:
            print_success(f"Demo '{args.demo}' passed!")
            if result.output:
                print(f"Output:\n{result.output}")
        else:
            print_error(f"Demo '{args.demo}' failed: {result.error}")
            sys.exit(1)
    elif args.all:
        print_info("Running all discovered demos...")
        results = registry.run_all()

        print_section("Demo Execution Results")
        table_data = [
            {
                "Name": r.name,
                "Status": "✅ PASS" if r.success else "❌ FAIL",
                "Time": f"{r.execution_time:.2f}s",
                "Error": r.error or ""
            }
            for r in results
        ]
        print(format_table(table_data, ["Name", "Status", "Time", "Error"]))

        if any(not r.success for r in results):
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Workflow runner utility.

Run any workflow from the workflows directory with common options.

Usage:
    python run_workflow.py <workflow_name> [--verbose] [options...]

Examples:
    python run_workflow.py build_and_validate --verbose
    python run_workflow.py code_quality --fix
    python run_workflow.py module_health --module auth
    python run_workflow.py --list
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))  # Add for scripts package imports

from scripts.orchestrator.workflows import list_workflows, get_workflow


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run orchestration workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available workflows:
  analyze_and_report  - Full codebase analysis with HTML report
  build_and_validate  - Complete build pipeline with validation
  quick_test          - Fast parallel test runner
  module_health       - Module health check workflow
  dependency_check    - Check project dependencies
  code_quality        - Comprehensive code quality analysis
  deploy_preview      - Deploy to preview environment
  parallel_tests      - Run tests in parallel with coverage

Example:
  python run_workflow.py build_and_validate --verbose
  python run_workflow.py code_quality --fix
  python run_workflow.py --list
        """
    )

    parser.add_argument(
        "workflow",
        nargs="?",
        help="Workflow name to run"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available workflows"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be run without executing"
    )

    # Parse known args, pass rest to workflow
    args, remaining = parser.parse_known_args()

    # List workflows
    if args.list or not args.workflow:
        workflows = list_workflows()
        print("Available workflows:")
        print()
        for name, path in sorted(workflows.items()):
            print(f"  {name:20} - {path.name}")
        print()
        print("Run with: python run_workflow.py <workflow_name> [options]")
        return 0

    # Get workflow
    try:
        workflow_path = get_workflow(args.workflow)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    if not workflow_path.exists():
        print(f"Error: Workflow file not found: {workflow_path}")
        return 1

    # Build command
    cmd = ["python", str(workflow_path)]

    if args.verbose:
        cmd.append("--verbose")

    if args.dry_run:
        # Check if workflow supports dry-run
        if args.workflow in ["deploy_preview"]:
            cmd.append("--dry-run")

    # Add remaining arguments
    cmd.extend(remaining)

    if args.dry_run and args.workflow not in ["deploy_preview"]:
        print(f"Would run: {' '.join(cmd)}")
        return 0

    # Run workflow
    print(f"Running workflow: {args.workflow}")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

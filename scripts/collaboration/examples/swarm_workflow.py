#!/usr/bin/env python3
"""Advanced swarm workflow example for the collaboration module.

This script demonstrates coordinated multi-agent task execution using
SwarmManager with task decomposition and result aggregation.

Usage:
    python swarm_workflow.py [--agents N]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from codomyrmex.utils.cli_helpers import print_success, print_error, print_info
except ImportError:
    def print_success(msg): print(f"SUCCESS: {msg}")
    def print_error(msg): print(f"ERROR: {msg}")
    def print_info(msg): print(f"INFO: {msg}")


def main():
    """Demonstrate advanced swarm coordination workflow."""
    parser = argparse.ArgumentParser(description="Swarm coordination demo")
    parser.add_argument("--agents", type=int, default=3, help="Number of agents")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print_info("Collaboration Module - Swarm Workflow Example")
    print_info("=" * 50)

    try:
        from codomyrmex.collaboration import SwarmManager, TaskDecomposer
        print_success("Imported collaboration module")

        # Create swarm manager
        print_info(f"\n1. Initializing swarm with {args.agents} agents...")
        swarm = SwarmManager()

        # Create task decomposer
        print_info("\n2. Setting up task decomposer...")
        decomposer = TaskDecomposer()

        # Define a complex task
        complex_task = {
            "name": "code_review_workflow",
            "description": "Review and improve code quality",
            "subtasks": [
                "analyze_code_structure",
                "check_style_compliance",
                "identify_security_issues",
                "suggest_optimizations"
            ]
        }

        print_info(f"\n3. Task to decompose: {complex_task['name']}")
        print_info(f"   Description: {complex_task['description']}")
        print_info(f"   Subtasks: {len(complex_task['subtasks'])}")

        # Simulate task decomposition
        print_info("\n4. Decomposing task for parallel execution...")
        for i, subtask in enumerate(complex_task["subtasks"]):
            agent_id = i % args.agents
            if args.verbose:
                print_info(f"   Subtask '{subtask}' -> Agent {agent_id}")

        # Show coordination pattern
        print_info("\n5. Coordination patterns available:")
        print_info("   - Fan-out: Distribute subtasks to agents")
        print_info("   - Fan-in: Aggregate results")
        print_info("   - Pipeline: Sequential processing")
        print_info("   - Map-reduce: Parallel processing with aggregation")

        print_success("\nSwarm workflow demonstration complete!")
        return 0

    except ImportError as e:
        print_error(f"Failed to import collaboration module: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during demonstration: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

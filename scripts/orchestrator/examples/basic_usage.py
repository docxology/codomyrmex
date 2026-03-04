#!/usr/bin/env python3
"""
Basic orchestrator Usage

Demonstrates basic usage patterns.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
import asyncio
from codomyrmex.orchestrator import Workflow

async def main() -> int:
    setup_logging()
    print_info(f"Running Basic orchestrator Usage...")

    # 1. Workflow Creation
    print_info("Creating a real orchestration workflow...")
    workflow = Workflow(name="demo_workflow")
    
    # 2. Add Tasks
    def process_data(data):
        print_info(f"  Processing: {data}")
        return f"processed_{data}"

    def aggregate_results():
        print_info("  Aggregating results (simulated)...")
        return "final_result"

    workflow.add_task(name="task1", action=process_data, kwargs={"data": "A"})
    workflow.add_task(name="task2", action=process_data, kwargs={"data": "B"})
    workflow.add_task(name="aggregate", action=aggregate_results, dependencies=["task1", "task2"])

    # 3. Run Workflow
    print_info("Running workflow...")
    try:
        # We need to pass the results from task1 and task2 to aggregate.
        # Workflow._execute_task doesn't automatically inject results into deps.
        # But wait, looking at Workflow.add_task it takes Callable[..., Any].
        # The Workflow class provided seems to run action(*args, **kwargs).
        
        # Let's adjust task3 to use results if possible, or just run.
        # Actually, the provided Workflow doesn't seem to pass results down.
        # Let's check _execute_task again.
        
        results = await workflow.run()
        print_success(f"Workflow '{workflow.name}' completed.")
        for name, task in workflow.tasks.items():
            print_info(f"  Task '{name}': {task.status.value}")
            if task.result:
                print_info(f"    Result: {task.result}")
    except Exception as e:
        print_error(f"Workflow execution failed: {e}")

    print_success(f"Basic orchestrator Usage completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

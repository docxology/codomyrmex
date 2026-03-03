#!/usr/bin/env python3
"""
Logistics - Real Usage Examples

Demonstrates actual logistics capabilities:
- Workflow management (WorkflowManager)
- Task/Job queuing (Queue, Job)
- Scheduling (ScheduleManager)
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.logistics import Job, Queue, ScheduleManager, WorkflowManager
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "logistics"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/logistics/config.yaml")

    setup_logging()
    print_info("Running Logistics Examples...")

    # 1. Workflow Manager
    print_info("Testing WorkflowManager...")
    try:
        WorkflowManager()
        print_success("  WorkflowManager initialized successfully.")
    except Exception as e:
        print_error(f"  WorkflowManager failed: {e}")

    # 2. Task Queue & Jobs
    print_info("Testing Task Queue and Jobs...")
    try:
        queue = Queue(backend="in_memory")
        job = Job(task="echo 'Hello'")
        job_id = queue.enqueue(job)
        stats = queue.get_stats()
        if stats.get("queue_length", 0) > 0:
            print_success(f"  Job '{job_id}' enqueued successfully.")
    except Exception as e:
        print_error(f"  Task queue failed: {e}")

    # 3. Scheduling
    print_info("Testing ScheduleManager...")
    try:
        ScheduleManager()
        print_success("  ScheduleManager initialized successfully.")
    except Exception as e:
        print_error(f"  ScheduleManager failed: {e}")

    print_success("Logistics examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

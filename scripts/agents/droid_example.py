#!/usr/bin/env python3
"""
Droid Controller Example

Demonstrates usage of DroidController for managed task execution.
"""
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import DroidController
from codomyrmex.agents.droid import DroidConfig, DroidMode
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def sample_task(data: dict) -> str:
    """A sample task that the droid will execute."""
    return f"Processed: {data.get('message', 'no message')}"


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "agents" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/agents/config.yaml")

    setup_logging()
    print_info("Initializing Droid Controller...")

    # Create custom config
    config = DroidConfig(
        identifier="example_droid",
        mode=DroidMode.DEVELOPMENT,
        max_parallel_tasks=2,
    )

    controller = DroidController(config)
    controller.start()

    print_info(f"Droid Status: {controller.status.value}")

    # Execute a task through the droid
    print_info("Executing task through Droid...")
    try:
        result = controller.execute_task(
            operation_id="sample_operation",
            handler=sample_task,
            data={"message": "Hello from Droid!"}
        )
        print_success(f"Task Result: {result}")
    except Exception as e:
        print_error(f"Droid Error: {e}")
        return 1
    finally:
        controller.stop()
        print_info(f"Final Droid Metrics: {controller.metrics}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

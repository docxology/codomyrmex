#!/usr/bin/env python3
"""
OpenCode Agent Example

Demonstrates basic usage of OpenCodeClient for CLI-based code operations.
This script handles gracefully when OpenCode CLI is not installed.
"""
import os
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import AgentRequest, OpenCodeClient
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    print_warning,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "agents" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/agents/config.yaml")

    setup_logging()
    print_info("Initializing OpenCode Agent...")

    client = OpenCodeClient()

    if not client.test_connection():
        print_warning("OpenCode CLI not available. Skipping execution.")
        print_info("To use: ensure OpenCode CLI is installed and in PATH")
        return 0  # Exit gracefully - this is expected for demo scripts

    if os.getenv("CODOMYRMEX_TEST_MODE") == "1":
        print_info("Test mode enabled: skipping resource-intensive execution.")
        return 0

    # Execute a simple request
    request = AgentRequest(
        prompt="Create a Python function to validate email addresses",
        context={"language": "python"},
    )

    print_info("Sending request to OpenCode...")
    response = client.execute(request)

    if response.is_success():
        print_success("OpenCode Response:")
        print(response.content)
    else:
        print_error(f"OpenCode Error: {response.error}")
        # Return 0 for demo purposes even on operational failure (like missing auth)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

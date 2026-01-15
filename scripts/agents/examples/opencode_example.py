#!/usr/bin/env python3
"""
OpenCode Agent Example

Demonstrates basic usage of OpenCodeClient for CLI-based code operations.
This script handles gracefully when OpenCode CLI is not installed.
"""
import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import OpenCodeClient, AgentRequest
from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_error, print_info, print_warning


def main():
    setup_logging()
    print_info("Initializing OpenCode Agent...")

    client = OpenCodeClient()
    
    # Test connection - gracefully handle when CLI not available
    if not client.test_connection():
        print_warning("OpenCode CLI not available. Skipping execution.")
        print_info("To use: ensure OpenCode CLI is installed and in PATH")
        return 0  # Exit gracefully - this is expected for demo scripts

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
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

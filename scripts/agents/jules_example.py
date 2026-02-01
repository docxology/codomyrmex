#!/usr/bin/env python3
"""
Jules Agent Example

Demonstrates basic usage of JulesClient for CLI-based code operations.
This script handles gracefully when Jules CLI is not installed.
"""
import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import JulesClient, AgentRequest
from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_error, print_info, print_warning


def main():
    setup_logging()
    print_info("Initializing Jules Agent...")

    client = JulesClient()
    
    # Test connection - gracefully handle when CLI not available
    if not client.test_connection():
        print_warning("Jules CLI not available. Skipping execution.")
        print_info("To use: ensure Jules CLI is installed and in PATH")
        return 0  # Exit gracefully - this is expected for demo scripts

    # Execute a simple request
    request = AgentRequest(
        prompt="Create a simple Python hello world function",
        context={"language": "python"},
    )

    print_info("Sending request to Jules...")
    response = client.execute(request)

    if response.is_success():
        print_success("Jules Response:")
        print(response.content)
    else:
        print_error(f"Jules Error: {response.error}")
        # Return 0 for demo purposes even on operational failure (like missing auth)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

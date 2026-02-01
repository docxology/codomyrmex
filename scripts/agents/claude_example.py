#!/usr/bin/env python3
"""
Claude Agent Example

Demonstrates basic usage of ClaudeClient for API-based code generation.
This script handles gracefully when Claude API is not configured.
"""
import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import ClaudeClient, AgentRequest
from codomyrmex.agents.exceptions import AgentConfigurationError
from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_error, print_info, print_warning


def main():
    setup_logging()
    print_info("Initializing Claude Agent...")

    # Gracefully handle when API key is not configured
    try:
        client = ClaudeClient()
    except AgentConfigurationError as e:
        print_warning(f"Claude not configured: {e}")
        print_info("To configure: set ANTHROPIC_API_KEY environment variable")
        return 0  # Exit gracefully - this is expected for demo scripts
    
    # Test connection
    if not client.test_connection():
        print_warning("Claude connection test failed. Check API key.")
        return 0

    # Execute a simple request
    request = AgentRequest(
        prompt="Write a Python function that calculates the factorial of a number.",
        context={"language": "python"},
    )

    print_info("Sending request to Claude...")
    response = client.execute(request)

    if response.is_success():
        print_success("Claude Response:")
        print(response.content)
    else:
        print_error(f"Claude Error: {response.error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

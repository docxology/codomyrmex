#!/usr/bin/env python3
"""
Codex Agent Example

Demonstrates basic usage of CodexClient for OpenAI API-based code generation.
This script handles gracefully when OpenAI API is not configured.
"""
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import CodexClient, AgentRequest
from codomyrmex.agents.exceptions import AgentConfigurationError, AgentError
from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_error, print_info, print_warning


def main():
    setup_logging()
    print_info("Initializing Codex Agent...")

    # Gracefully handle when API key is not configured
    try:
        client = CodexClient()
    except (AgentConfigurationError, Exception) as e:
        print_warning(f"Codex not configured: {e}")
        print_info("To configure: set OPENAI_API_KEY environment variable")
        return 0  # Exit gracefully - this is expected for demo scripts
    
    # Test connection - wrap in try/except for safety
    try:
        if not client.test_connection():
            print_warning("Codex connection test failed. Check API key.")
            return 0
    except Exception as e:
        print_warning(f"Codex connection test error: {e}")
        print_info("To configure: set OPENAI_API_KEY environment variable")
        return 0

    # Execute a simple request
    request = AgentRequest(
        prompt="Write a Python function that checks if a number is prime.",
        context={"language": "python"},
    )

    print_info("Sending request to Codex...")
    try:
        response = client.execute(request)
    except (AgentError, Exception) as e:
        print_warning(f"Codex execution error: {e}")
        return 0

    if response.is_success():
        print_success("Codex Response:")
        print(response.content)
    else:
        print_error(f"Codex Error: {response.error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

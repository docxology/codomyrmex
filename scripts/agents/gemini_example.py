#!/usr/bin/env python3
"""
Gemini Agent Example

Demonstrates basic usage of GeminiClient for Google API-based code generation.
This script handles gracefully when Gemini API is not configured.
"""
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import GeminiClient, AgentRequest
from codomyrmex.agents.exceptions import AgentConfigurationError, AgentError, GeminiError
from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_error, print_info, print_warning


def is_config_error(error_msg: str) -> bool:
    """Check if error message indicates a configuration/initialization issue."""
    error_lower = str(error_msg).lower()
    config_indicators = ["not initialized", "not configured", "api", "key", "missing"]
    return any(indicator in error_lower for indicator in config_indicators)


def main():
    setup_logging()
    print_info("Initializing Gemini Agent...")

    # Gracefully handle when API key is not configured
    try:
        client = GeminiClient()
    except (AgentConfigurationError, Exception) as e:
        print_warning(f"Gemini not configured: {e}")
        print_info("To configure: set GEMINI_API_KEY environment variable")
        return 0  # Exit gracefully - this is expected for demo scripts
    
    # Test connection - wrap in try/except for safety
    try:
        if not client.test_connection():
            print_warning("Gemini connection test failed. Check API key.")
            return 0
    except Exception as e:
        print_warning(f"Gemini connection test error: {e}")
        print_info("To configure: set GEMINI_API_KEY environment variable")
        return 0

    # Execute a simple request
    request = AgentRequest(
        prompt="Write a Python function that sorts a list using quicksort.",
        context={"language": "python"},
    )

    print_info("Sending request to Gemini...")
    try:
        response = client.execute(request)
    except (AgentError, GeminiError, Exception) as e:
        if is_config_error(str(e)):
            print_warning(f"Gemini not configured: {e}")
            print_info("To configure: set GEMINI_API_KEY environment variable")
            return 0
        else:
            print_error(f"Gemini Error: {e}")
            return 1

    if response.is_success():
        print_success("Gemini Response:")
        print(response.content)
    else:
        # Check if error is configuration-related
        if is_config_error(response.error):
            print_warning(f"Gemini not configured: {response.error}")
            print_info("To configure: set GEMINI_API_KEY environment variable")
            return 0
        else:
            print_error(f"Gemini Error: {response.error}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

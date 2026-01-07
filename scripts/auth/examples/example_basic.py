#!/usr/bin/env python3
"""
Example: Auth System - Authentication and Authorization

This example demonstrates the Codomyrmex authentication and authorization system.

CORE FUNCTIONALITY:
- API key management and rotation
- Token generation and validation
- Authentication methods
- Authorization checks

USAGE EXAMPLES:
    # Basic authentication
    from codomyrmex.auth import Authenticator, APIKeyManager
    authenticator = Authenticator()
    result = authenticator.authenticate(api_key="your_key_here")
"""
import sys
from pathlib import Path

# Add src to path for importing Codomyrmex modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
# Setup paths
root_dir = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))

# Import common utilities
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error

from codomyrmex.auth import Authenticator, APIKeyManager, Token

def main():
    """Run the auth system example."""
    print_section("Auth System Example")
    print("Demonstrating authentication and authorization functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize authenticator
        authenticator = Authenticator()
        print_success("✓ Authenticator initialized")

        # Initialize API key manager
        api_key_manager = APIKeyManager()
        print_success("✓ API key manager initialized")

        operations_summary = {
            "authenticator_initialized": True,
            "api_key_manager_initialized": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Auth System example completed successfully!")
    except Exception as e:
        runner.error("Auth System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()


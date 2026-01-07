#!/usr/bin/env python3
"""
Example: Encryption System - Encryption Functionality

This example demonstrates the Codomyrmex encryption system.

CORE FUNCTIONALITY:
- encryption operations

USAGE EXAMPLES:
    # Basic encryption
    from codomyrmex.encryption import Encryptor, KeyManager
    instance = Encryptor()
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

try:
    from codomyrmex.encryption import Encryptor, KeyManager
except ImportError:
    print("Module encryption not yet fully implemented")

def main():
    """Run the encryption system example."""
    print_section("Encryption System Example")
    print("Demonstrating encryption functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize encryptor
        instance = Encryptor()
        print_success(f"✓ {instance.__class__.__name__} initialized")

        operations_summary = {
            "encryption_initialized": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Encryption System example completed successfully!")
    except Exception as e:
        runner.error("Encryption System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Orchestrator for environment_setup.

Demonstrates the use of the environment_setup module for validating
the runtime environment, checking dependencies, and loading configuration.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.environment_setup import (
    check_and_setup_env_vars,
    generate_environment_report,
    is_uv_available,
    validate_environment,
)


def run_orchestration():
    """Main orchestration loop for environment setup."""
    print("--- Codomyrmex Environment Orchestration ---")

    # 1. Report current state
    print("\n[Step 1] System Status Report:")
    report = generate_environment_report()
    print(report)

    # 2. Check for .env and required vars
    print("\n[Step 2] Loading Environment Variables:")
    missing = check_and_setup_env_vars(
        repo_root=str(project_root),
        required=["OPENAI_API_KEY", "ANTHROPIC_API_KEY"],
        optional=["LOG_LEVEL", "DEBUG"]
    )
    if missing:
        print(f"Warning: Missing required environment variables: {missing}")
    else:
        print("Success: All required environment variables are present.")

    # 3. Comprehensive validation
    print("\n[Step 3] Environment Validation:")
    val_report = validate_environment(min_python="3.11")
    if val_report.valid:
        print("Success: Environment validation passed.")
    else:
        print(f"Error: Environment validation failed: {val_report.missing_items}")

    # 4. uv Check
    print("\n[Step 4] Package Manager Check:")
    if is_uv_available():
        print("uv is available for fast package management.")
    else:
        print("uv is not found. Falling back to pip for installations.")

    print("\n--- Orchestration Complete ---")
    return val_report.valid



    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "environment_setup" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/environment_setup/config.yaml")

if __name__ == "__main__":
    success = run_orchestration()
    sys.exit(0 if success else 1)

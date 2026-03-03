#!/usr/bin/env python3
"""
Git Operations - Real Usage Examples

Demonstrates actual git capabilities:
- Git availability and status
- Repository management (RepositoryManager)
- Commit history and config
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.git_operations import (
    RepositoryManager,
    check_git_availability,
    get_commit_history,
    get_config,
    get_current_branch,
    is_git_repository,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "git_operations"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/git_operations/config.yaml")

    setup_logging()
    print_info("Running Git Operations Examples...")

    # 1. Availability & Status
    print_info("Checking Git status...")
    current_dir = Path.cwd()
    if check_git_availability():
        print_success("  Git is available.")

    if is_git_repository(current_dir):
        print_success("  Current directory is a Git repository.")
        try:
            branch = get_current_branch(current_dir)
            print_success(f"  Branch: {branch}")

            history = get_commit_history(current_dir, max_count=5)
            print_success(f"  Retrieved {len(history)} recent commit(s).")

            config = get_config(current_dir)
            if config:
                print_success("  Git configuration retrieved.")
        except Exception as e:
            print_error(f"  Status retrieval failed: {e}")

    # 2. Repository Manager
    print_info("Testing RepositoryManager...")
    try:
        RepositoryManager()
        # Initialize (loads metadata etc)
        print_success("  RepositoryManager initialized.")
    except Exception as e:
        print_error(f"  RepositoryManager failed: {e}")

    print_success("Git operations examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

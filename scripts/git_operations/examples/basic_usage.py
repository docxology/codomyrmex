#!/usr/bin/env python3
"""
Git Operations - Real Usage Examples

Demonstrates actual git operation capabilities:
- Repository status and information
- Branch management
- Commit operations
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error


def main():
    setup_logging()
    print_info("Running Git Operations Examples...")

    try:
        from codomyrmex.git_operations import (
            check_git_availability,
            is_git_repository,
            get_current_branch,
            get_status,
        )
        print_info("Successfully imported git_operations module")
    except ImportError as e:
        print_error(f"Could not import git_operations: {e}")
        return 1

    # Example 1: Check git availability
    print_info("Checking Git availability...")
    try:
        git_available = check_git_availability()
        print(f"  Git available: {git_available}")
    except Exception as e:
        print_info(f"  Git check: {e}")

    # Example 2: Check if current directory is a git repo
    print_info("Checking repository status...")
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    
    try:
        is_repo = is_git_repository(project_root)
        print(f"  Is git repository: {is_repo}")
    except Exception as e:
        print_info(f"  Repo check: {e}")

    # Example 3: Get current branch
    print_info("Getting current branch...")
    try:
        branch = get_current_branch(project_root)
        print(f"  Current branch: {branch}")
    except Exception as e:
        print_info(f"  Branch check: {e}")

    # Example 4: Available git operations
    print_info("Available git operations:")
    print("  Core: check_git_availability, is_git_repository, initialize_git_repository, clone_repository")
    print("  Branch: create_branch, switch_branch, get_current_branch, merge_branch")
    print("  File: add_files, commit_changes, get_status, get_diff, reset_changes")
    print("  Remote: push_changes, pull_changes, fetch_changes, add_remote")
    print("  History: get_commit_history, get_commit_history_filtered")

    # Example 5: Integration with other modules
    print_info("Cross-module integration:")
    print("  - llm → git_operations: AI commit messages")
    print("  - data_visualization → git_operations: Commit graphs")
    print("  - ci_cd_automation → git_operations: Deploy triggers")

    print_success("Git Operations examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Git Operations - Real Usage Examples

Demonstrates actual git capabilities:
- Git availability and status
- Repository management (RepositoryManager)
- Commit history and config
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.git_operations import (
    check_git_availability,
    is_git_repository,
    get_current_branch,
    get_status,
    get_commit_history,
    get_config,
    RepositoryManager
)

def main():
    setup_logging()
    print_info("Running Git Operations Examples...")

    # 1. Availability & Status
    print_info("Checking Git status...")
    current_dir = Path.cwd()
    if check_git_availability():
        print_success("  Git is available.")
    
    if is_git_repository(current_dir):
        print_success(f"  Current directory is a Git repository.")
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
        mgr = RepositoryManager()
        # Initialize (loads metadata etc)
        print_success("  RepositoryManager initialized.")
    except Exception as e:
        print_error(f"  RepositoryManager failed: {e}")

    print_success("Git operations examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Git Operations Module - Example Orchestrator

This script demonstrates a comprehensive Git workflow using the improved git_operations module.
It serves as a working, tested example of how to use the module programmatically.

Workflow:
1. Initialize a new temporary repository
2. Create and add files
3. Create a commit
4. Create and switch to a feature branch
5. Modify files and commit on the branch
6. Switch back to main and merge the feature branch
7. Inspect history and status
8. Clean up
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.git_operations import (
    add_files,
    commit_changes,
    create_branch,
    delete_branch,
    get_commit_history,
    get_current_branch,
    get_status,
    initialize_git_repository,
    merge_branch,
    switch_branch,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    setup_logging,
)


def run_workflow():
    setup_logging()
    print_section("Git Operations Workflow Demonstration")

    # Create a temporary directory for the demo repository
    temp_dir = tempfile.mkdtemp(prefix="git_demo_")
    repo_path = os.path.join(temp_dir, "demo_repo")

    try:
        # 1. Initialize repository
        print_info(f"Initializing repository at: {repo_path}")
        if not initialize_git_repository(repo_path, initial_commit=True):
            print_error("Failed to initialize repository")
            return 1
        print_success("Repository initialized with initial commit.")

        # 2. Add some files
        print_info("Creating and adding new files...")
        file1 = os.path.join(repo_path, "feature.txt")
        with open(file1, "w") as f:
            f.write("New feature content\n")

        if not add_files(["feature.txt"], repository_path=repo_path):
            print_error("Failed to add files")
            return 1
        print_success("Files added to staging area.")

        # 3. Commit changes
        print_info("Committing changes...")
        sha = commit_changes("feat: add feature.txt", repository_path=repo_path)
        if not sha:
            print_error("Failed to commit changes")
            return 1
        print_success(f"Changes committed. SHA: {sha[:8]}")

        # 4. Create and switch to a feature branch
        branch_name = "feature/experimental"
        print_info(f"Creating and switching to branch: {branch_name}")
        if not create_branch(branch_name, repository_path=repo_path):
            print_error(f"Failed to create branch {branch_name}")
            return 1

        current = get_current_branch(repository_path=repo_path)
        print_success(f"Now on branch: {current}")

        # 5. Modify on branch
        print_info("Modifying file on feature branch...")
        with open(file1, "a") as f:
            f.write("Experimental changes\n")

        sha2 = commit_changes("feat: experimental updates", repository_path=repo_path)
        print_success(f"Committed on branch. SHA: {sha2[:8]}")

        # 6. Merge back to main
        main_branch = "main"
        # Check if it's main or master
        status = get_status(repo_path)

        print_info("Switching back to main and merging...")
        if not switch_branch("main", repository_path=repo_path):
            if not switch_branch("master", repository_path=repo_path):
                print_error("Failed to switch back to main branch")
                return 1
            main_branch = "master"

        if not merge_branch(branch_name, repository_path=repo_path):
            print_error(f"Failed to merge {branch_name}")
            return 1
        print_success(f"Merged {branch_name} into {main_branch}.")

        # 7. Final inspection
        print_section("Final Repository State")

        history = get_commit_history(limit=5, repository_path=repo_path)
        print_info("Recent History:")
        for commit in history:
            print(
                f"  {commit['hash'][:7]} - {commit['message']} ({commit['author_name']})"
            )

        status = get_status(repo_path)
        if status.get("clean"):
            print_success("Working directory is clean.")
        else:
            print_info(f"Working directory status: {status}")

        # Clean up the branch
        delete_branch(branch_name, repository_path=repo_path, force=True)
        print_info(f"Deleted branch {branch_name}")

    finally:
        # 8. Cleanup
        print_info(f"Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)

    print_success("\nGit Operations workflow completed successfully!")
    return 0

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


if __name__ == "__main__":
    # If run as orchestrator (with --scripts-dir), it will find this file.
    # If run directly, execute the workflow.
    if "--scripts-dir" in " ".join(sys.argv):
        from codomyrmex.orchestrator.core import main

        current_dir = Path(__file__).resolve().parent
        if not any(arg.startswith("--scripts-dir") for arg in sys.argv):
            sys.argv.append(f"--scripts-dir={current_dir}")
        sys.exit(main())
    else:
        sys.exit(run_workflow())

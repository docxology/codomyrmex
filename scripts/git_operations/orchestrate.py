#!/usr/bin/env python3
"""
Git Operations Orchestrator

Thin orchestrator script providing CLI access to git_operations module functionality.
Calls actual module functions from codomyrmex.git_operations.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import GitOperationError, RepositoryError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        validate_file_path,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions
from codomyrmex.git_operations import (
    add_files,
    check_git_availability,
    clone_repository,
    commit_changes,
    create_branch,
    get_current_branch,
    get_status,
    get_commit_history,
    initialize_git_repository,
    is_git_repository,
    push_changes,
    pull_changes,
    switch_branch,
)

logger = get_logger(__name__)


def handle_status(args):
    """Handle git status command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Getting git status")

        status = get_status()
        print_section("Git Status")
        print(format_output(status, format_type="json"))
        print_section("", separator="")
        return True

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error getting git status")
        print_error("Unexpected error getting git status", exception=e)
        return False


def handle_branch(args):
    """Handle branch operations."""
    try:
        if args.action == "current":
            branch = get_current_branch()
            print_success(f"Current branch: {branch}")
            return True
        elif args.action == "create":
            if getattr(args, "dry_run", False):
                print_info(f"Dry run: Would create branch: {args.name}")
                return True
            result = create_branch(args.name)
            if result:
                print_success(f"Created branch: {args.name}")
                return True
            else:
                print_error("Failed to create branch", context=args.name)
                return False
        elif args.action == "switch":
            if getattr(args, "dry_run", False):
                print_info(f"Dry run: Would switch to branch: {args.name}")
                return True
            result = switch_branch(args.name)
            if result:
                print_success(f"Switched to branch: {args.name}")
                return True
            else:
                print_error("Failed to switch to branch", context=args.name)
                return False

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during branch operation")
        print_error("Unexpected error during branch operation", exception=e)
        return False


def handle_commit(args):
    """Handle commit command."""
    try:
        files = args.files if args.files else []
        
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would commit with message: {args.message}")
            if files:
                print_info(f"Files: {', '.join(files)}")
            return True

        if getattr(args, "verbose", False):
            logger.info(f"Committing with message: {args.message}")
            if files:
                logger.info(f"Files: {', '.join(files)}")

        result = commit_changes(message=args.message, files=files)

        if result:
            print_success(f"Committed changes: {args.message}")
            return True
        else:
            print_error("Failed to commit changes")
            return False

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during commit")
        print_error("Unexpected error during commit", exception=e)
        return False


def handle_add(args):
    """Handle add files command."""
    try:
        files = args.files if args.files else []
        
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would add files: {', '.join(files) if files else 'all'}")
            return True

        result = add_files(files)

        if result:
            print_success(f"Added files: {', '.join(files) if files else 'all'}")
            return True
        else:
            print_error("Failed to add files")
            return False

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during add")
        print_error("Unexpected error during add", exception=e)
        return False


def handle_push(args):
    """Handle push command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would push to {args.remote}/{args.branch}")
            if args.force:
                print_info("Force push would be used")
            return True

        result = push_changes(
            branch=args.branch, remote=args.remote, force=args.force
        )

        if result:
            print_success(f"Pushed changes to {args.remote}/{args.branch}")
            return True
        else:
            print_error("Failed to push changes")
            return False

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during push")
        print_error("Unexpected error during push", exception=e)
        return False


def handle_pull(args):
    """Handle pull command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would pull from {args.remote}/{args.branch}")
            return True

        result = pull_changes(remote=args.remote, branch=args.branch)

        if result:
            print_success(f"Pulled changes from {args.remote}/{args.branch}")
            return True
        else:
            print_error("Failed to pull changes")
            return False

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during pull")
        print_error("Unexpected error during pull", exception=e)
        return False


def handle_clone(args):
    """Handle clone command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would clone {args.url} to {args.destination}")
            if args.branch:
                print_info(f"Branch: {args.branch}")
            return True

        if getattr(args, "verbose", False):
            logger.info(f"Cloning {args.url} to {args.destination}")

        result = clone_repository(
            url=args.url, destination=args.destination, branch=args.branch
        )

        if result:
            print_success(f"Cloned repository to {args.destination}")
            return True
        else:
            print_error("Failed to clone repository")
            return False

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during clone")
        print_error("Unexpected error during clone", exception=e)
        return False


def handle_init(args):
    """Handle init command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would initialize git repository at {args.path}")
            return True

        if getattr(args, "verbose", False):
            logger.info(f"Initializing git repository at {args.path}")

        result = initialize_git_repository(path=args.path)

        if result:
            print_success(f"Initialized git repository at {args.path}")
            return True
        else:
            print_error("Failed to initialize git repository")
            return False

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during init")
        print_error("Unexpected error during init", exception=e)
        return False


def handle_history(args):
    """Handle commit history command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Getting commit history (limit: {args.limit})")

        history = get_commit_history(limit=args.limit)

        print_section("Commit History")
        if isinstance(history, list):
            for commit in history:
                hash_val = commit.get("hash", "N/A")[:8] if commit.get("hash") else "N/A"
                message = commit.get("message", "N/A")
                print(f"  {hash_val} - {message}")
        else:
            print(format_output(history, format_type="json"))
        print_section("", separator="")
        return True

    except GitOperationError as e:
        logger.error(f"Git operation error: {str(e)}")
        print_error("Git operation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error getting commit history")
        print_error("Unexpected error getting commit history", exception=e)
        return False


def handle_check(args):
    """Handle check git availability command."""
    try:
        available = check_git_availability()
        if available:
            print_success("Git is available")
            return True
        else:
            print_error("Git is not available")
            return False

    except Exception as e:
        logger.exception("Unexpected error checking git availability")
        print_error("Unexpected error checking git availability", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Git Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status
  %(prog)s branch current
  %(prog)s branch create feature/new-feature
  %(prog)s branch switch main
  %(prog)s add file1.py file2.py
  %(prog)s commit -m "Add new feature"
  %(prog)s push --branch main --remote origin
  %(prog)s pull --remote origin --branch main
  %(prog)s clone https://github.com/user/repo.git --destination ./repo
  %(prog)s init --path .
  %(prog)s history --limit 10
  %(prog)s check
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry run mode (no changes)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    subparsers.add_parser("status", help="Show git status")

    # Branch commands
    branch_parser = subparsers.add_parser("branch", help="Branch operations")
    branch_subparsers = branch_parser.add_subparsers(
        dest="action", help="Branch action"
    )
    branch_subparsers.add_parser("current", help="Show current branch")
    branch_create = branch_subparsers.add_parser("create", help="Create branch")
    branch_create.add_argument("name", help="Branch name")
    branch_switch = branch_subparsers.add_parser("switch", help="Switch branch")
    branch_switch.add_argument("name", help="Branch name")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add files to staging")
    add_parser.add_argument("files", nargs="*", help="Files to add")

    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Commit changes")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    commit_parser.add_argument("files", nargs="*", help="Files to commit")

    # Push command
    push_parser = subparsers.add_parser("push", help="Push changes")
    push_parser.add_argument("--branch", default="main", help="Branch to push")
    push_parser.add_argument("--remote", default="origin", help="Remote name")
    push_parser.add_argument("--force", action="store_true", help="Force push")

    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Pull changes")
    pull_parser.add_argument("--branch", help="Branch to pull")
    pull_parser.add_argument("--remote", default="origin", help="Remote name")

    # Clone command
    clone_parser = subparsers.add_parser("clone", help="Clone repository")
    clone_parser.add_argument("url", help="Repository URL")
    clone_parser.add_argument("--destination", default=".", help="Destination path")
    clone_parser.add_argument("--branch", help="Branch to clone")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize git repository")
    init_parser.add_argument("--path", default=".", help="Repository path")

    # History command
    history_parser = subparsers.add_parser("history", help="Show commit history")
    history_parser.add_argument("--limit", type=int, default=10, help="Number of commits")

    # Check command
    subparsers.add_parser("check", help="Check git availability")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "status": handle_status,
        "branch": handle_branch,
        "commit": handle_commit,
        "add": handle_add,
        "push": handle_push,
        "pull": handle_pull,
        "clone": handle_clone,
        "init": handle_init,
        "history": handle_history,
        "check": handle_check,
    }

    handler = handlers.get(args.command)
    if handler:
        success = handler(args)
        return 0 if success else 1
    else:
        print_error("Unknown command", context=args.command)
        return 1


if __name__ == "__main__":
    sys.exit(main())


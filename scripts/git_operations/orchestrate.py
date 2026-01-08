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

# Setup path to include src
# scripts/git_operations/orchestrate.py -> git_operations -> scripts -> codomyrmex (root)
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir / "src"))

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import GitOperationError, RepositoryError, CodomyrmexError

# Import shared utilities
from codomyrmex.utils.cli_helpers import (
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
    add_remote,
    amend_commit,
    apply_stash,
    check_git_availability,
    cherry_pick,
    clone_repository,
    commit_changes,
    create_branch,
    create_tag,
    fetch_changes,
    get_config,
    get_commit_history,
    get_commit_history_filtered,
    get_current_branch,
    get_status,
    initialize_git_repository,
    is_git_repository,
    list_remotes,
    list_stashes,
    list_tags,
    merge_branch,
    pull_changes,
    push_changes,
    rebase_branch,
    remove_remote,
    set_config,
    stash_changes,
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
        file_paths = args.files if args.files else None
        author_name = getattr(args, "author_name", None)
        author_email = getattr(args, "author_email", None)
        stage_all = getattr(args, "stage_all", True)  # Default True, set to False with --no-stage-all
        
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would commit with message: {args.message}")
            if file_paths:
                print_info(f"Files: {', '.join(file_paths)}")
            if author_name:
                print_info(f"Author: {author_name} <{author_email or ''}>")
            return True

        if getattr(args, "verbose", False):
            logger.info(f"Committing with message: {args.message}")
            if file_paths:
                logger.info(f"Files: {', '.join(file_paths)}")
            if author_name:
                logger.info(f"Author: {author_name} <{author_email or ''}>")

        result = commit_changes(
            message=args.message,
            file_paths=file_paths,
            author_name=author_name,
            author_email=author_email,
            stage_all=stage_all,
        )

        if result:
            print_success(f"Committed changes: {args.message} (SHA: {result[:8]})")
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

        # Use filtered history if any filters are provided
        if any([
            getattr(args, "since", None),
            getattr(args, "until", None),
            getattr(args, "author", None),
            getattr(args, "branch", None),
            getattr(args, "file", None),
        ]):
            history = get_commit_history_filtered(
                limit=args.limit,
                since=getattr(args, "since", None),
                until=getattr(args, "until", None),
                author=getattr(args, "author", None),
                branch=getattr(args, "branch", None),
                file_path=getattr(args, "file", None),
            )
        else:
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


def handle_fetch(args):
    """Handle fetch command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would fetch from {args.remote}")
            if args.branch:
                print_info(f"Branch: {args.branch}")
            return True

        result = fetch_changes(
            remote=args.remote,
            branch=args.branch,
            prune=getattr(args, "prune", False),
        )

        if result:
            print_success(f"Fetched changes from {args.remote}")
            return True
        else:
            print_error("Failed to fetch changes")
            return False

    except Exception as e:
        logger.exception("Unexpected error during fetch")
        print_error("Unexpected error during fetch", exception=e)
        return False


def handle_remote(args):
    """Handle remote operations."""
    try:
        if args.action == "list":
            remotes = list_remotes()
            print_section("Git Remotes")
            if remotes:
                for remote in remotes:
                    print(f"  {remote['name']}: {remote['url']}")
            else:
                print("  No remotes configured")
            print_section("", separator="")
            return True
        elif args.action == "add":
            if getattr(args, "dry_run", False):
                print_info(f"Dry run: Would add remote '{args.name}' with URL: {args.url}")
                return True
            result = add_remote(args.name, args.url)
            if result:
                print_success(f"Added remote: {args.name}")
                return True
            else:
                print_error("Failed to add remote")
                return False
        elif args.action == "remove":
            if getattr(args, "dry_run", False):
                print_info(f"Dry run: Would remove remote '{args.name}'")
                return True
            result = remove_remote(args.name)
            if result:
                print_success(f"Removed remote: {args.name}")
                return True
            else:
                print_error("Failed to remove remote")
                return False

    except Exception as e:
        logger.exception("Unexpected error during remote operation")
        print_error("Unexpected error during remote operation", exception=e)
        return False


def handle_config(args):
    """Handle config operations."""
    try:
        if args.action == "get":
            value = get_config(args.key, global_config=getattr(args, "global", False))
            if value:
                print_success(f"{args.key} = {value}")
                return True
            else:
                print_error(f"Config key '{args.key}' not found")
                return False
        elif args.action == "set":
            if getattr(args, "dry_run", False):
                print_info(f"Dry run: Would set {args.key} = {args.value}")
                return True
            result = set_config(
                args.key, args.value, global_config=getattr(args, "global", False)
            )
            if result:
                print_success(f"Set {args.key} = {args.value}")
                return True
            else:
                print_error("Failed to set config")
                return False

    except Exception as e:
        logger.exception("Unexpected error during config operation")
        print_error("Unexpected error during config operation", exception=e)
        return False


def handle_cherry_pick(args):
    """Handle cherry-pick command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would cherry-pick commit: {args.commit}")
            return True

        result = cherry_pick(
            args.commit, no_commit=getattr(args, "no_commit", False)
        )

        if result:
            print_success(f"Cherry-picked commit: {args.commit[:8]}")
            return True
        else:
            print_error("Failed to cherry-pick commit")
            return False

    except Exception as e:
        logger.exception("Unexpected error during cherry-pick")
        print_error("Unexpected error during cherry-pick", exception=e)
        return False


def handle_amend(args):
    """Handle amend commit command."""
    try:
        author_name = getattr(args, "author_name", None)
        author_email = getattr(args, "author_email", None)
        
        if getattr(args, "dry_run", False):
            print_info("Dry run: Would amend last commit")
            if args.message:
                print_info(f"Message: {args.message}")
            return True

        result = amend_commit(
            message=args.message,
            author_name=author_name,
            author_email=author_email,
            no_edit=getattr(args, "no_edit", False),
        )

        if result:
            print_success(f"Amended commit: {result[:8]}")
            return True
        else:
            print_error("Failed to amend commit")
            return False

    except Exception as e:
        logger.exception("Unexpected error during amend")
        print_error("Unexpected error during amend", exception=e)
        return False


def handle_merge(args):
    """Handle merge command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would merge {args.branch} into current branch")
            return True

        result = merge_branch(
            source_branch=args.branch,
            strategy=getattr(args, "strategy", None)
        )

        if result:
            print_success(f"Merged {args.branch} successfully")
            return True
        else:
            print_error("Failed to merge branch")
            return False
            
    except Exception as e:
        logger.exception("Unexpected error during merge")
        print_error("Unexpected error during merge", exception=e)
        return False


def handle_rebase(args):
    """Handle rebase command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would rebase on {args.upstream}")
            return True

        result = rebase_branch(
            target_branch=args.upstream,
            interactive=getattr(args, "interactive", False)
        )

        if result:
            print_success(f"Rebased on {args.upstream} successfully")
            return True
        else:
            print_error("Failed to rebase")
            return False
            
    except Exception as e:
        logger.exception("Unexpected error during rebase")
        print_error("Unexpected error during rebase", exception=e)
        return False


def handle_tag(args):
    """Handle tag operations."""
    try:
        if args.action == "list":
            tags = list_tags()
            print_section("Git Tags")
            if tags:
                for tag in tags:
                    print(f"  {tag}")
            else:
                print("  No tags found")
            print_section("", separator="")
            return True
        elif args.action == "create":
            if getattr(args, "dry_run", False):
                print_info(f"Dry run: Would create tag '{args.name}'")
                return True
            result = create_tag(args.name, message=getattr(args, "message", None))
            if result:
                print_success(f"Created tag: {args.name}")
                return True
            else:
                print_error("Failed to create tag")
                return False
                
    except Exception as e:
        logger.exception("Unexpected error during tag operation")
        print_error("Unexpected error during tag operation", exception=e)
        return False


def handle_stash(args):
    """Handle stash operations."""
    try:
        if args.action == "list":
            stashes = list_stashes()
            print_section("Git Stashes")
            if stashes:
                for stash in stashes:
                    print(f"  {stash}")
            else:
                print("  No stashes found")
            print_section("", separator="")
            return True
        elif args.action == "save":
            if getattr(args, "dry_run", False):
                print_info("Dry run: Would stash changes")
                return True
            result = stash_changes(message=getattr(args, "message", None))
            if result:
                print_success("Saved stash")
                return True
            else:
                print_error("Failed to save stash")
                return False
        elif args.action == "apply":
            if getattr(args, "dry_run", False):
                print_info("Dry run: Would apply last stash")
                return True
            result = apply_stash()
            if result:
                print_success("Applied stash")
                return True
            else:
                print_error("Failed to apply stash")
                return False
                
    except Exception as e:
        logger.exception("Unexpected error during stash operation")
        print_error("Unexpected error during stash operation", exception=e)
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
  %(prog)s commit -m "Add new feature"
  %(prog)s merge feature-branch
  %(prog)s rebase main
  %(prog)s tag create v1.0.0 -m "Release v1.0.0"
  %(prog)s stash save -m "WIP"
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
    commit_parser.add_argument("--author-name", help="Override author name")
    commit_parser.add_argument("--author-email", help="Override author email")
    commit_parser.add_argument("--no-stage-all", action="store_false", dest="stage_all", help="Don't stage all tracked files")

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
    history_parser.add_argument("--since", help="Show commits after this date")
    history_parser.add_argument("--until", help="Show commits before this date")
    history_parser.add_argument("--author", help="Filter by author")
    history_parser.add_argument("--branch", help="Branch to show commits from")
    history_parser.add_argument("--file", help="Show only commits affecting this file")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch changes from remote")
    fetch_parser.add_argument("--remote", default="origin", help="Remote name")
    fetch_parser.add_argument("--branch", help="Branch to fetch")
    fetch_parser.add_argument("--prune", action="store_true", help="Prune remote-tracking branches")

    # Remote commands
    remote_parser = subparsers.add_parser("remote", help="Remote operations")
    remote_subparsers = remote_parser.add_subparsers(
        dest="action", help="Remote action", required=True
    )
    remote_subparsers.add_parser("list", help="List remotes")
    remote_add = remote_subparsers.add_parser("add", help="Add remote")
    remote_add.add_argument("name", help="Remote name")
    remote_add.add_argument("url", help="Remote URL")
    remote_remove = remote_subparsers.add_parser("remove", help="Remove remote")
    remote_remove.add_argument("name", help="Remote name")

    # Config commands
    config_parser = subparsers.add_parser("config", help="Config operations")
    config_subparsers = config_parser.add_subparsers(
        dest="action", help="Config action", required=True
    )
    config_get = config_subparsers.add_parser("get", help="Get config value")
    config_get.add_argument("key", help="Config key")
    config_get.add_argument("--global", action="store_true", dest="global", help="Use global config")
    config_set = config_subparsers.add_parser("set", help="Set config value")
    config_set.add_argument("key", help="Config key")
    config_set.add_argument("value", help="Config value")
    config_set.add_argument("--global", action="store_true", dest="global", help="Use global config")

    # Cherry-pick command
    cherry_pick_parser = subparsers.add_parser("cherry-pick", help="Cherry-pick a commit")
    cherry_pick_parser.add_argument("commit", help="Commit SHA to cherry-pick")
    cherry_pick_parser.add_argument("--no-commit", action="store_true", help="Don't commit changes")

    # Amend command
    amend_parser = subparsers.add_parser("amend", help="Amend last commit")
    amend_parser.add_argument("-m", "--message", help="New commit message")
    amend_parser.add_argument("--author-name", help="Override author name")
    amend_parser.add_argument("--author-email", help="Override author email")
    amend_parser.add_argument("--no-edit", action="store_true", help="Don't edit commit message")

    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge a branch")
    merge_parser.add_argument("branch", help="Branch to merge")
    merge_parser.add_argument("--strategy", help="Merge strategy")

    # Rebase command
    rebase_parser = subparsers.add_parser("rebase", help="Rebase on upstream")
    rebase_parser.add_argument("upstream", help="Upstream branch")
    rebase_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive rebase")

    # Tag commands
    tag_parser = subparsers.add_parser("tag", help="Tag operations")
    tag_subparsers = tag_parser.add_subparsers(dest="action", help="Tag action", required=True)
    tag_subparsers.add_parser("list", help="List tags")
    tag_create = tag_subparsers.add_parser("create", help="Create tag")
    tag_create.add_argument("name", help="Tag name")
    tag_create.add_argument("-m", "--message", help="Tag message")

    # Stash commands
    stash_parser = subparsers.add_parser("stash", help="Stash operations")
    stash_subparsers = stash_parser.add_subparsers(dest="action", help="Stash action", required=True)
    stash_subparsers.add_parser("list", help="List stashes")
    stash_save = stash_subparsers.add_parser("save", help="Save stash")
    stash_save.add_argument("-m", "--message", help="Stash message")
    stash_subparsers.add_parser("apply", help="Apply last stash")

    # Check command
    subparsers.add_parser("check", help="Check git availability")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "status": handle_status,
        "branch": handle_branch,
        "commit": handle_commit,
        "add": handle_add,
        "push": handle_push,
        "pull": handle_pull,
        "fetch": handle_fetch,
        "clone": handle_clone,
        "init": handle_init,
        "history": handle_history,
        "check": handle_check,
        "remote": handle_remote,
        "config": handle_config,
        "cherry-pick": handle_cherry_pick,
        "amend": handle_amend,
        "merge": handle_merge,
        "rebase": handle_rebase,
        "tag": handle_tag,
        "stash": handle_stash,
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

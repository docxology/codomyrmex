import argparse
import traceback
from pathlib import Path

from codomyrmex.git_operations.core.git import (
    add_remote,
    clean_repository,
    list_remotes,
    prune_remote,
    remove_remote,
)
from codomyrmex.git_operations.core.repository import (
    RepositoryManager,
    RepositoryType,
)
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent / "src"
# sys.path.insert(0, str(src_dir))  # Removed sys.path manipulation


def cmd_list(manager: RepositoryManager, args) -> None:
    """List repositories command."""
    repo_type = None
    if args.type:
        try:
            repo_type = RepositoryType(args.type.upper())
        except ValueError:
            print(f"Invalid repository type: {args.type}")
            print(f"Valid types: {', '.join([t.value for t in RepositoryType])}")
            return

    repos = manager.list_repositories(repo_type)

    if args.owner:
        repos = [repo for repo in repos if repo.owner.lower() == args.owner.lower()]

    print(f"\nFound {len(repos)} repositories:")
    print("-" * 80)

    for repo in repos:
        local_path = manager.get_local_path(repo)
        exists = (
            "✅" if local_path.exists() and (local_path / ".git").exists() else "❌"
        )

        print(
            f"{exists} {repo.repo_type.value:<4} {repo.full_name:<30} {repo.description}"
        )
        if args.verbose:
            print(f"     URL: {repo.url}")
            print(f"     Local: {local_path}")
            print()


def cmd_search(manager: RepositoryManager, args) -> None:
    """Search repositories command."""
    repos = manager.search_repositories(args.query)

    print(f"\nFound {len(repos)} repositories matching '{args.query}':")
    print("-" * 80)

    for repo in repos:
        local_path = manager.get_local_path(repo)
        exists = (
            "✅" if local_path.exists() and (local_path / ".git").exists() else "❌"
        )

        print(
            f"{exists} {repo.repo_type.value:<4} {repo.full_name:<30} {repo.description}"
        )
        if args.verbose:
            print(f"     URL: {repo.url}")
            print(f"     Local: {local_path}")
            print()


def cmd_clone(manager: RepositoryManager, args) -> None:
    """Clone repository command."""
    if args.all:
        # Bulk clone
        repo_type = None
        if args.type:
            try:
                repo_type = RepositoryType(args.type.upper())
            except ValueError:
                print(f"Invalid repository type: {args.type}")
                return

        owner_filter = args.owner if args.owner else None

        print("Bulk cloning repositories...")
        if repo_type:
            print(f"  Type filter: {repo_type.value}")
        if owner_filter:
            print(f"  Owner filter: {owner_filter}")

        results = manager.bulk_clone(repo_type, owner_filter)

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        print(f"\nBulk clone results: {successful}/{total} successful")

        if args.verbose:
            for repo_name, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {repo_name}")

    else:
        # Single repository clone
        if not args.repository:
            print("Error: Repository name required for single clone")
            print("Use --all for bulk cloning or specify a repository name")
            return

        success = manager.clone_repository(args.repository, args.path)

        if success:
            print(f"✅ Successfully cloned {args.repository}")
        else:
            print(f"❌ Failed to clone {args.repository}")


def cmd_update(manager: RepositoryManager, args) -> None:
    """Update repository command."""
    if args.all:
        # Bulk update
        repo_type = None
        if args.type:
            try:
                repo_type = RepositoryType(args.type.upper())
            except ValueError:
                print(f"Invalid repository type: {args.type}")
                return

        owner_filter = args.owner if args.owner else None

        print("Bulk updating repositories...")
        if repo_type:
            print(f"  Type filter: {repo_type.value}")
        if owner_filter:
            print(f"  Owner filter: {owner_filter}")

        results = manager.bulk_update(repo_type, owner_filter)

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        print(f"\nBulk update results: {successful}/{total} successful")

        if args.verbose:
            for repo_name, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {repo_name}")

    else:
        # Single repository update
        if not args.repository:
            print("Error: Repository name required for single update")
            print("Use --all for bulk updating or specify a repository name")
            return

        success = manager.update_repository(args.repository, args.path)

        if success:
            print(f"✅ Successfully updated {args.repository}")
        else:
            print(f"❌ Failed to update {args.repository}")


def cmd_status(manager: RepositoryManager, args) -> None:
    """Show repository status command."""
    if not args.repository:
        print("Error: Repository name required for status check")
        return

    status = manager.get_repository_status(args.repository, args.path)

    if not status:
        print(f"❌ Repository '{args.repository}' not found")
        return

    if "error" in status:
        print(f"❌ {status['error']}: {status['path']}")
        return

    print(f"\nRepository Status: {status['repository']}")
    print("-" * 50)
    print(f"Path: {status['path']}")
    print(f"Branch: {status['branch']}")
    print(f"Type: {status['type']}")
    print(f"Development repo: {status['is_development']}")

    repo_status = status["status"]
    if repo_status.get("clean"):
        print("Status: ✅ Clean")
    else:
        print("Status: 📝 Has changes")
        if repo_status.get("modified"):
            print(f"  Modified: {', '.join(repo_status['modified'])}")
        if repo_status.get("added"):
            print(f"  Added: {', '.join(repo_status['added'])}")
        if repo_status.get("untracked"):
            print(f"  Untracked: {', '.join(repo_status['untracked'])}")


def cmd_summary(manager: RepositoryManager, args) -> None:
    """Show repository library summary."""
    manager.print_repository_summary()


def cmd_remote(manager: RepositoryManager, args) -> None:
    """Remote management command."""
    if not args.repository:
        print("Error: Repository name required")
        return

    repo = manager.get_repository(args.repository)
    if not repo:
        print(f"❌ Repository '{args.repository}' not found")
        return

    local_path = str(manager.get_local_path(repo))
    if not Path(local_path).exists():
        print(f"❌ Repository not cloned at {local_path}")
        return

    if args.list:
        remotes = list_remotes(local_path)
        print(f"\nRemotes for {args.repository}:")
        for r in remotes:
            print(f"  {r['name']:<10} {r['url']}")
    elif args.add:
        if not args.url:
            print("Error: URL required for adding remote")
            return
        if add_remote(args.add, args.url, local_path):
            print(f"✅ Added remote '{args.add}'")
        else:
            print(f"❌ Failed to add remote '{args.add}'")
    elif args.remove:
        if remove_remote(args.remove, local_path):
            print(f"✅ Removed remote '{args.remove}'")
        else:
            print(f"❌ Failed to remove remote '{args.remove}'")
    elif args.prune:
        if prune_remote(args.prune, local_path):
            print(f"✅ Pruned remote '{args.prune}'")
        else:
            print(f"❌ Failed to prune remote '{args.prune}'")
    else:
        # Default to list
        remotes = list_remotes(local_path)
        print(f"\nRemotes for {args.repository}:")
        for r in remotes:
            print(f"  {r['name']:<10} {r['url']}")


def cmd_sync(manager: RepositoryManager, args) -> None:
    """Sync repository command."""
    if not args.repository:
        print("Error: Repository name required")
        return

    if manager.sync_repository(args.repository, args.path):
        print(f"✅ Successfully synced {args.repository}")
    else:
        print(f"❌ Failed to sync {args.repository}")


def cmd_prune(manager: RepositoryManager, args) -> None:
    """Prune repository command."""
    if not args.repository:
        print("Error: Repository name required")
        return

    if manager.prune_repository(args.repository, args.path):
        print(f"✅ Successfully pruned {args.repository}")
    else:
        print(f"❌ Failed to prune {args.repository}")


def cmd_clean(manager: RepositoryManager, args) -> None:
    """Clean repository command."""
    if not args.repository:
        print("Error: Repository name required")
        return

    repo = manager.get_repository(args.repository)
    if not repo:
        print(f"❌ Repository '{args.repository}' not found")
        return

    local_path = str(manager.get_local_path(repo))
    if args.path:
        local_path = args.path

    if clean_repository(force=args.force, directories=True, repository_path=local_path):
        print(f"✅ Successfully cleaned {args.repository}")
    else:
        print(f"❌ Failed to clean {args.repository}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Repository Manager CLI - Manage GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list --type own                    # List your own repositories
  %(prog)s search docxology                   # Search for docxology repositories
  %(prog)s clone docxology/docxology          # Clone a specific repository
  %(prog)s clone --all --type own             # Clone all your repositories
  %(prog)s update --all --owner docxology     # Update all docxology repositories
  %(prog)s status docxology/docxology         # Check repository status
  %(prog)s summary                            # Show library summary
        """,
    )

    parser.add_argument(
        "--base-path",
        help="Base path for repositories (default: ~/Documents/GitHub)",
        default=None,
    )

    parser.add_argument(
        "--library", help="Path to repository library file", default=None
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List repositories")
    list_parser.add_argument(
        "--type", help="Filter by repository type (own, use, fork)"
    )
    list_parser.add_argument("--owner", help="Filter by owner")
    list_parser.set_defaults(func=cmd_list)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search repositories")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=cmd_search)

    # Clone command
    clone_parser = subparsers.add_parser("clone", help="Clone repositories")
    clone_parser.add_argument(
        "repository", nargs="?", help="Repository name (owner/repo)"
    )
    clone_parser.add_argument("--path", help="Custom local path")
    clone_parser.add_argument(
        "--all", action="store_true", help="Clone all repositories"
    )
    clone_parser.add_argument("--type", help="Filter by repository type (for --all)")
    clone_parser.add_argument("--owner", help="Filter by owner (for --all)")
    clone_parser.set_defaults(func=cmd_clone)

    # Update command
    update_parser = subparsers.add_parser("update", help="Update repositories")
    update_parser.add_argument(
        "repository", nargs="?", help="Repository name (owner/repo)"
    )
    update_parser.add_argument("--path", help="Custom local path")
    update_parser.add_argument(
        "--all", action="store_true", help="Update all repositories"
    )
    update_parser.add_argument("--type", help="Filter by repository type (for --all)")
    update_parser.add_argument("--owner", help="Filter by owner (for --all)")
    update_parser.set_defaults(func=cmd_update)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show repository status")
    status_parser.add_argument("repository", help="Repository name (owner/repo)")
    status_parser.add_argument("--path", help="Custom local path")
    status_parser.set_defaults(func=cmd_status)

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show library summary")
    summary_parser.set_defaults(func=cmd_summary)

    # Remote command
    remote_parser = subparsers.add_parser("remote", help="Manage remotes")
    remote_parser.add_argument("repository", help="Repository name")
    remote_parser.add_argument("--list", action="store_true", help="List remotes")
    remote_parser.add_argument("--add", metavar="NAME", help="Add remote")
    remote_parser.add_argument("--url", help="URL for adding remote")
    remote_parser.add_argument("--remove", metavar="NAME", help="Remove remote")
    remote_parser.add_argument("--prune", metavar="NAME", help="Prune remote")
    remote_parser.set_defaults(func=cmd_remote)

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync repository (pull + push)")
    sync_parser.add_argument("repository", help="Repository name")
    sync_parser.add_argument("--path", help="Custom local path")
    sync_parser.set_defaults(func=cmd_sync)

    # Prune command
    prune_parser = subparsers.add_parser("prune", help="Prune repository branches")
    prune_parser.add_argument("repository", help="Repository name")
    prune_parser.add_argument("--path", help="Custom local path")
    prune_parser.set_defaults(func=cmd_prune)

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean repository")
    clean_parser.add_argument("repository", help="Repository name")
    clean_parser.add_argument("--path", help="Custom local path")
    clean_parser.add_argument("--force", action="store_true", help="Force clean (ignored files)")
    clean_parser.set_defaults(func=cmd_clean)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize repository manager
    try:
        manager = RepositoryManager(library_file=args.library, base_path=args.base_path)
    except Exception as e:
        print(f"Error initializing repository manager: {e}")
        return

    # Execute command
    try:
        args.func(manager, args)
    except Exception as e:
        print(f"Error executing command: {e}")
        if args.verbose:

            traceback.print_exc()


if __name__ == "__main__":
    main()

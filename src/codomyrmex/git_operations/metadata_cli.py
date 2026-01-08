from datetime import datetime
from pathlib import Path
import argparse
import json
import traceback

from codomyrmex.git_operations.repository_manager import RepositoryManager
from codomyrmex.git_operations.repository_metadata import (
from codomyrmex.logging_monitoring.logger_config import get_logger


#!/usr/bin/env python3
"""
Repository Metadata CLI - Command Line Interface for Repository Metadata Management

This script provides a command-line interface for managing repository metadata,
including status tracking, permissions, versions, and comprehensive reporting.
"""

    CloneStatus,
    RepositoryMetadataManager,
)


# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent / "src"
# sys.path.insert(0, str(src_dir))  # Removed sys.path manipulation

logger = get_logger(__name__)


def cmd_update_metadata(manager: RepositoryMetadataManager, args) -> None:
    """Update metadata for repositories."""
    if args.repository:
        # Update single repository
        parts = args.repository.split("/")
        if len(parts) != 2:
            print("Error: Repository must be in format 'owner/name'")
            return

        owner, name = parts
        full_name = f"{owner}/{name}"

        metadata = manager.create_or_update_metadata(
            full_name=full_name,
            owner=owner,
            name=name,
            repo_type=args.type or "USE",
            url=f"https://github.com/{full_name}.git",
            description=args.description or "",
            local_path=args.path or "",
        )

        print(f"✅ Updated metadata for {full_name}")
        if args.verbose:
            print(f"   Clone Status: {metadata.clone_status.value}")
            print(f"   Access Level: {metadata.access_level.value}")
            print(f"   Stars: {metadata.stats.stars}")
            print(f"   Last Activity: {metadata.stats.last_activity}")

    elif args.from_library:
        # Update from repository library
        repo_manager = RepositoryManager(
            library_file=args.from_library, github_token=args.token
        )

        repositories = []
        for repo in repo_manager.list_repositories():
            repositories.append(
                {
                    "owner": repo.owner,
                    "name": repo.name,
                    "type": repo.repo_type.value,
                    "url": repo.url,
                    "description": repo.description,
                    "local_path": repo.local_path_suggestion,
                }
            )

        print(f"Updating metadata for {len(repositories)} repositories from library...")
        results = manager.bulk_update_metadata(
            repositories, str(repo_manager.base_path)
        )

        successful = sum(1 for success in results.values() if success)
        print(f"✅ Updated {successful}/{len(results)} repositories")

    else:
        print("Error: Must specify --repository or --from-library")


def cmd_show_metadata(manager: RepositoryMetadataManager, args) -> None:
    """Show metadata for repositories."""
    if args.repository:
        # Show single repository
        metadata = manager.get_repository_metadata(args.repository)
        if not metadata:
            print(f"❌ No metadata found for {args.repository}")
            return

        print(f"\n📊 Repository Metadata: {metadata.full_name}")
        print("=" * 60)
        print(f"Owner: {metadata.owner}")
        print(f"Name: {metadata.name}")
        print(f"Type: {metadata.repo_type}")
        print(f"Description: {metadata.description}")
        print(f"URL: {metadata.url}")
        print()

        print("🔐 Access & Permissions:")
        print(f"   Access Level: {metadata.access_level.value}")
        print(f"   Private: {metadata.is_private}")
        print(f"   Fork: {metadata.is_fork}")
        print(f"   Can Push: {metadata.can_push}")
        print()

        print("📁 Clone & Sync Status:")
        print(f"   Clone Status: {metadata.clone_status.value}")
        print(f"   Sync Status: {metadata.sync_status.value}")
        print(f"   Local Path: {metadata.local_path}")
        print(f"   Clone Date: {metadata.clone_date}")
        print(f"   Last Sync: {metadata.last_sync_date}")
        print()

        print("🔖 Version Information:")
        print(f"   Default Branch: {metadata.default_branch}")
        print(f"   Current Local Branch: {metadata.current_local_branch}")
        print(f"   Latest Release: {metadata.latest_release}")
        print(f"   Version Tags: {', '.join(metadata.version_tags[:5])}")
        print()

        print("📈 Statistics:")
        print(f"   Stars: {metadata.stats.stars}")
        print(f"   Forks: {metadata.stats.forks}")
        print(f"   Watchers: {metadata.stats.watchers}")
        print(f"   Issues: {metadata.stats.issues}")
        print(f"   Size: {metadata.stats.size_kb} KB")
        print(f"   Last Activity: {metadata.stats.last_activity}")
        print()

        if metadata.local_info.exists:
            print("💻 Local Repository Info:")
            print(f"   Path: {metadata.local_info.path}")
            print(f"   Git Repository: {metadata.local_info.is_git_repo}")
            print(f"   Current Branch: {metadata.local_info.current_branch}")
            print(f"   Uncommitted Changes: {metadata.local_info.uncommitted_changes}")
            print(f"   Untracked Files: {len(metadata.local_info.untracked_files)}")
            print(f"   Modified Files: {len(metadata.local_info.modified_files)}")
            print(f"   Last Commit: {metadata.local_info.last_commit_hash[:8]}")
            print(f"   Last Commit Date: {metadata.local_info.last_commit_date}")
            print()

        print("🏷️ Custom Fields:")
        print(f"   Tags: {', '.join(metadata.tags)}")
        print(f"   Priority: {metadata.priority}")
        print(f"   Category: {metadata.category}")
        print(f"   Notes: {metadata.notes}")
        print()

        print("🕒 Metadata Info:")
        print(f"   Created: {metadata.created_date}")
        print(f"   Updated: {metadata.updated_date}")
        print(f"   Last Metadata Update: {metadata.last_metadata_update}")
        print(f"   Metadata Version: {metadata.metadata_version}")

    else:
        # Show summary for all repositories
        print("\n📊 Repository Metadata Summary")
        print("=" * 50)

        all_repos = list(manager.metadata.values())
        if not all_repos:
            print("No repositories found in metadata")
            return

        print(f"Total Repositories: {len(all_repos)}")
        print()

        # Group by status
        status_groups = {}
        for repo in all_repos:
            status = repo.clone_status.value
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(repo)

        for status, repos in status_groups.items():
            print(f"{status.upper()}: {len(repos)}")
            if args.verbose:
                for repo in repos[:5]:  # Show first 5
                    print(f"   - {repo.full_name}")
                if len(repos) > 5:
                    print(f"   ... and {len(repos) - 5} more")
            print()


def cmd_report(manager: RepositoryMetadataManager, args) -> None:
    """Generate comprehensive metadata report."""
    report = manager.generate_metadata_report()

    print("\n📊 COMPREHENSIVE REPOSITORY METADATA REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Repositories: {report['total_repositories']}")
    print()

    print("📁 Clone Status Breakdown:")
    for status, count in report["status_breakdown"].items():
        print(f"   {status.replace('_', ' ').title()}: {count}")
    print()

    print("🔐 Access Level Breakdown:")
    for access, count in report["access_breakdown"].items():
        print(f"   {access.replace('_', ' ').title()}: {count}")
    print()

    print("📂 Repository Type Breakdown:")
    for repo_type, count in report["type_breakdown"].items():
        print(f"   {repo_type}: {count}")
    print()

    print("⭐ Statistics:")
    print(f"   Total Stars: {report['total_stars']:,}")
    print(f"   Total Forks: {report['total_forks']:,}")
    print(f"   Outdated Repositories: {report['outdated_repositories']}")
    print()

    if args.detailed:
        # Show detailed breakdowns
        print("🔍 DETAILED ANALYSIS")
        print("-" * 40)

        # Top starred repositories
        starred_repos = sorted(
            manager.metadata.values(), key=lambda x: x.stats.stars, reverse=True
        )[:10]

        print("⭐ Top Starred Repositories:")
        for repo in starred_repos:
            if repo.stats.stars > 0:
                print(f"   {repo.full_name}: {repo.stats.stars} stars")
        print()

        # Recently active repositories
        active_repos = [
            repo for repo in manager.metadata.values() if repo.stats.last_activity
        ]
        active_repos.sort(key=lambda x: x.stats.last_activity or "", reverse=True)

        print("🕒 Recently Active Repositories:")
        for repo in active_repos[:10]:
            print(f"   {repo.full_name}: {repo.stats.last_activity}")
        print()

        # Repositories needing attention
        outdated = manager.get_outdated_repositories(30)
        if outdated:
            print("⚠️ Repositories Needing Attention (not synced in 30 days):")
            for repo in outdated[:10]:
                last_sync = repo.last_sync_date or "Never"
                print(f"   {repo.full_name}: {last_sync}")

    if args.export:
        # Export report to JSON
        export_file = args.export
        with open(export_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📄 Report exported to: {export_file}")


def cmd_sync_status(manager: RepositoryMetadataManager, args) -> None:
    """Check synchronization status of repositories."""
    print("\n🔄 Repository Synchronization Status")
    print("=" * 50)

    cloned_repos = manager.get_repositories_by_status(CloneStatus.CLONED)

    if not cloned_repos:
        print("No cloned repositories found")
        return

    print(f"Checking {len(cloned_repos)} cloned repositories...")
    print()

    needs_sync = []
    up_to_date = []
    errors = []

    for repo in cloned_repos:
        try:
            # Update local info
            manager.update_local_repository_info(repo)

            if repo.local_info.uncommitted_changes:
                needs_sync.append((repo, "Uncommitted changes"))
            elif repo.local_info.untracked_files:
                needs_sync.append(
                    (repo, f"{len(repo.local_info.untracked_files)} untracked files")
                )
            else:
                up_to_date.append(repo)

        except Exception as e:
            errors.append((repo, str(e)))

    print(f"✅ Up to Date: {len(up_to_date)}")
    print(f"⚠️ Needs Attention: {len(needs_sync)}")
    print(f"❌ Errors: {len(errors)}")
    print()

    if needs_sync and args.verbose:
        print("⚠️ Repositories Needing Attention:")
        for repo, reason in needs_sync:
            print(f"   {repo.full_name}: {reason}")
        print()

    if errors and args.verbose:
        print("❌ Repositories with Errors:")
        for repo, error in errors:
            print(f"   {repo.full_name}: {error}")


def cmd_cleanup(manager: RepositoryMetadataManager, args) -> None:
    """Clean up metadata for non-existent repositories."""
    print("\n🧹 Cleaning up repository metadata")
    print("=" * 40)

    removed_count = 0
    total_count = len(manager.metadata)

    to_remove = []
    for full_name, metadata in manager.metadata.items():
        if metadata.local_path and not Path(metadata.local_path).exists():
            if args.dry_run:
                print(
                    f"Would remove: {full_name} (path not found: {metadata.local_path})"
                )
            else:
                to_remove.append(full_name)

    if not args.dry_run:
        for full_name in to_remove:
            del manager.metadata[full_name]
            removed_count += 1
            print(f"Removed: {full_name}")

        if removed_count > 0:
            manager.save_metadata()

    print("\n📊 Cleanup Summary:")
    print(f"   Total repositories: {total_count}")
    print(f"   Removed: {removed_count}")
    print(f"   Remaining: {total_count - removed_count}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Repository Metadata Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s update --repository docxology/codomyrmex --type OWN
  %(prog)s update --from-library repository_library.txt
  %(prog)s show --repository docxology/codomyrmex
  %(prog)s show --verbose
  %(prog)s report --detailed --export report.json
  %(prog)s sync-status --verbose
  %(prog)s cleanup --dry-run
        """,
    )

    parser.add_argument(
        "--metadata-file", help="Path to metadata JSON file", default=None
    )

    parser.add_argument("--token", help="GitHub personal access token", default=None)

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update repository metadata")
    update_parser.add_argument("--repository", help="Repository name (owner/repo)")
    update_parser.add_argument("--type", help="Repository type (OWN, FORK, USE)")
    update_parser.add_argument("--description", help="Repository description")
    update_parser.add_argument("--path", help="Local repository path")
    update_parser.add_argument(
        "--from-library", help="Update from repository library file"
    )
    update_parser.set_defaults(func=cmd_update_metadata)

    # Show command
    show_parser = subparsers.add_parser("show", help="Show repository metadata")
    show_parser.add_argument("--repository", help="Repository name (owner/repo)")
    show_parser.set_defaults(func=cmd_show_metadata)

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate metadata report")
    report_parser.add_argument(
        "--detailed", action="store_true", help="Detailed report"
    )
    report_parser.add_argument("--export", help="Export report to JSON file")
    report_parser.set_defaults(func=cmd_report)

    # Sync status command
    sync_parser = subparsers.add_parser(
        "sync-status", help="Check synchronization status"
    )
    sync_parser.set_defaults(func=cmd_sync_status)

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up metadata")
    cleanup_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be removed"
    )
    cleanup_parser.set_defaults(func=cmd_cleanup)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize metadata manager
    try:
        manager = RepositoryMetadataManager(
            metadata_file=args.metadata_file, github_token=args.token
        )
    except Exception as e:
        print(f"Error initializing metadata manager: {e}")
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

"""
Repository Metadata Management System

This module provides comprehensive metadata tracking for repositories including
clone status, permissions, versions, dates, and other structured information.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import subprocess
import requests
from codomyrmex.exceptions import CodomyrmexError

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent / "src"
# sys.path.insert(0, str(src_dir))  # Removed sys.path manipulation

from codomyrmex.git_operations.git_manager import (
    is_git_repository,
    get_current_branch,
    get_commit_history,
    get_status as get_git_status,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AccessLevel(Enum):
    """Repository access levels."""

    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    UNKNOWN = "unknown"


class CloneStatus(Enum):
    """Repository clone status."""

    NOT_CLONED = "not_cloned"
    CLONED = "cloned"
    OUTDATED = "outdated"
    ERROR = "error"
    UNKNOWN = "unknown"


class SyncStatus(Enum):
    """Repository synchronization status."""

    UP_TO_DATE = "up_to_date"
    AHEAD = "ahead"
    BEHIND = "behind"
    DIVERGED = "diverged"
    UNKNOWN = "unknown"


@dataclass
class RepositoryStats:
    """Repository statistics."""

    total_commits: int = 0
    contributors: int = 0
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    issues: int = 0
    pull_requests: int = 0
    size_kb: int = 0
    languages: Dict[str, int] = field(default_factory=dict)
    last_activity: Optional[str] = None


@dataclass
class LocalRepositoryInfo:
    """Local repository information."""

    path: str = ""
    exists: bool = False
    is_git_repo: bool = False
    current_branch: str = ""
    uncommitted_changes: bool = False
    untracked_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    staged_files: List[str] = field(default_factory=list)
    last_commit_hash: str = ""
    last_commit_date: Optional[str] = None
    last_commit_message: str = ""
    total_local_commits: int = 0


@dataclass
class RepositoryMetadata:
    """Comprehensive repository metadata."""

    # Basic Information
    full_name: str
    owner: str
    name: str
    repo_type: str  # OWN, FORK, USE
    url: str
    clone_url: str
    description: str = ""

    # Access & Permissions
    access_level: AccessLevel = AccessLevel.UNKNOWN
    is_private: bool = False
    is_fork: bool = False
    can_push: bool = False
    can_admin: bool = False

    # Clone & Sync Information
    clone_status: CloneStatus = CloneStatus.NOT_CLONED
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    local_path: str = ""
    clone_date: Optional[str] = None
    last_sync_date: Optional[str] = None
    last_fetch_date: Optional[str] = None

    # Version Information
    default_branch: str = "main"
    current_local_branch: str = ""
    latest_remote_commit: str = ""
    latest_local_commit: str = ""
    version_tags: List[str] = field(default_factory=list)
    latest_release: str = ""

    # Statistics
    stats: RepositoryStats = field(default_factory=RepositoryStats)

    # Local Repository Info
    local_info: LocalRepositoryInfo = field(default_factory=LocalRepositoryInfo)

    # Metadata Management
    created_date: Optional[str] = None
    updated_date: Optional[str] = None
    metadata_version: str = "1.0"
    last_metadata_update: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Custom Fields
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    priority: int = 0  # 0=normal, 1=high, 2=critical
    category: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert enums to strings
        data["access_level"] = self.access_level.value
        data["clone_status"] = self.clone_status.value
        data["sync_status"] = self.sync_status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryMetadata":
        """Create from dictionary (JSON deserialization)."""
        # Convert enum strings back to enums
        if "access_level" in data:
            data["access_level"] = AccessLevel(data["access_level"])
        if "clone_status" in data:
            data["clone_status"] = CloneStatus(data["clone_status"])
        if "sync_status" in data:
            data["sync_status"] = SyncStatus(data["sync_status"])

        # Handle nested dataclasses
        if "stats" in data and isinstance(data["stats"], dict):
            data["stats"] = RepositoryStats(**data["stats"])
        if "local_info" in data and isinstance(data["local_info"], dict):
            data["local_info"] = LocalRepositoryInfo(**data["local_info"])

        return cls(**data)


class RepositoryMetadataManager:
    """Manager for repository metadata with persistence."""

    def __init__(
        self, metadata_file: Optional[str] = None, github_token: Optional[str] = None
    ):
        """
        Initialize metadata manager.

        Args:
            metadata_file: Path to metadata JSON file
            github_token: GitHub personal access token for API access
        """
        if metadata_file is None:
            metadata_file = os.path.join(
                os.path.dirname(__file__), "repository_metadata.json"
            )

        self.metadata_file = Path(metadata_file)
        self.github_token = github_token
        self.metadata: Dict[str, RepositoryMetadata] = {}

        # GitHub API headers
        self.github_headers = {}
        if github_token:
            self.github_headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

        self.load_metadata()

    def load_metadata(self) -> None:
        """Load metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)

                self.metadata = {}
                for repo_name, repo_data in data.items():
                    self.metadata[repo_name] = RepositoryMetadata.from_dict(repo_data)

                logger.info(f"Loaded metadata for {len(self.metadata)} repositories")

            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                self.metadata = {}
        else:
            logger.info("No existing metadata file found, starting fresh")
            self.metadata = {}

    def save_metadata(self) -> bool:
        """Save metadata to JSON file."""
        try:
            # Create backup
            if self.metadata_file.exists():
                backup_file = f"{self.metadata_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.metadata_file.rename(backup_file)
                logger.info(f"Created backup: {backup_file}")

            # Prepare data for JSON serialization
            data = {}
            for repo_name, metadata in self.metadata.items():
                data[repo_name] = metadata.to_dict()

            # Write to file
            with open(self.metadata_file, "w") as f:
                json.dump(data, f, indent=2, sort_keys=True)

            logger.info(f"Saved metadata for {len(self.metadata)} repositories")
            return True

        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False

    def get_repository_metadata(self, full_name: str) -> Optional[RepositoryMetadata]:
        """Get metadata for a specific repository."""
        return self.metadata.get(full_name)

    def update_repository_metadata(self, metadata: RepositoryMetadata) -> None:
        """Update metadata for a repository."""
        metadata.last_metadata_update = datetime.now(timezone.utc).isoformat()
        self.metadata[metadata.full_name] = metadata

    def fetch_github_metadata(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Fetch repository metadata from GitHub API."""
        url = f"https://api.github.com/repos/{owner}/{repo}"

        try:
            response = requests.get(url, headers=self.github_headers)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch GitHub metadata for {owner}/{repo}: {e}")
            return None

    def determine_access_level(
        self, github_data: Dict[str, Any], owner: str
    ) -> AccessLevel:
        """Determine access level based on GitHub data."""
        if not github_data:
            return AccessLevel.UNKNOWN

        permissions = github_data.get("permissions", {})

        if permissions.get("admin", False):
            return AccessLevel.ADMIN
        elif permissions.get("push", False):
            return AccessLevel.READ_WRITE
        elif permissions.get("pull", True):  # Default assumption
            return AccessLevel.READ_ONLY
        else:
            return AccessLevel.UNKNOWN

    def update_local_repository_info(self, metadata: RepositoryMetadata) -> None:
        """Update local repository information."""
        local_path = Path(metadata.local_path)

        # Basic existence checks
        metadata.local_info.path = str(local_path)
        metadata.local_info.exists = local_path.exists()
        metadata.local_info.is_git_repo = (
            is_git_repository(str(local_path)) if local_path.exists() else False
        )

        if not metadata.local_info.is_git_repo:
            metadata.clone_status = (
                CloneStatus.NOT_CLONED if not local_path.exists() else CloneStatus.ERROR
            )
            return

        try:
            # Current branch
            metadata.local_info.current_branch = (
                get_current_branch(str(local_path)) or ""
            )
            metadata.current_local_branch = metadata.local_info.current_branch

            # Git status
            git_status = get_git_status(str(local_path))
            if git_status and not git_status.get("error"):
                metadata.local_info.uncommitted_changes = not git_status.get(
                    "clean", True
                )
                metadata.local_info.untracked_files = git_status.get("untracked", [])
                metadata.local_info.modified_files = git_status.get("modified", [])
                metadata.local_info.staged_files = git_status.get("added", [])

            # Commit information
            commits = get_commit_history(limit=1, repository_path=str(local_path))
            if commits:
                latest_commit = commits[0]
                metadata.local_info.last_commit_hash = latest_commit["hash"]
                metadata.local_info.last_commit_date = latest_commit["date"]
                metadata.local_info.last_commit_message = latest_commit["message"]
                metadata.latest_local_commit = latest_commit["hash"]

            # Total commits
            all_commits = get_commit_history(
                limit=1000, repository_path=str(local_path)
            )
            metadata.local_info.total_local_commits = (
                len(all_commits) if all_commits else 0
            )

            metadata.clone_status = CloneStatus.CLONED

        except Exception as e:
            logger.warning(f"Error updating local info for {metadata.full_name}: {e}")
            metadata.clone_status = CloneStatus.ERROR

    def create_or_update_metadata(
        self,
        full_name: str,
        owner: str,
        name: str,
        repo_type: str,
        url: str,
        description: str = "",
        local_path: str = "",
    ) -> RepositoryMetadata:
        """Create or update repository metadata."""

        # Get existing metadata or create new
        metadata = self.metadata.get(full_name)
        if metadata is None:
            metadata = RepositoryMetadata(
                full_name=full_name,
                owner=owner,
                name=name,
                repo_type=repo_type,
                url=url,
                clone_url=url,
                description=description,
                local_path=local_path,
                created_date=datetime.now(timezone.utc).isoformat(),
            )
        else:
            # Update basic info
            metadata.description = description or metadata.description
            metadata.local_path = local_path or metadata.local_path
            metadata.updated_date = datetime.now(timezone.utc).isoformat()

        # Fetch GitHub metadata
        github_data = self.fetch_github_metadata(owner, name)
        if github_data:
            # Update from GitHub API
            metadata.is_private = github_data.get("private", False)
            metadata.is_fork = github_data.get("fork", False)
            metadata.default_branch = github_data.get("default_branch", "main")
            metadata.access_level = self.determine_access_level(github_data, owner)

            # Update statistics
            metadata.stats.stars = github_data.get("stargazers_count", 0)
            metadata.stats.forks = github_data.get("forks_count", 0)
            metadata.stats.watchers = github_data.get("watchers_count", 0)
            metadata.stats.size_kb = github_data.get("size", 0)
            metadata.stats.issues = github_data.get("open_issues_count", 0)
            metadata.stats.last_activity = github_data.get("updated_at")

            # Languages
            try:
                lang_url = github_data.get("languages_url")
                if lang_url:
                    lang_response = requests.get(lang_url, headers=self.github_headers)
                    if lang_response.status_code == 200:
                        metadata.stats.languages = lang_response.json()
            except Exception as e:
                logger.warning(f"Failed to fetch languages for {full_name}: {e}")

        # Update local repository information
        if local_path:
            self.update_local_repository_info(metadata)

        # Store metadata
        self.update_repository_metadata(metadata)

        return metadata

    def bulk_update_metadata(
        self, repositories: List[Dict[str, str]], base_path: str = ""
    ) -> Dict[str, bool]:
        """Bulk update metadata for multiple repositories."""
        results = {}

        for repo_info in repositories:
            full_name = f"{repo_info['owner']}/{repo_info['name']}"
            local_path = (
                os.path.join(base_path, repo_info.get("local_path", ""))
                if base_path
                else ""
            )

            try:
                self.create_or_update_metadata(
                    full_name=full_name,
                    owner=repo_info["owner"],
                    name=repo_info["name"],
                    repo_type=repo_info.get("type", "USE"),
                    url=repo_info["url"],
                    description=repo_info.get("description", ""),
                    local_path=local_path,
                )
                results[full_name] = True
                logger.info(f"Updated metadata for {full_name}")

            except Exception as e:
                logger.error(f"Failed to update metadata for {full_name}: {e}")
                results[full_name] = False

        # Save all metadata
        self.save_metadata()

        return results

    def get_repositories_by_status(
        self, clone_status: CloneStatus
    ) -> List[RepositoryMetadata]:
        """Get repositories filtered by clone status."""
        return [
            metadata
            for metadata in self.metadata.values()
            if metadata.clone_status == clone_status
        ]

    def get_repositories_by_access(
        self, access_level: AccessLevel
    ) -> List[RepositoryMetadata]:
        """Get repositories filtered by access level."""
        return [
            metadata
            for metadata in self.metadata.values()
            if metadata.access_level == access_level
        ]

    def get_outdated_repositories(self, days: int = 30) -> List[RepositoryMetadata]:
        """Get repositories that haven't been synced in specified days."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        outdated = []

        for metadata in self.metadata.values():
            if metadata.last_sync_date:
                try:
                    last_sync = datetime.fromisoformat(
                        metadata.last_sync_date.replace("Z", "+00:00")
                    )
                    if last_sync < cutoff_date:
                        outdated.append(metadata)
                except ValueError:
                    outdated.append(metadata)  # Invalid date format
            else:
                outdated.append(metadata)  # Never synced

        return outdated

    def generate_metadata_report(self) -> Dict[str, Any]:
        """Generate comprehensive metadata report."""
        total_repos = len(self.metadata)

        # Count by status
        status_counts = {}
        for status in CloneStatus:
            status_counts[status.value] = len(self.get_repositories_by_status(status))

        # Count by access level
        access_counts = {}
        for access in AccessLevel:
            access_counts[access.value] = len(self.get_repositories_by_access(access))

        # Count by type
        type_counts = {}
        for metadata in self.metadata.values():
            repo_type = metadata.repo_type
            type_counts[repo_type] = type_counts.get(repo_type, 0) + 1

        # Statistics
        total_stars = sum(m.stats.stars for m in self.metadata.values())
        total_forks = sum(m.stats.forks for m in self.metadata.values())

        return {
            "total_repositories": total_repos,
            "status_breakdown": status_counts,
            "access_breakdown": access_counts,
            "type_breakdown": type_counts,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "outdated_repositories": len(self.get_outdated_repositories()),
            "last_update": datetime.now(timezone.utc).isoformat(),
        }


def main():
    """Main function for testing metadata management."""
    manager = RepositoryMetadataManager()

    # Example usage
    print("Repository Metadata Manager")
    print("=" * 50)

    # Generate report
    report = manager.generate_metadata_report()
    print(f"Total repositories: {report['total_repositories']}")
    print(f"Clone status breakdown: {report['status_breakdown']}")
    print(f"Access level breakdown: {report['access_breakdown']}")
    print(f"Repository type breakdown: {report['type_breakdown']}")


if __name__ == "__main__":
    main()

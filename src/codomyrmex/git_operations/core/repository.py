import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

from .git import (
    clone_repository,
    create_branch,
    get_current_branch,
    get_status,
    is_git_repository,
    prune_remote,
    pull_changes,
    push_changes,
)
from .metadata import (
    CloneStatus,
    RepositoryMetadataManager,
)

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent.parent / "src"
# sys.path.insert(0, str(src_dir))  # Removed sys.path manipulation

logger = get_logger(__name__)


class RepositoryType(Enum):
    """Types of repositories in the library."""

    OWN = "OWN"  # Own repositories for development/contributions
    USE = "USE"  # External repositories for usage only
    FORK = "FORK"  # Forked repositories for contributions


@dataclass
class Repository:
    """Represents a repository in the library."""

    repo_type: RepositoryType
    owner: str
    name: str
    url: str
    description: str
    local_path_suggestion: str

    @property
    def full_name(self) -> str:
        """Get the full repository name (owner/name)."""
        return f"{self.owner}/{self.name}"

    @property
    def is_development_repo(self) -> bool:
        """Check if this is a development repository."""
        return self.repo_type in [RepositoryType.OWN, RepositoryType.FORK]

    @property
    def is_readonly_repo(self) -> bool:
        """Check if this is a read-only repository."""
        return self.repo_type == RepositoryType.USE


class RepositoryManager:
    """Manages the repository library and Git operations with metadata tracking."""

    def __init__(
        self,
        library_file: str | None = None,
        base_path: str | None = None,
        metadata_file: str | None = None,
        github_token: str | None = None,
    ):
        """
        Initialize the repository manager.

        Args:
            library_file: Path to the repository library file
            base_path: Base path for cloning repositories
            metadata_file: Path to metadata JSON file
            github_token: GitHub personal access token for enhanced metadata
        """
        if library_file is None:
            library_file = os.path.join(
                os.path.dirname(__file__), "repository_library.txt"
            )

        if base_path is None:
            base_path = os.path.expanduser("~/Documents/GitHub")

        self.library_file = library_file
        self.base_path = Path(base_path)
        self.repositories: dict[str, Repository] = {}

        self.metadata_manager = RepositoryMetadataManager(
            metadata_file=metadata_file, github_token=github_token
        )

        self._load_repository_library()

    def _load_repository_library(self) -> None:
        """Load repositories from the library file."""
        if not os.path.exists(self.library_file):
            logger.warning("Repository library file not found: %s", self.library_file)
            return

        try:
            with open(self.library_file) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Parse repository entry
                    parts = line.split("|")
                    if len(parts) != 6:
                        logger.warning(
                            "Invalid repository entry at line %s: %s", line_num, line
                        )
                        continue

                    repo_type_str, owner, name, url, description, local_path = parts

                    try:
                        repo_type = RepositoryType(repo_type_str)
                    except ValueError:
                        logger.warning(
                            "Invalid repository type '%s' at line %s", repo_type_str, line_num
                        )
                        continue

                    repo = Repository(
                        repo_type=repo_type,
                        owner=owner,
                        name=name,
                        url=url,
                        description=description,
                        local_path_suggestion=local_path,
                    )

                    self.repositories[repo.full_name] = repo

            logger.info("Loaded %s repositories from library", len(self.repositories))

        except Exception as e:
            logger.error("Error loading repository library: %s", e)

    def list_repositories(
        self, repo_type: RepositoryType | None = None
    ) -> list[Repository]:
        """
        List repositories, optionally filtered by type.

        Args:
            repo_type: Filter by repository type

        Returns:
            List of repositories
        """
        repos = list(self.repositories.values())

        if repo_type:
            repos = [repo for repo in repos if repo.repo_type == repo_type]

        return sorted(repos, key=lambda r: (r.repo_type.value, r.owner, r.name))

    def get_repository(self, full_name: str) -> Repository | None:
        """
        Get a repository by full name (owner/name).

        Args:
            full_name: Repository full name (e.g., "docxology/docxology")

        Returns:
            Repository object or None if not found
        """
        return self.repositories.get(full_name)

    def search_repositories(self, query: str) -> list[Repository]:
        """
        Search repositories by name, owner, or description.

        Args:
            query: Search query

        Returns:
            List of matching repositories
        """
        query_lower = query.lower()
        matches = []

        for repo in self.repositories.values():
            if (
                query_lower in repo.name.lower()
                or query_lower in repo.owner.lower()
                or query_lower in repo.description.lower()
            ):
                matches.append(repo)

        return sorted(matches, key=lambda r: (r.repo_type.value, r.owner, r.name))

    def get_local_path(self, repo: Repository) -> Path:
        """
        Get the local path for a repository.

        Args:
            repo: Repository object

        Returns:
            Path object for the local repository
        """
        return self.base_path / repo.local_path_suggestion

    def clone_repository(self, full_name: str, custom_path: str | None = None) -> bool:
        """
        Clone a repository from the library with metadata tracking.

        Args:
            full_name: Repository full name (e.g., "docxology/docxology")
            custom_path: Custom local path (overrides suggestion)

        Returns:
            True if successful, False otherwise
        """
        repo = self.get_repository(full_name)
        if not repo:
            logger.error("Repository '%s' not found in library", full_name)
            return False

        local_path = Path(custom_path) if custom_path else self.get_local_path(repo)

        local_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Cloning %s to %s", repo.full_name, local_path)

        metadata = self.metadata_manager.create_or_update_metadata(
            full_name=repo.full_name,
            owner=repo.owner,
            name=repo.name,
            repo_type=repo.repo_type.value,
            url=repo.url,
            description=repo.description,
            local_path=str(local_path),
        )

        success = clone_repository(repo.url, str(local_path))

        if success:
            logger.info("Successfully cloned %s", repo.full_name)

            metadata.clone_date = datetime.now().isoformat()
            metadata.clone_status = CloneStatus.CLONED
            metadata.last_sync_date = datetime.now().isoformat()

            self.metadata_manager.update_local_repository_info(metadata)
            self.metadata_manager.update_repository_metadata(metadata)
            self.metadata_manager.save_metadata()

            # For development repositories, set up development branch if needed
            if repo.is_development_repo:
                self._setup_development_repo(str(local_path), repo)
        else:
            logger.error("Failed to clone %s", repo.full_name)
            metadata.clone_status = CloneStatus.ERROR
            self.metadata_manager.update_repository_metadata(metadata)
            self.metadata_manager.save_metadata()

        return success

    def _setup_development_repo(self, repo_path: str, repo: Repository) -> None:
        """
        Set up a development repository with appropriate branches.

        Args:
            repo_path: Local repository path
            repo: Repository object
        """
        try:
            current_branch = get_current_branch(repo_path)
            logger.info("Repository %s is on branch: %s", repo.full_name, current_branch)

            # For own repositories, create a development branch
            if repo.repo_type == RepositoryType.OWN:
                dev_branch = "develop"
                if current_branch != dev_branch:
                    create_branch(dev_branch, repo_path)
                    logger.info("Created development branch: %s", dev_branch)

        except Exception as e:
            logger.warning(
                "Could not set up development branches for %s: %s", repo.full_name, e
            )

    def update_repository(self, full_name: str, custom_path: str | None = None) -> bool:
        """
        Update a repository (pull latest changes).

        Args:
            full_name: Repository full name
            custom_path: Custom local path

        Returns:
            True if successful, False otherwise
        """
        repo = self.get_repository(full_name)
        if not repo:
            logger.error("Repository '%s' not found in library", full_name)
            return False

        local_path = Path(custom_path) if custom_path else self.get_local_path(repo)

        if not is_git_repository(str(local_path)):
            logger.error("Repository not found locally: %s", local_path)
            return False

        logger.info("Updating %s at %s", repo.full_name, local_path)

        current_branch = get_current_branch(str(local_path))
        if not current_branch:
            logger.error("Could not determine current branch for %s", repo.full_name)
            return False

        success = pull_changes("origin", current_branch, str(local_path))

        if success:
            logger.info("Successfully updated %s", repo.full_name)
        else:
            logger.error("Failed to update %s", repo.full_name)

        return success

    def get_repository_status(
        self, full_name: str, custom_path: str | None = None
    ) -> dict | None:
        """
        Get the status of a local repository.

        Args:
            full_name: Repository full name
            custom_path: Custom local path

        Returns:
            Status dictionary or None if not found
        """
        repo = self.get_repository(full_name)
        if not repo:
            logger.error("Repository '%s' not found in library", full_name)
            return None

        local_path = Path(custom_path) if custom_path else self.get_local_path(repo)

        if not is_git_repository(str(local_path)):
            return {"error": "Repository not found locally", "path": str(local_path)}

        status = get_status(str(local_path))
        current_branch = get_current_branch(str(local_path))

        return {
            "repository": repo.full_name,
            "path": str(local_path),
            "branch": current_branch,
            "status": status,
            "type": repo.repo_type.value,
            "is_development": repo.is_development_repo,
        }

    def bulk_clone(
        self,
        repo_type: RepositoryType | None = None,
        owner_filter: str | None = None,
        max_workers: int = 4,
    ) -> dict[str, bool]:
        """
        Clone multiple repositories in bulk.

        Args:
            repo_type: Filter by repository type
            owner_filter: Filter by owner name
            max_workers: Number of parallel threads

        Returns:
            Dictionary mapping repository names to success status
        """
        repos = self.list_repositories(repo_type)

        if owner_filter:
            repos = [repo for repo in repos if repo.owner == owner_filter]

        results = {}
        futures = {}

        logger.info(
            "Bulk cloning %s repositories with %s workers...", len(repos), max_workers
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for repo in repos:
                future = executor.submit(self.clone_repository, repo.full_name)
                futures[future] = repo.full_name

            for future in as_completed(futures):
                repo_name = futures[future]
                try:
                    success = future.result()
                    results[repo_name] = success
                except Exception as e:
                    logger.error("Error cloning %s: %s", repo_name, e)
                    results[repo_name] = False

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        logger.info("Bulk clone completed: %s/%s successful", successful, total)

        return results

    def bulk_update(
        self,
        repo_type: RepositoryType | None = None,
        owner_filter: str | None = None,
        max_workers: int = 4,
    ) -> dict[str, bool]:
        """
        Update multiple repositories in bulk.

        Args:
            repo_type: Filter by repository type
            owner_filter: Filter by owner name
            max_workers: Number of parallel threads

        Returns:
            Dictionary mapping repository names to success status
        """
        repos = self.list_repositories(repo_type)

        if owner_filter:
            repos = [repo for repo in repos if repo.owner == owner_filter]

        # Separate locally cloned repos from uncloned ones
        repos_to_update = []
        results = {}
        for repo in repos:
            local_path = self.get_local_path(repo)
            if is_git_repository(str(local_path)):
                repos_to_update.append(repo)
            else:
                logger.info("Skipping %s - not cloned locally", repo.full_name)
                results[repo.full_name] = False

        futures = {}

        logger.info(
            "Bulk updating %s repositories with %s workers...", len(repos_to_update), max_workers
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for repo in repos_to_update:
                future = executor.submit(self.update_repository, repo.full_name)
                futures[future] = repo.full_name

            for future in as_completed(futures):
                repo_name = futures[future]
                try:
                    success = future.result()
                    results[repo_name] = success
                except Exception as e:
                    logger.error("Error updating %s: %s", repo_name, e)
                    results[repo_name] = False

        successful = sum(1 for success in results.values() if success)
        total = len(repos_to_update)

        logger.info("Bulk update completed: %s/%s successful", successful, total)

        return results

    def sync_repository(self, full_name: str, custom_path: str | None = None) -> bool:
        """
        Sync a repository (pull and push).

        Args:
            full_name: Repository full name
            custom_path: Custom local path

        Returns:
            True if successful, False otherwise
        """
        # First update (pull)
        if not self.update_repository(full_name, custom_path):
            return False

        repo = self.get_repository(full_name)
        local_path = Path(custom_path) if custom_path else self.get_local_path(repo)

        # Then push
        logger.info("Syncing (pushing) %s...", repo.full_name)
        return push_changes(repository_path=str(local_path))

    def prune_repository(self, full_name: str, custom_path: str | None = None) -> bool:
        """
        Prune remote tracking branches for a repository.

        Args:
            full_name: Repository full name
            custom_path: Custom local path

        Returns:
            True if successful, False otherwise
        """
        repo = self.get_repository(full_name)
        if not repo:
            return False

        local_path = Path(custom_path) if custom_path else self.get_local_path(repo)

        if not is_git_repository(str(local_path)):
            return False

        logger.info("Pruning %s...", repo.full_name)
        return prune_remote("origin", str(local_path))

    def print_repository_summary(self) -> None:
        """Print a summary of all repositories in the library."""
        print("\n" + "=" * 80)
        print("CODOMYRMEX REPOSITORY LIBRARY SUMMARY")
        print("=" * 80)

        # Count by type
        type_counts = {}
        for repo in self.repositories.values():
            type_counts[repo.repo_type] = type_counts.get(repo.repo_type, 0) + 1

        print(f"\nTotal Repositories: {len(self.repositories)}")
        for repo_type, count in type_counts.items():
            print(f"  {repo_type.value}: {count}")

        # List by type
        for repo_type in RepositoryType:
            repos = self.list_repositories(repo_type)
            if repos:
                print(f"\n{repo_type.value} REPOSITORIES ({len(repos)}):")
                print("-" * 40)

                for repo in repos:
                    local_path = self.get_local_path(repo)
                    exists = "✅" if is_git_repository(str(local_path)) else "❌"
                    print(f"  {exists} {repo.full_name}")
                    print(f"     {repo.description}")
                    print(f"     Local: {local_path}")
                    print()


def main():
    """Main function for testing the repository manager."""
    manager = RepositoryManager()

    # Print summary
    manager.print_repository_summary()

    # Example usage
    print("\n" + "=" * 80)
    print("EXAMPLE OPERATIONS")
    print("=" * 80)

    # Search for docxology repositories
    docx_repos = manager.search_repositories("docxology")
    print(f"\nFound {len(docx_repos)} docxology repositories:")
    for repo in docx_repos[:3]:  # Show first 3
        print(f"  - {repo.full_name}: {repo.description}")

    # List development repositories
    dev_repos = manager.list_repositories(RepositoryType.OWN)
    print(f"\nDevelopment repositories: {len(dev_repos)}")

    # Example: Clone a repository (commented out for safety)
    # success = manager.clone_repository("docxology/docxology")
    # print(f"Clone result: {success}")


if __name__ == "__main__":
    main()

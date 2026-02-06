import os
import subprocess
import time

from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
from codomyrmex.performance import monitor_performance, performance_context

#!/usr/bin/env python3

"""Git Operations Manager for Codomyrmex.

This module provides a standardized interface and a set of tools for performing
common Git actions programmatically within the Codomyrmex ecosystem.
"""

# Add project root for sibling module imports if run directly
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
# if PROJECT_ROOT not in sys.path:
#     pass

logger = get_logger(__name__)

# Import performance monitoring
try:

    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    # Create no-op decorators
    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):

            return func

        return decorator

    class performance_context:
        """
        A class for handling performance_context operations.
        """
        def __init__(self, context_name: str = "unknown_context", *args, **kwargs):
            """Initialize performance context (fallback)."""
            self.context_name = context_name
            self.start_time = 0

        def __enter__(self):
            """Enter context."""
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Exit context."""
            duration = time.time() - self.start_time
            logger.debug(f"Exiting performance context: {self.context_name} (Duration: {duration:.4f}s)")

def check_git_availability() -> bool:
    """Check if Git is available on the system."""
    try:
        result = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, check=True
        )
        version = result.stdout.strip()
        logger.info(f"Git is available: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Git is not available on this system")
        return False

def is_git_repository(path: str = None) -> bool:
    """Check if the given path is a Git repository."""
    if path is None:
        path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False

@monitor_performance("git_initialize_repository")
def initialize_git_repository(path: str, initial_commit: bool = True) -> bool:
    """Initialize a new Git repository at the specified path."""
    try:
        logger.info(f"Initializing Git repository at: {path}")

        # Initialize repository
        result = subprocess.run(
            ["git", "init"], cwd=path, capture_output=True, text=True, check=True
        )

        if initial_commit:
            # Create initial commit only if there are no commits yet
            try:
                # Check if there are any commits
                result = subprocess.run(
                    ["git", "rev-list", "--count", "HEAD"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                has_commits = result.returncode == 0 and int(result.stdout.strip()) > 0
            except (ValueError, subprocess.SubprocessError):
                has_commits = False

            if not has_commits:
                # Create initial commit
                readme_path = os.path.join(path, "README.md")
                if not os.path.exists(readme_path):
                    with open(readme_path, "w") as f:
                        f.write("# Project\n\nInitial commit.\n")

                subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
                subprocess.run(
                    [
                        "git",
                        "-c",
                        "user.email=system@codomyrmex.dev",
                        "-c",
                        "user.name=Codomyrmex System",
                        "commit",
                        "-m",
                        "Initial commit",
                    ],
                    cwd=path,
                    check=True,
                )

        logger.info("Git repository initialized successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to initialize Git repository: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error initializing repository: {e}")
        return False

@monitor_performance("git_clone_repository")
def clone_repository(url: str, destination: str, branch: str = None) -> bool:
    """Clone a Git repository to the specified destination."""
    try:
        logger.info(f"Cloning repository from {url} to {destination}")

        cmd = ["git", "clone"]
        if branch:
            cmd.extend(["-b", branch])
        cmd.extend([url, destination])

        subprocess.run(cmd, capture_output=True, text=True, check=True)

        logger.info("Repository cloned successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error cloning repository: {e}")
        return False

def create_branch(branch_name: str, repository_path: str = None) -> bool:
    """Create and switch to a new Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Creating new branch '{branch_name}' in {repository_path}")

        # Create and switch to new branch
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Branch '{branch_name}' created and checked out successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create branch '{branch_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating branch: {e}")
        return False

def switch_branch(branch_name: str, repository_path: str = None) -> bool:
    """Switch to an existing Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Switching to branch '{branch_name}' in {repository_path}")

        subprocess.run(
            ["git", "checkout", branch_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Switched to branch '{branch_name}' successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to switch to branch '{branch_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error switching branch: {e}")
        return False

def get_current_branch(repository_path: str = None) -> str | None:
    """Get the name of the current Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        branch_name = result.stdout.strip()
        logger.debug(f"Current branch: {branch_name}")
        return branch_name

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get current branch: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting current branch: {e}")
        return None

def add_files(file_paths: list[str], repository_path: str = None) -> bool:
    """Add files to the Git staging area."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Adding files to staging area: {file_paths}")

        cmd = ["git", "add"] + file_paths
        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info("Files added to staging area successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add files to staging area: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error adding files: {e}")
        return False

def commit_changes(
    message: str,
    repository_path: str = None,
    author_name: str = None,
    author_email: str = None,
    stage_all: bool = True,
    file_paths: list[str] = None,
) -> str | None:
    """
    Commit staged changes with the given message.

    Args:
        message: Commit message
        repository_path: Path to repository (defaults to current directory)
        author_name: Override Git config for author name
        author_email: Override Git config for author email
        stage_all: If True, stages all tracked, modified files before committing (default: True)
        file_paths: Optional list of specific files to stage and commit (if provided, stage_all is ignored)

    Returns:
        SHA of the new commit on success, None on failure
    """
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Committing changes with message: {message}")

        # Stage files if needed
        if file_paths:
            # Stage specific files
            if not add_files(file_paths, repository_path):
                logger.error("Failed to stage files for commit")
                return None
        elif stage_all:
            # Stage all tracked, modified files
            subprocess.run(
                ["git", "add", "-u"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug("Staged all tracked, modified files")

        # Build commit command
        cmd = ["git", "commit"]

        # Add author override if provided
        if author_name and author_email:
            cmd.extend(["--author", f"{author_name} <{author_email}>"])
        elif author_name:
            # If only name provided, try to get email from config or use name only
            email_result = subprocess.run(
                ["git", "config", "user.email"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=False,
            )
            email = email_result.stdout.strip() if email_result.returncode == 0 else ""
            if email:
                cmd.extend(["--author", f"{author_name} <{email}>"])
            else:
                cmd.extend(["--author", author_name])
        elif author_email:
            # If only email provided, try to get name from config
            name_result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=False,
            )
            name = name_result.stdout.strip() if name_result.returncode == 0 else "Unknown"
            cmd.extend(["--author", f"{name} <{author_email}>"])

        # Add commit message
        cmd.extend(["-m", message])

        # Execute commit
        result = subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Get commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commit_sha = sha_result.stdout.strip()
        logger.info(f"Changes committed successfully: {commit_sha[:8]}")
        return commit_sha

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to commit changes: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error committing changes: {e}")
        return None

def push_changes(
    remote: str = "origin", branch: str = None, repository_path: str = None
) -> bool:
    """Push committed changes to a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    if branch is None:
        branch = get_current_branch(repository_path)
        if not branch:
            logger.error("Could not determine current branch for push")
            return False

    try:
        logger.info(f"Pushing changes to {remote}/{branch}")

        subprocess.run(
            ["git", "push", remote, branch],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info("Changes pushed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to push changes: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error pushing changes: {e}")
        return False

def pull_changes(
    remote: str = "origin", branch: str = None, repository_path: str = None
) -> bool:
    """Pull changes from a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    if branch is None:
        branch = get_current_branch(repository_path)
        if not branch:
            logger.error("Could not determine current branch for pull")
            return False

    try:
        logger.info(f"Pulling changes from {remote}/{branch}")

        subprocess.run(
            ["git", "pull", remote, branch],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info("Changes pulled successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to pull changes: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error pulling changes: {e}")
        return False

def get_status(repository_path: str = None) -> dict[str, any]:
    """Get the current Git repository status."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Getting Git repository status")

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        status_lines = (
            result.stdout.strip().split("\n") if result.stdout.strip() else []
        )

        status_info = {
            "modified": [],
            "added": [],
            "deleted": [],
            "renamed": [],
            "untracked": [],
            "clean": len(status_lines) == 0,
        }

        for line in status_lines:
            if not line.strip():
                continue

            # Git status --porcelain format: XY filename
            # X = index status, Y = worktree status
            if len(line) < 3:
                continue

            index_status = line[0]
            worktree_status = line[1]
            filename = line[3:]  # Skip the space after status codes

            # Check index status (staged changes)
            if index_status == "A":
                status_info["added"].append(filename)
            elif index_status == "M":
                status_info["modified"].append(filename)
            elif index_status == "D":
                status_info["deleted"].append(filename)
            elif index_status == "R":
                status_info["renamed"].append(filename)

            # Check worktree status (unstaged changes)
            if worktree_status == "M":
                if filename not in status_info["modified"]:
                    status_info["modified"].append(filename)
            elif worktree_status == "D":
                if filename not in status_info["deleted"]:
                    status_info["deleted"].append(filename)

            # Untracked files
            if index_status == "?" and worktree_status == "?":
                status_info["untracked"].append(filename)

        logger.debug(f"Repository status: {len(status_lines)} changes")
        return status_info

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get repository status: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error getting status: {e}")
        return {"error": str(e)}

def get_commit_history(
    limit: int = 10, repository_path: str = None
) -> list[dict[str, str]]:
    """Get recent commit history."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug(f"Getting commit history (limit: {limit})")

        result = subprocess.run(
            [
                "git",
                "log",
                "--oneline",
                "-n",
                str(limit),
                "--pretty=format:%H|%an|%ae|%ad|%s",
            ],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commits = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append(
                        {
                            "hash": parts[0],
                            "author_name": parts[1],
                            "author_email": parts[2],
                            "date": parts[3],
                            "message": parts[4],
                        }
                    )

        logger.debug(f"Retrieved {len(commits)} commits")
        return commits

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get commit history: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting commit history: {e}")
        return []

def merge_branch(
    source_branch: str,
    target_branch: str = None,
    repository_path: str = None,
    strategy: str = None,
) -> bool:
    """Merge a source branch into the target branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    if target_branch is None:
        target_branch = get_current_branch(repository_path)
        if not target_branch:
            logger.error("Could not determine target branch for merge")
            return False

    try:
        logger.info(
            f"Merging branch '{source_branch}' into '{target_branch}' in {repository_path}"
        )

        # Switch to target branch first
        if not switch_branch(target_branch, repository_path):
            logger.error(f"Failed to switch to target branch '{target_branch}'")
            return False

        # Prepare merge command
        cmd = ["git", "merge"]
        if strategy:
            cmd.extend(["-s", strategy])
        cmd.append(source_branch)

        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info(f"Successfully merged '{source_branch}' into '{target_branch}'")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to merge branch '{source_branch}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error merging branch: {e}")
        return False

def rebase_branch(
    target_branch: str, repository_path: str = None, interactive: bool = False
) -> bool:
    """Rebase current branch onto target branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        current_branch = get_current_branch(repository_path)
        logger.info(
            f"Rebasing branch '{current_branch}' onto '{target_branch}' in {repository_path}"
        )

        cmd = ["git", "rebase"]
        if interactive:
            cmd.append("-i")
        cmd.append(target_branch)

        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info(f"Successfully rebased '{current_branch}' onto '{target_branch}'")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to rebase onto '{target_branch}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error rebasing branch: {e}")
        return False

def create_tag(tag_name: str, message: str = None, repository_path: str = None) -> bool:
    """Create a Git tag."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Creating tag '{tag_name}' in {repository_path}")

        cmd = ["git", "tag"]
        if message:
            cmd.extend(["-a", tag_name, "-m", message])
        else:
            cmd.append(tag_name)

        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info(f"Tag '{tag_name}' created successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create tag '{tag_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating tag: {e}")
        return False

def list_tags(repository_path: str = None) -> list[str]:
    """List all Git tags."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Listing Git tags")

        result = subprocess.run(
            ["git", "tag", "-l"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        tags = [tag.strip() for tag in result.stdout.strip().split("\n") if tag.strip()]
        logger.debug(f"Found {len(tags)} tags")
        return tags

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list tags: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error listing tags: {e}")
        return []

def stash_changes(message: str = None, repository_path: str = None) -> bool:
    """Stash current changes."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Stashing changes in {repository_path}")

        cmd = ["git", "stash"]
        if message:
            cmd.extend(["push", "-m", message])

        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info("Changes stashed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stash changes: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error stashing changes: {e}")
        return False

def apply_stash(stash_ref: str = None, repository_path: str = None) -> bool:
    """Apply stashed changes."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Applying stash in {repository_path}")

        cmd = ["git", "stash", "apply"]
        if stash_ref:
            cmd.append(stash_ref)

        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info("Stash applied successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to apply stash: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error applying stash: {e}")
        return False

def list_stashes(repository_path: str = None) -> list[dict[str, str]]:
    """List all stashes."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Listing Git stashes")

        result = subprocess.run(
            ["git", "stash", "list"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        stashes = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                # Parse stash format: stash@{0}: WIP on branch: message
                parts = line.split(": ", 2)
                if len(parts) >= 2:
                    stashes.append(
                        {
                            "ref": parts[0],
                            "branch_info": parts[1] if len(parts) > 1 else "",
                            "message": parts[2] if len(parts) > 2 else "",
                        }
                    )

        logger.debug(f"Found {len(stashes)} stashes")
        return stashes

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list stashes: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error listing stashes: {e}")
        return []

# ==========================================
# Phase 13: Core Git Enhancements
# ==========================================

# --- Remote Management ---

def add_remote(name: str, url: str, repository_path: str = None) -> bool:
    """Add a new remote to the repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Adding remote '{name}' ({url}) in {repository_path}")
        subprocess.run(
            ["git", "remote", "add", name, url],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add remote '{name}': {e}")
        return False

def remove_remote(name: str, repository_path: str = None) -> bool:
    """Remove a remote from the repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Removing remote '{name}' in {repository_path}")
        subprocess.run(
            ["git", "remote", "remove", name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to remove remote '{name}': {e}")
        return False

def list_remotes(repository_path: str = None) -> list[dict[str, str]]:
    """List all remotes in the repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        remotes = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    remotes.append({"name": parts[0], "url": parts[1]})
        # Deduplicate by name (git remote -v shows fetch and push separately)
        unique_remotes = {r["name"]: r["url"] for r in remotes}
        return [{"name": k, "url": v} for k, v in unique_remotes.items()]
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list remotes: {e}")
        return []

def fetch_remote(remote: str = "origin", repository_path: str = None) -> bool:
    """Fetch changes from a remote."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Fetching from remote '{remote}' in {repository_path}")
        subprocess.run(
            ["git", "fetch", remote],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to fetch remote '{remote}': {e}")
        return False

def prune_remote(remote: str = "origin", repository_path: str = None) -> bool:
    """Prune remote tracking branches."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Pruning remote '{remote}' in {repository_path}")
        subprocess.run(
            ["git", "remote", "prune", remote],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to prune remote '{remote}': {e}")
        return False

# --- State Management ---

def reset_changes(mode: str = "mixed", commit: str = "HEAD", repository_path: str = None) -> bool:
    """Reset current HEAD to the specified state."""
    # modes: soft, mixed, hard
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Resetting ({mode}) to '{commit}' in {repository_path}")
        cmd = ["git", "reset", f"--{mode}", commit]
        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reset changes: {e}")
        return False

def revert_commit(commit_sha: str, repository_path: str = None) -> bool:
    """Revert a specific commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Reverting commit '{commit_sha}' in {repository_path}")
        # --no-edit to avoid opening editor for commit message
        subprocess.run(
            ["git", "revert", "--no-edit", commit_sha],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to revert commit '{commit_sha}': {e}")
        return False

def clean_repository(force: bool = False, directories: bool = False, repository_path: str = None) -> bool:
    """Clean untracked files from the repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        cmd = ["git", "clean", "-f"]
        if force:
            cmd.append("-x") # Remove ignored files too if force is very true, typically just -f is enough for tracked, but here force param usually implies -f. Actually git clean requires -f.
            # Let's interpret 'force' as -x (ignored files) and always use -f.
            pass

        # Actually, standard git clean usage:
        # -f is required via configuration or flag.
        # -d for directories.
        # -x for ignored files.

        base_cmd = ["git", "clean", "-f"] # Force is required by default in most extensive configs
        if directories:
            base_cmd.append("-d")
        if force:
            base_cmd.append("-x")

        logger.info(f"Cleaning repository in {repository_path}")
        subprocess.run(
            base_cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clean repository: {e}")
        return False

# --- Analysis Tools ---

def get_diff(target: str = "HEAD", repository_path: str = None, cached: bool = False) -> str:
    """Get the diff of current changes against a target."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        cmd = ["git", "diff"]
        if cached:
            cmd.append("--cached")
        cmd.append(target)

        result = subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get diff: {e}")
        return ""
    except FileNotFoundError:
        return ""
    except Exception as e:
        logger.error(f"Unexpected error getting diff: {e}")
        return ""

def get_blame(file_path: str, repository_path: str = None) -> str:
    """Get the blame for a file."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "blame", file_path],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get blame for {file_path}: {e}")
        return ""

def get_commit_details(commit_sha: str, repository_path: str = None) -> dict:
    """Get detailed information about a specific commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        # format: hash|author|email|date|subject|body
        fmt = "%H|%an|%ae|%ad|%s|%b"
        result = subprocess.run(
            ["git", "show", "-s", f"--format={fmt}", commit_sha],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        parts = result.stdout.strip().split("|", 5)
        if len(parts) < 6:
            return {}

        return {
            "hash": parts[0],
            "author": parts[1],
            "email": parts[2],
            "date": parts[3],
            "subject": parts[4],
            "body": parts[5]
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get commit details for {commit_sha}: {e}")
        return {}

# --- Configuration Management ---

def get_config(key: str, repository_path: str = None) -> str | None:
    """Get a git configuration value."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=False, # Don't error if key not found, just return empty/None
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        logger.error(f"Error getting config {key}: {e}")
        return None

def set_config(key: str, value: str, scope: str = "local", repository_path: str = None) -> bool:
    """Set a git configuration value."""
    # scope: local, global, system
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        cmd = ["git", "config", f"--{scope}", key, value]
        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set config {key}: {e}")
        return False

# --- Advanced Workflows ---

def cherry_pick(commit_sha: str, repository_path: str = None) -> bool:
    """Cherry-pick a commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Cherry-picking {commit_sha} in {repository_path}")
        subprocess.run(
            ["git", "cherry-pick", commit_sha],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to cherry-pick {commit_sha}: {e}")
        # Abort cherry-pick if failed to avoid leaving repo in bad state?
        # Or let user handle conflict? Simple wrapper implies return False.
        try:
             subprocess.run(["git", "cherry-pick", "--abort"], cwd=repository_path, capture_output=True)
        except Exception as e:
            logger.debug(f"Cherry-pick abort cleanup failed: {e}")
        return False

def init_submodules(repository_path: str = None) -> bool:
    """Initialize and update submodules."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Initializing submodules in {repository_path}")
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to init submodules: {e}")
        return False

def update_submodules(repository_path: str = None) -> bool:
    """Update submodules to latest commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Updating submodules in {repository_path}")
        subprocess.run(
            ["git", "submodule", "update", "--remote", "--recursive"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to update submodules: {e}")
        return False

def get_diff_files(
    file_path: str = None, staged: bool = False, repository_path: str = None
) -> str:
    """Get diff of changes."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Getting Git diff")

        cmd = ["git", "diff"]
        if staged:
            cmd.append("--staged")
        if file_path:
            cmd.append(file_path)

        result = subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.debug(f"Retrieved diff ({len(result.stdout)} characters)")
        return result.stdout

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get diff: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error getting diff: {e}")
        return ""

def reset_changes(
    mode: str = "mixed", target: str = "HEAD", repository_path: str = None
) -> bool:
    """Reset repository to a specific state."""
    if repository_path is None:
        repository_path = os.getcwd()

    valid_modes = ["soft", "mixed", "hard"]
    if mode not in valid_modes:
        logger.error(f"Invalid reset mode '{mode}'. Valid modes: {valid_modes}")
        return False

    try:
        logger.info(
            f"Resetting repository to '{target}' with mode '{mode}' in {repository_path}"
        )

        cmd = ["git", "reset", f"--{mode}", target]
        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info("Repository reset successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reset repository: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error resetting repository: {e}")
        return False

def add_remote(
    remote_name: str, url: str, repository_path: str = None
) -> bool:
    """Add a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Adding remote '{remote_name}' with URL: {url}")

        subprocess.run(
            ["git", "remote", "add", remote_name, url],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Remote '{remote_name}' added successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add remote '{remote_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error adding remote: {e}")
        return False

def remove_remote(remote_name: str, repository_path: str = None) -> bool:
    """Remove a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Removing remote '{remote_name}'")

        subprocess.run(
            ["git", "remote", "remove", remote_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Remote '{remote_name}' removed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to remove remote '{remote_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error removing remote: {e}")
        return False

def list_remotes(repository_path: str = None) -> list[dict[str, str]]:
    """List all remote repositories."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Listing Git remotes")

        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        remotes = []
        seen_remotes = set()
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    url = parts[1]
                    fetch_or_push = parts[2] if len(parts) > 2 else "fetch"

                    if name not in seen_remotes:
                        remotes.append({
                            "name": name,
                            "url": url,
                            "fetch": url if fetch_or_push == "(fetch)" else None,
                            "push": url if fetch_or_push == "(push)" else None,
                        })
                        seen_remotes.add(name)
                    else:
                        # Update existing remote with push URL if needed
                        for remote in remotes:
                            if remote["name"] == name and fetch_or_push == "(push)":
                                remote["push"] = url

        logger.debug(f"Found {len(remotes)} remotes")
        return remotes

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list remotes: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error listing remotes: {e}")
        return []

def get_config(key: str, repository_path: str = None, global_config: bool = False) -> str | None:
    """Get a Git configuration value."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug(f"Getting Git config: {key}")

        cmd = ["git", "config"]
        if global_config:
            cmd.append("--global")
        cmd.extend(["--get", key])

        result = subprocess.run(
            cmd,
            cwd=repository_path if not global_config else None,
            capture_output=True,
            text=True,
            check=True,
        )

        value = result.stdout.strip()
        logger.debug(f"Config value for {key}: {value}")
        return value

    except subprocess.CalledProcessError as e:
        logger.debug(f"Config key '{key}' not found or not set")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting config: {e}")
        return None

def set_config(
    key: str, value: str, repository_path: str = None, global_config: bool = False
) -> bool:
    """Set a Git configuration value."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Setting Git config: {key} = {value}")

        cmd = ["git", "config"]
        if global_config:
            cmd.append("--global")
        cmd.extend([key, value])

        subprocess.run(
            cmd,
            cwd=repository_path if not global_config else None,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Config '{key}' set successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set config '{key}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error setting config: {e}")
        return False

def cherry_pick(
    commit_sha: str, repository_path: str = None, no_commit: bool = False
) -> bool:
    """Cherry-pick a commit from another branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Cherry-picking commit: {commit_sha}")

        cmd = ["git", "cherry-pick"]
        if no_commit:
            cmd.append("--no-commit")
        cmd.append(commit_sha)

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Successfully cherry-picked commit {commit_sha[:8]}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to cherry-pick commit '{commit_sha}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error cherry-picking commit: {e}")
        return False

def amend_commit(
    message: str = None,
    repository_path: str = None,
    author_name: str = None,
    author_email: str = None,
    no_edit: bool = False,
) -> str | None:
    """Amend the last commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Amending last commit")

        cmd = ["git", "commit", "--amend"]

        if no_edit:
            if message:
                cmd.extend(["-m", message])
            else:
                cmd.append("--no-edit")
        elif message:
            cmd.extend(["-m", message])
        else:
            cmd.append("--no-edit")

        # Add author override if provided
        if author_name and author_email:
            cmd.extend(["--author", f"{author_name} <{author_email}>"])
        elif author_name:
            email_result = subprocess.run(
                ["git", "config", "user.email"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=False,
            )
            email = email_result.stdout.strip() if email_result.returncode == 0 else ""
            if email:
                cmd.extend(["--author", f"{author_name} <{email}>"])
            else:
                cmd.extend(["--author", author_name])
        elif author_email:
            name_result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=False,
            )
            name = name_result.stdout.strip() if name_result.returncode == 0 else "Unknown"
            cmd.extend(["--author", f"{name} <{author_email}>"])

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Get amended commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commit_sha = sha_result.stdout.strip()
        logger.info(f"Successfully amended commit: {commit_sha[:8]}")
        return commit_sha

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to amend commit: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error amending commit: {e}")
        return None

def fetch_changes(
    remote: str = "origin",
    branch: str = None,
    repository_path: str = None,
    prune: bool = False,
) -> bool:
    """Fetch changes from a remote repository without merging."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Fetching changes from {remote}")

        cmd = ["git", "fetch"]
        if prune:
            cmd.append("--prune")
        cmd.append(remote)
        if branch:
            cmd.append(branch)

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Successfully fetched changes from {remote}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to fetch changes from {remote}: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error fetching changes: {e}")
        return False

def get_commit_history_filtered(
    limit: int = 10,
    repository_path: str = None,
    since: str = None,
    until: str = None,
    author: str = None,
    branch: str = None,
    file_path: str = None,
) -> list[dict[str, str]]:
    """
    Get commit history with filters.

    Args:
        limit: Maximum number of commits to return
        repository_path: Path to repository
        since: Show commits after this date (ISO format or relative like "2 weeks ago")
        until: Show commits before this date (ISO format or relative)
        author: Filter by author name or email
        branch: Branch to show commits from
        file_path: Show only commits affecting this file

    Returns:
        List of commit dictionaries
    """
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug(f"Getting filtered commit history (limit: {limit})")

        cmd = [
            "git",
            "log",
            "--oneline",
            "-n",
            str(limit),
            "--pretty=format:%H|%an|%ae|%ad|%s",
        ]

        if since:
            cmd.extend(["--since", since])
        if until:
            cmd.extend(["--until", until])
        if author:
            cmd.extend(["--author", author])
        if file_path:
            cmd.append("--")
            cmd.append(file_path)

        if branch:
            cmd.append(branch)

        result = subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commits = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append(
                        {
                            "hash": parts[0],
                            "author_name": parts[1],
                            "author_email": parts[2],
                            "date": parts[3],
                            "message": parts[4],
                        }
                    )

        logger.debug(f"Retrieved {len(commits)} filtered commits")
        return commits

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get filtered commit history: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting filtered commit history: {e}")
        return []

if __name__ == "__main__":
    # Ensure logging is set up when script is run directly
    setup_logging()
    logger.info("Executing git_manager.py directly for testing example.")

    # Example usage
    if check_git_availability():
        logger.info("Git operations available. Testing basic functionality...")

        # Test repository detection
        is_repo = is_git_repository()
        logger.info(f"Current directory is Git repository: {is_repo}")

        if is_repo:
            # Test getting status
            status = get_status()
            logger.info(f"Repository status: {status}")

            # Test getting current branch
            branch = get_current_branch()
            logger.info(f"Current branch: {branch}")

            # Test getting commit history
            commits = get_commit_history(5)
            logger.info(f"Recent commits: {len(commits)}")
    else:
        logger.warning("Git is not available. Cannot test Git operations.")

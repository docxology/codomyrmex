#!/usr/bin/env python3
"""
Git Operations Manager for Codomyrmex.

This module provides a standardized interface and a set of tools for performing
common Git actions programmatically within the Codomyrmex ecosystem.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root for sibling module imports if run directly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
except ImportError:
    # Fallback for environments where logging_monitoring might not be discoverable
    import logging
    print("Warning: Could not import Codomyrmex logging. Using standard Python logging.", file=sys.stderr)
    def setup_logging():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    def get_logger(name):
        _logger = logging.getLogger(name)
        if not _logger.handlers:
            _handler = logging.StreamHandler(sys.stdout)
            _formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
            _handler.setFormatter(_formatter)
            _logger.addHandler(_handler)
            _logger.setLevel(logging.INFO)
        return _logger

logger = get_logger(__name__)

def check_git_availability() -> bool:
    """Check if Git is available on the system."""
    try:
        result = subprocess.run(['git', '--version'],
                              capture_output=True, text=True, check=True)
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
        result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                              cwd=path, capture_output=True, text=True, check=False)
        return result.returncode == 0
    except Exception:
        return False

def initialize_git_repository(path: str, initial_commit: bool = True) -> bool:
    """Initialize a new Git repository at the specified path."""
    try:
        logger.info(f"Initializing Git repository at: {path}")

        # Initialize repository
        result = subprocess.run(['git', 'init'], cwd=path,
                              capture_output=True, text=True, check=True)

        if initial_commit:
            # Create initial commit only if there are no commits yet
            try:
                # Check if there are any commits
                result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                                      cwd=path, capture_output=True, text=True, check=False)
                has_commits = result.returncode == 0 and int(result.stdout.strip()) > 0
            except (ValueError, subprocess.SubprocessError):
                has_commits = False
            
            if not has_commits:
                # Create initial commit
                readme_path = os.path.join(path, 'README.md')
                if not os.path.exists(readme_path):
                    with open(readme_path, 'w') as f:
                        f.write("# Project\n\nInitial commit.\n")

                subprocess.run(['git', 'add', 'README.md'], cwd=path, check=True)
                subprocess.run(['git', '-c', 'user.email=system@codomyrmex.dev',
                               '-c', 'user.name=Codomyrmex System',
                               'commit', '-m', 'Initial commit'], cwd=path, check=True)

        logger.info("Git repository initialized successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to initialize Git repository: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error initializing repository: {e}")
        return False

def clone_repository(url: str, destination: str, branch: str = None) -> bool:
    """Clone a Git repository to the specified destination."""
    try:
        logger.info(f"Cloning repository from {url} to {destination}")

        cmd = ['git', 'clone']
        if branch:
            cmd.extend(['-b', branch])
        cmd.extend([url, destination])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

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
        result = subprocess.run(['git', 'checkout', '-b', branch_name],
                              cwd=repository_path, capture_output=True, text=True, check=True)

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

        result = subprocess.run(['git', 'checkout', branch_name],
                              cwd=repository_path, capture_output=True, text=True, check=True)

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

def get_current_branch(repository_path: str = None) -> Optional[str]:
    """Get the name of the current Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        result = subprocess.run(['git', 'branch', '--show-current'],
                              cwd=repository_path, capture_output=True, text=True, check=True)

        branch_name = result.stdout.strip()
        logger.debug(f"Current branch: {branch_name}")
        return branch_name

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get current branch: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting current branch: {e}")
        return None

def add_files(file_paths: List[str], repository_path: str = None) -> bool:
    """Add files to the Git staging area."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Adding files to staging area: {file_paths}")

        cmd = ['git', 'add'] + file_paths
        result = subprocess.run(cmd, cwd=repository_path,
                              capture_output=True, text=True, check=True)

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

def commit_changes(message: str, repository_path: str = None) -> bool:
    """Commit staged changes with the given message."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Committing changes with message: {message}")

        result = subprocess.run(['git', 'commit', '-m', message],
                              cwd=repository_path, capture_output=True, text=True, check=True)

        logger.info("Changes committed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to commit changes: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error committing changes: {e}")
        return False

def push_changes(remote: str = "origin", branch: str = None, repository_path: str = None) -> bool:
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

        result = subprocess.run(['git', 'push', remote, branch],
                              cwd=repository_path, capture_output=True, text=True, check=True)

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

def pull_changes(remote: str = "origin", branch: str = None, repository_path: str = None) -> bool:
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

        result = subprocess.run(['git', 'pull', remote, branch],
                              cwd=repository_path, capture_output=True, text=True, check=True)

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

def get_status(repository_path: str = None) -> Dict[str, any]:
    """Get the current Git repository status."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Getting Git repository status")

        result = subprocess.run(['git', 'status', '--porcelain'],
                              cwd=repository_path, capture_output=True, text=True, check=True)

        status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

        status_info = {
            "modified": [],
            "added": [],
            "deleted": [],
            "renamed": [],
            "untracked": [],
            "clean": len(status_lines) == 0
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
            if index_status == 'A':
                status_info["added"].append(filename)
            elif index_status == 'M':
                status_info["modified"].append(filename)
            elif index_status == 'D':
                status_info["deleted"].append(filename)
            elif index_status == 'R':
                status_info["renamed"].append(filename)
            
            # Check worktree status (unstaged changes)
            if worktree_status == 'M':
                if filename not in status_info["modified"]:
                    status_info["modified"].append(filename)
            elif worktree_status == 'D':
                if filename not in status_info["deleted"]:
                    status_info["deleted"].append(filename)
            
            # Untracked files
            if index_status == '?' and worktree_status == '?':
                status_info["untracked"].append(filename)

        logger.debug(f"Repository status: {len(status_lines)} changes")
        return status_info

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get repository status: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error getting status: {e}")
        return {"error": str(e)}

def get_commit_history(limit: int = 10, repository_path: str = None) -> List[Dict[str, str]]:
    """Get recent commit history."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug(f"Getting commit history (limit: {limit})")

        result = subprocess.run(
            ['git', 'log', '--oneline', '-n', str(limit), '--pretty=format:%H|%an|%ae|%ad|%s'],
            cwd=repository_path, capture_output=True, text=True, check=True
        )

        commits = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split('|', 4)
                if len(parts) == 5:
                    commits.append({
                        "hash": parts[0],
                        "author_name": parts[1],
                        "author_email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })

        logger.debug(f"Retrieved {len(commits)} commits")
        return commits

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get commit history: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting commit history: {e}")
        return []

def merge_branch(source_branch: str, target_branch: str = None, repository_path: str = None, 
                 strategy: str = None) -> bool:
    """Merge a source branch into the target branch."""
    if repository_path is None:
        repository_path = os.getcwd()
    
    if target_branch is None:
        target_branch = get_current_branch(repository_path)
        if not target_branch:
            logger.error("Could not determine target branch for merge")
            return False

    try:
        logger.info(f"Merging branch '{source_branch}' into '{target_branch}' in {repository_path}")

        # Switch to target branch first
        if not switch_branch(target_branch, repository_path):
            logger.error(f"Failed to switch to target branch '{target_branch}'")
            return False

        # Prepare merge command
        cmd = ['git', 'merge']
        if strategy:
            cmd.extend(['-s', strategy])
        cmd.append(source_branch)

        result = subprocess.run(cmd, cwd=repository_path, 
                              capture_output=True, text=True, check=True)

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

def rebase_branch(target_branch: str, repository_path: str = None, interactive: bool = False) -> bool:
    """Rebase current branch onto target branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        current_branch = get_current_branch(repository_path)
        logger.info(f"Rebasing branch '{current_branch}' onto '{target_branch}' in {repository_path}")

        cmd = ['git', 'rebase']
        if interactive:
            cmd.append('-i')
        cmd.append(target_branch)

        result = subprocess.run(cmd, cwd=repository_path,
                              capture_output=True, text=True, check=True)

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

        cmd = ['git', 'tag']
        if message:
            cmd.extend(['-a', tag_name, '-m', message])
        else:
            cmd.append(tag_name)

        result = subprocess.run(cmd, cwd=repository_path,
                              capture_output=True, text=True, check=True)

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

def list_tags(repository_path: str = None) -> List[str]:
    """List all Git tags."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Listing Git tags")

        result = subprocess.run(['git', 'tag', '-l'], cwd=repository_path,
                              capture_output=True, text=True, check=True)

        tags = [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
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

        cmd = ['git', 'stash']
        if message:
            cmd.extend(['push', '-m', message])

        result = subprocess.run(cmd, cwd=repository_path,
                              capture_output=True, text=True, check=True)

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

        cmd = ['git', 'stash', 'apply']
        if stash_ref:
            cmd.append(stash_ref)

        result = subprocess.run(cmd, cwd=repository_path,
                              capture_output=True, text=True, check=True)

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

def list_stashes(repository_path: str = None) -> List[Dict[str, str]]:
    """List all stashes."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Listing Git stashes")

        result = subprocess.run(['git', 'stash', 'list'], cwd=repository_path,
                              capture_output=True, text=True, check=True)

        stashes = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                # Parse stash format: stash@{0}: WIP on branch: message
                parts = line.split(': ', 2)
                if len(parts) >= 2:
                    stashes.append({
                        "ref": parts[0],
                        "branch_info": parts[1] if len(parts) > 1 else "",
                        "message": parts[2] if len(parts) > 2 else ""
                    })

        logger.debug(f"Found {len(stashes)} stashes")
        return stashes

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list stashes: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error listing stashes: {e}")
        return []

def get_diff(file_path: str = None, staged: bool = False, repository_path: str = None) -> str:
    """Get diff of changes."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Getting Git diff")

        cmd = ['git', 'diff']
        if staged:
            cmd.append('--staged')
        if file_path:
            cmd.append(file_path)

        result = subprocess.run(cmd, cwd=repository_path,
                              capture_output=True, text=True, check=True)

        logger.debug(f"Retrieved diff ({len(result.stdout)} characters)")
        return result.stdout

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get diff: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error getting diff: {e}")
        return ""

def reset_changes(mode: str = "mixed", target: str = "HEAD", repository_path: str = None) -> bool:
    """Reset repository to a specific state."""
    if repository_path is None:
        repository_path = os.getcwd()

    valid_modes = ["soft", "mixed", "hard"]
    if mode not in valid_modes:
        logger.error(f"Invalid reset mode '{mode}'. Valid modes: {valid_modes}")
        return False

    try:
        logger.info(f"Resetting repository to '{target}' with mode '{mode}' in {repository_path}")

        cmd = ['git', 'reset', f'--{mode}', target]
        result = subprocess.run(cmd, cwd=repository_path,
                              capture_output=True, text=True, check=True)

        logger.info(f"Repository reset successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reset repository: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error resetting repository: {e}")
        return False

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

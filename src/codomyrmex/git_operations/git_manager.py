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

            status_code = line[:2]
            filename = line[3:]

            if status_code[0] in ['M', 'A', 'D', 'R']:
                if 'M' in status_code:
                    status_info["modified"].append(filename)
                if 'A' in status_code:
                    status_info["added"].append(filename)
                if 'D' in status_code:
                    status_info["deleted"].append(filename)
                if 'R' in status_code:
                    status_info["renamed"].append(filename)
            elif status_code[0] == '?':
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

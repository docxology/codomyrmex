import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.performance import monitor_performance

logger = get_logger(__name__)

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
    except Exception as e:
        logger.warning("Failed to check if %s is a git repository: %s", path, e)
        return False

@mcp_tool()
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

@mcp_tool()
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


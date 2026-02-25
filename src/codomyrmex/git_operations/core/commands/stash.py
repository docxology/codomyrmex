import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)

@mcp_tool()
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

@mcp_tool()
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

@mcp_tool()
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


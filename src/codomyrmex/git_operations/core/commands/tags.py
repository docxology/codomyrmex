import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)

@mcp_tool()
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

@mcp_tool()
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


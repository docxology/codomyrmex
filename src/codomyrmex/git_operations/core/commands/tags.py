import os
import subprocess

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

_GIT_TIMEOUT = 60  # seconds

logger = get_logger(__name__)


@mcp_tool(name="git_create_tag")
def create_tag(
    tag_name: str, message: str | None = None, repository_path: str | None = None
) -> bool:
    """Create a Git tag."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Creating tag '%s' in %s", tag_name, repository_path)

        cmd = ["git", "tag"]
        if message:
            cmd.extend(["-a", tag_name, "-m", message])
        else:
            cmd.append(tag_name)

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Tag '%s' created successfully", tag_name)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to create tag '%s': %s", tag_name, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error creating tag: %s", e)
        return False


@mcp_tool(name="git_list_tags")
def list_tags(repository_path: str | None = None) -> list[str]:
    """list all Git tags."""
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
            timeout=_GIT_TIMEOUT,
        )

        tags = [tag.strip() for tag in result.stdout.strip().split("\n") if tag.strip()]
        logger.debug("Found %s tags", len(tags))
        return tags

    except subprocess.CalledProcessError as e:
        logger.error("Failed to list tags: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error listing tags: %s", e)
        return []

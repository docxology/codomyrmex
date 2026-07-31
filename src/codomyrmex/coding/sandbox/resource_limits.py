"""
Resource Limits Configuration

Defines default resource limits and Docker security arguments.
"""

import json
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Path to the custom seccomp profile (relative to this file)
_SECCOMP_PATH = Path(__file__).parent / "seccomp_profile.json"


def _seccomp_opt() -> list[str]:
    """Return ``--security-opt seccomp=…`` if the profile file exists."""
    if _SECCOMP_PATH.is_file():
        return [f"--security-opt=seccomp={_SECCOMP_PATH}"]
    logger.warning("Seccomp profile not found at %s", _SECCOMP_PATH)
    return []


# Default Docker run arguments for security
DEFAULT_DOCKER_ARGS = [
    "--network=none",  # No network access
    "--cap-drop=ALL",  # Drop all capabilities
    "--security-opt=no-new-privileges",  # Prevent privilege escalation
    "--read-only",  # Read-only container
    "--memory=256m",  # Memory limit
    "--memory-swap=256m",  # Disable swap
    "--cpus=0.5",  # CPU limit
    "--pids-limit=50",  # Process limit
    *_seccomp_opt(),
]

"""System Context Module.

This module aggregates system information into a standardized context format
consumable by Agents.
"""

from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.system_discovery.reporting.profilers import (
    EnvironmentProfiler,
    HardwareProfiler,
)

from .discovery_engine import SystemDiscovery

logger = get_logger(__name__)


def get_system_context(root_dir: str = ".") -> dict[str, Any]:
    """
    Get the current system context for agents.

    Args:
        root_dir: Root directory of the system

    Returns:
        Dictionary containing system context (structure, health, hardware, etc.)
    """
    try:
        engine = SystemDiscovery(Path(root_dir))

        # Gather information from various components
        hw_info = HardwareProfiler.get_hardware_info()
        env_info = EnvironmentProfiler.get_environment_info()

        # Get module list
        # We perform a quick discovery or use an existing one if possible
        inventory = engine.scan_system()

        context = {
            "system_root": str(Path(root_dir).absolute()),
            "platform": hw_info["os"],
            "os": hw_info,
            "environment": env_info,
            "modules": list(inventory["modules"].keys()),
            "stats": inventory["stats"],
            "capabilities": [
                "python",
                "git" if "git_operations" in inventory["modules"] else None,
            ],
            "health_status": "unknown",
        }

        # Add specific capabilities if tools are found on path
        import shutil
        if shutil.which("docker"):
            context["capabilities"].append("docker")

        # Filter None from capabilities
        context["capabilities"] = [c for c in context["capabilities"] if c is not None]

        return context

    except Exception as e:
        logger.error("Failed to get system context: %s", e)
        return {"error": str(e)}

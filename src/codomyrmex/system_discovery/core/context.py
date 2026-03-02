
"""System Context Module.

This module aggregates system information into a standardized context format
consumable by Agents.
"""

from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from ..health.health_checker import HealthChecker
from .discovery_engine import SystemDiscovery

# from .capability_scanner import CapabilityScanner # Optional, might be heavy

logger = get_logger(__name__)

def get_system_context(root_dir: str = ".") -> dict[str, Any]:
    """
    Get the current system context for agents.

    Args:
        root_dir: Root directory of the system

    Returns:
        Dictionary containing system context (structure, health, etc.)
    """
    try:
        SystemDiscovery(Path(root_dir))
        HealthChecker()

        # Determine basic structure
        # This is a lightweight context, not a full index

        context = {
            "system_root": root_dir,
            "modules": [], # List of available modules
            "health_status": "unknown"
        }

        # Get module list (simplified)
        # engine.discover() might be expensive, so maybe just list top level?
        # For now, let's just return what we know is statically available or quick to check.

        # Assuming engine has a quick scan method or we use it lightly
        # Lightweight implementation to avoid heavy computation on every context call.

        context["platform"] = "codomyrmex"
        context["capabilities"] = ["python", "git", "cli"]

        return context

    except Exception as e:
        logger.error(f"Failed to get system context: {e}")
        return {"error": str(e)}

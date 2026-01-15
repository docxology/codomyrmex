
"""System Context Module.

This module aggregates system information into a standardized context format
consumable by Agents.
"""

from typing import Any, Dict

from pathlib import Path

from codomyrmex.logging_monitoring import get_logger
from .discovery_engine import SystemDiscovery
from .health_checker import HealthChecker
# from .capability_scanner import CapabilityScanner # Optional, might be heavy

logger = get_logger(__name__)

def get_system_context(root_dir: str = ".") -> Dict[str, Any]:
    """
    Get the current system context for agents.
    
    Args:
        root_dir: Root directory of the system
        
    Returns:
        Dictionary containing system context (structure, health, etc.)
    """
    try:
        engine = SystemDiscovery(Path(root_dir))
        health = HealthChecker()
        
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
        # For this implementation, we will mock/simplify to avoid heavy computation on every context call.
        
        context["platform"] = "codomyrmex"
        context["capabilities"] = ["python", "git", "cli"]
        
        return context
        
    except Exception as e:
        logger.error(f"Failed to get system context: {e}")
        return {"error": str(e)}

"""Plugin interface enforcer."""

from typing import Any, List, Type
import logging

logger = logging.getLogger(__name__)

class InterfaceEnforcer:
    """Validates that a plugin class implements a specific interface."""
    
    @staticmethod
    def enforce(plugin_obj: Any, interface_class: Type) -> bool:
        """Check if plugin_obj satisfies the interface_class requirements."""
        required_methods = [
            m for m in dir(interface_class) 
            if not m.startswith("_") and callable(getattr(interface_class, m))
        ]
        
        missing = []
        for method in required_methods:
            if not hasattr(plugin_obj, method) or not callable(getattr(plugin_obj, method)):
                missing.append(method)
                
        if missing:
            logger.error(f"Plugin {type(plugin_obj).__name__} is missing required methods: {missing}")
            return False
            
        return True

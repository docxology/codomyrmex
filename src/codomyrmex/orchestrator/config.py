from pathlib import Path
from typing import Dict, Any
import json

from codomyrmex.logging_monitoring import get_logger























"""Orchestrator Configuration.

Handles loading and parsing of script configurations.

This module provides config functionality including:
- 2 functions: load_config, get_script_config
- 0 classes: 

Usage:
    from config import FunctionName, ClassName
    # Example usage here
"""
logger = get_logger(__name__)


def load_config(scripts_dir: Path) -> Dict[str, Any]:
    """Load script configuration."""
    config_path = scripts_dir / "scripts_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            pass
    return {"default": {}, "scripts": {}}

def get_script_config(script_path: Path, scripts_dir: Path, global_config: Dict[str, Any]) -> Dict[str, Any]:
    """Get configuration for a specific script."""
    rel_path = str(script_path.relative_to(scripts_dir))
    
    config = global_config.get("default", {}).copy()
    
    # Direct match
    if rel_path in global_config.get("scripts", {}):
        config.update(global_config["scripts"][rel_path])
        return config
        
    # Check if any key in config ends with the script name or relative path
    for key, val in global_config.get("scripts", {}).items():
        if rel_path.endswith(key):
            config.update(val)
            return config
            
    return config

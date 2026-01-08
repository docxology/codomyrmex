"""
Orchestrator Configuration

Handles loading and parsing of script configurations.
"""

import json
from pathlib import Path
from typing import Dict, Any

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

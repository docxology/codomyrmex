"""
Configuration loader for examples.

Supports loading from YAML and JSON files with environment variable substitution
and validation.
"""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file (YAML or JSON)
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config format is invalid
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load based on file extension
    if config_path.suffix in ['.yaml', '.yml']:
        return _load_yaml(config_path)
    elif config_path.suffix == '.json':
        return _load_json(config_path)
    else:
        raise ValueError(f"Unsupported config format: {config_path.suffix}")


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    try:
        import yaml
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
    except ImportError:
        # Fallback to JSON if PyYAML not available
        raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
    
    return _substitute_env_vars(config)


def _load_json(path: Path) -> Dict[str, Any]:
    """Load JSON configuration file."""
    with open(path, 'r') as f:
        config = json.load(f)
    
    return _substitute_env_vars(config)


def _substitute_env_vars(config: Any) -> Any:
    """
    Recursively substitute environment variables in config.
    
    Supports ${VAR_NAME} and ${VAR_NAME:default_value} syntax.
    """
    if isinstance(config, dict):
        return {k: _substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_substitute_env_vars(item) for item in config]
    elif isinstance(config, str):
        # Pattern matches ${VAR} or ${VAR:default}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ''
            return os.environ.get(var_name, default_value)
        
        return re.sub(pattern, replace_var, config)
    else:
        return config


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.
    
    Later configs override earlier ones. Nested dicts are merged recursively.
    
    Args:
        *configs: Configuration dictionaries to merge
        
    Returns:
        Merged configuration
    """
    result = {}
    
    for config in configs:
        result = _deep_merge(result, config)
    
    return result


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """Recursively merge two dictionaries."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_config(config: Dict[str, Any], required_keys: list) -> None:
    """
    Validate that required keys exist in config.
    
    Args:
        config: Configuration dictionary
        required_keys: List of required key paths (use dot notation for nested keys)
        
    Raises:
        ValueError: If required keys are missing
    """
    missing_keys = []
    
    for key_path in required_keys:
        keys = key_path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                missing_keys.append(key_path)
                break
    
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

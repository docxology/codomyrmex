import json
from pathlib import Path
from typing import Any

import yaml

from codomyrmex.logging_monitoring import get_logger

"""Orchestrator Configuration.

Handles loading and parsing of script configurations.

This module provides config functionality including:
    pass
- 2 functions: load_config, get_script_config
- 0 classes:
    pass

Usage:
    from config import FunctionName, ClassName
    # Example usage here
"""
logger = get_logger(__name__)


def load_config(scripts_dir: Path) -> dict[str, Any]:
    """Load script configuration, searching upwards for config.yaml."""
    current = scripts_dir
    # Search up to 3 levels for config.yaml or config.yml
    for _ in range(4):
        for name in ["config.yaml", "config.yml"]:
            config_path = current / name
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        return yaml.safe_load(f) or {}
                except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                    logger.warning(f"Failed to load YAML config {config_path}: {e}")

        # Also check for scripts_config.json
        json_path = current / "scripts_config.json"
        if json_path.exists():
            try:
                with open(json_path) as f:
                    return json.load(f)
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                logger.warning(f"Failed to load JSON config {json_path}: {e}")

        # Stop if we hit project root or system root
        if (current / "src").exists() or current.parent == current:
            break
        current = current.parent

    return {"skip": [], "timeout_override": {}, "scripts": {}}

def get_script_config(script_path: Path, scripts_dir: Path, global_config: dict[str, Any]) -> dict[str, Any]:
    """Get configuration for a specific script."""
    rel_path = str(script_path.relative_to(scripts_dir))

    config = global_config.get("default", {}).copy()

    # Check skips
    skip_list = global_config.get("skip", [])
    if rel_path in skip_list:
        config["skip"] = True
        config["skip_reason"] = "Listed in skip configuration"

    # Check timeout overrides
    timeout_overrides = global_config.get("timeout_override", {})
    if rel_path in timeout_overrides:
        config["timeout"] = timeout_overrides[rel_path]

    # Scripts section.
    scripts_config = global_config.get("scripts", {})
    if rel_path in scripts_config:
        config.update(scripts_config[rel_path])
    else:
        # Check partial matches
        for key, val in scripts_config.items():
            if rel_path.endswith(key):
                config.update(val)
                break

    return config

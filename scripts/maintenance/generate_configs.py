#!/usr/bin/env python3
"""
Configuration Generator.

Ensures that every valid source module in `src/codomyrmex/` has a
corresponding dedicated configuration directory in the `/config/` root,
complete with a comprehensive default `config.yaml`.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src" / "codomyrmex"
CONFIG_DIR = REPO_ROOT / "config"

# Subdirectories in src/ that are not product modules
EXCLUDES = {
    "__pycache__", "tests", "examples", "docs", "scripts",
    "image", "vision", "demos"
}

def get_valid_modules() -> list[str]:
    """Find all valid top-level directories common to src/codomyrmex/."""
    modules = []
    if SRC_DIR.exists():
        for item in sorted(SRC_DIR.iterdir()):
            if item.is_dir() and item.name not in EXCLUDES and not item.name.startswith("."):
                modules.append(item.name)
    return modules

def generate_default_config(module_name: str) -> dict:
    """Generate a comprehensive default config dictionary for a module."""
    return {
        "module": module_name,
        "enabled": True,
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": f"logs/{module_name}.log"
        },
        "performance": {
            "max_workers": 4,
            "timeout_seconds": 30.0,
            "caching": True
        },
        "features": {
            "experimental": False,
            "strict_mode": True
        }
    }

def sync_configs():
    """Create config directories and files for all modules."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    modules = get_valid_modules()

    print(f"Found {len(modules)} valid modules. Synchronizing config/... ")

    created_count = 0
    updated_count = 0

    for mod in modules:
        mod_config_dir = CONFIG_DIR / mod
        mod_config_dir.mkdir(parents=True, exist_ok=True)

        config_file = mod_config_dir / "config.yaml"

        if not config_file.exists():
            default_config = generate_default_config(mod)
            with open(config_file, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
            created_count += 1
            print(f"  [+] Created {mod}/config.yaml")
        else:
            updated_count += 1

    print("\n✅ Synchronization complete.")
    print(f"Created {created_count} new config files. Skipped {updated_count} existing.")

if __name__ == "__main__":
    sync_configs()

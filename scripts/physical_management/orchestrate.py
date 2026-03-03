#!/usr/bin/env python3
"""
Orchestrator for physical_management
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator.core import main


    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "physical_management" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/physical_management/config.yaml")

if __name__ == "__main__":
    # Run the orchestrator for this specific module directory
    # We must explicitly set the scripts directory to avoid recursive discovery of the parent 'scripts' folder
    current_dir = Path(__file__).resolve().parent
    # Check if --scripts-dir is already passed
    if not any(arg.startswith("--scripts-dir") for arg in sys.argv):
        sys.argv.append(f"--scripts-dir={current_dir}")

    sys.exit(main())

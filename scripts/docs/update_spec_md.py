#!/usr/bin/env python3
"""
scripts/update_spec_md.py

Thin wrapper around codomyrmex.documentation.maintenance.update_spec.
"""

import argparse
from pathlib import Path
import sys

# Ensure src is in path
PROJ_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJ_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from codomyrmex.documentation.maintenance import update_spec
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    sys.exit(1)


def main():
    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "docs" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/docs/config.yaml")

    parser = argparse.ArgumentParser(description="Update SPEC.md with missing modules.")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    args = parser.parse_args()

    src_dir = args.root / "src" / "codomyrmex"

    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        return

    update_spec(src_dir)


if __name__ == "__main__":
    main()

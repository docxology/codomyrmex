#!/usr/bin/env python3
"""
scripts/update_root_docs.py

Thin wrapper around codomyrmex.documentation.maintenance.update_root_docs.
"""

import argparse
import sys
from pathlib import Path

# Ensure src is in path
PROJ_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJ_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from codomyrmex.documentation.maintenance import update_root_docs
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    sys.exit(1)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "docs" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/docs/config.yaml")

    parser = argparse.ArgumentParser(description="Update root documentation files.")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    args = parser.parse_args()

    src_dir = args.root / "src" / "codomyrmex"

    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        return

    update_root_docs(src_dir)


if __name__ == "__main__":
    main()

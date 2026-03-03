#!/usr/bin/env python3
"""
scripts/audit_rasp.py

Thin wrapper around codomyrmex.documentation.audit.audit_rasp.
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
    from codomyrmex.documentation.audit import audit_rasp
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    print("Ensure you are running from the project root or have set PYTHONPATH.")
    sys.exit(1)


def main():
    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "audits" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/audits/config.yaml")

    parser = argparse.ArgumentParser(description="Audit RASP documentation breadth.")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    args = parser.parse_args()

    src_dir = args.root / "src" / "codomyrmex"

    if not src_dir.exists():
        print(f"Critical Error: Could not find src/codomyrmex at {src_dir}")
        sys.exit(1)

    sys.exit(audit_rasp(src_dir))


if __name__ == "__main__":
    main()

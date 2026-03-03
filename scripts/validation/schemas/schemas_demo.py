#!/usr/bin/env python3
"""
Schemas Demo Script

Demonstrates functionality of the schemas submodule.
"""

import sys
from pathlib import Path

import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # 4 levels up
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from codomyrmex.utils.cli_helpers import (
        print_error,
        print_info,
        print_success,
        setup_logging,
    )
except ImportError:
    pass

# Auto-injected: Load configuration
config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "validation" / "config.yaml"
if config_path.exists():
    with open(config_path) as f:
        yaml.safe_load(f) or {}
        print("Loaded config from config/validation/config.yaml")

def main() -> int:
    setup_logging()
    print_info("=== Validation Schemas Demo ===")
    try:
        import codomyrmex.validation.schemas as mod
        print_success(f"schemas module loaded: version={getattr(mod, '__version__', 'unknown')}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("Validation Schemas demo complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())

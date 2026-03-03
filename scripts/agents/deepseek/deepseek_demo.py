#!/usr/bin/env python3
"""
Deepseek Demo Script

Demonstrates functionality of the deepseek submodule.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("=== DeepSeek Agent Demo ===")
    try:
        from codomyrmex.agents.deepseek import DeepSeekClient
        obj = DeepSeekClient()
        print_success(f"DeepSeekClient loaded: {obj!r}")
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1
    except Exception as e:
        print_error(f"Demo error: {e}")
        return 1
    print_success("DeepSeek Agent demo complete")
    return 0



    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "agents" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/agents/config.yaml")

if __name__ == "__main__":
    sys.exit(main())

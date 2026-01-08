#!/usr/bin/env python3
"""Utils module orchestrator script.

This is a thin orchestrator that delegates to the utils module
in src/codomyrmex/utils/.
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Main entry point for utils orchestration."""
    print("Utils module orchestrator")
    print("=" * 40)
    
    try:
        from codomyrmex import utils
        print(f"Utils module loaded: {utils.__name__}")
        
        # List available utilities
        if hasattr(utils, '__all__'):
            print(f"Available utilities: {utils.__all__}")
    except ImportError as e:
        print(f"Error importing utils module: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

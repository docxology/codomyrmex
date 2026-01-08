#!/usr/bin/env python3
"""Cloud module orchestrator script.

This is a thin orchestrator that delegates to the cloud module
in src/codomyrmex/cloud/.
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Main entry point for cloud orchestration."""
    print("Cloud module orchestrator")
    print("=" * 40)
    
    try:
        from codomyrmex import cloud
        print(f"Cloud module loaded: {cloud.__name__}")
        
        # List available functionality
        if hasattr(cloud, '__all__'):
            print(f"Available exports: {cloud.__all__}")
    except ImportError as e:
        print(f"Error importing cloud module: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

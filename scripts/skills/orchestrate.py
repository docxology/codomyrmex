#!/usr/bin/env python3
"""Skills module orchestrator script.

This is a thin orchestrator that delegates to the skills module
in src/codomyrmex/skills/.
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Main entry point for skills orchestration."""
    print("Skills module orchestrator")
    print("=" * 40)
    
    try:
        from codomyrmex import skills
        print(f"Skills module loaded: {skills.__name__}")
    except ImportError as e:
        print(f"Error importing skills module: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

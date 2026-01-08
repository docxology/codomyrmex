#!/usr/bin/env python3
"""Logistics module orchestrator script.

This is a thin orchestrator that delegates to the logistics module
in src/codomyrmex/logistics/ which includes orchestration and task management.
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Main entry point for logistics orchestration."""
    print("Logistics module orchestrator")
    print("=" * 40)
    
    try:
        from codomyrmex import logistics
        print(f"Logistics module loaded: {logistics.__name__}")
        
        # List available submodules
        print("\nAvailable submodules:")
        print("  - orchestration/project: Project orchestration and workflow management")
        print("  - task: Task queue and job scheduling")
    except ImportError as e:
        print(f"Error importing logistics module: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

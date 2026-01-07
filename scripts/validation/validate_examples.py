#!/usr/bin/env python3
"""
Thin wrapper for the Codomyrmex Examples Validator.
Delegates all logic to src/codomyrmex/validation/validator.py.
"""

import sys
from pathlib import Path

# Add src to path if not already there
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

try:
    from codomyrmex.validation.examples_validator import main
except ImportError as e:
    import traceback
    print("❌ Critical Error: Could not import codomyrmex.validation.validator")
    print(f"   Ensure {project_root}/src is in your Python path.")
    print(f"   Detailed error: {e}")
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())

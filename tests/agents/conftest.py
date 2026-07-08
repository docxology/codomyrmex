"""conftest.py for agents test directory.

Adds the open_gauss submodule to sys.path at collection time so all test
modules in this directory can import from it without reimporting sys.path
inside each test file.
"""

import sys
from pathlib import Path

# Add OpenGauss submodule to sys.path for direct imports (gauss_state, gauss_time, etc.)
OPEN_GAUSS_DIR = Path(__file__).parent.parent.parent / "agents" / "open_gauss"
if str(OPEN_GAUSS_DIR) not in sys.path:
    sys.path.insert(0, str(OPEN_GAUSS_DIR))

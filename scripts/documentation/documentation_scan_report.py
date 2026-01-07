#!/usr/bin/env python3
"""
Thin wrapper for documentation_scan_report.py.
Logic migrated to codomyrmex.documentation.scripts.documentation_scan_report.
"""

import sys
from pathlib import Path

# Ensure src is in python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

try:
    from codomyrmex.documentation.scripts import documentation_scan_report
    if hasattr(documentation_scan_report, 'main'):
        sys.exit(documentation_scan_report.main())
    else:
        # If no main, just running the module might have been the original behavior
        # But importing it effectively runs top-level code if not guarded.
        # Most scripts here likely have "if __name__ == '__main__': main()"
        # But if we import it, the name is not main.
        # So we might need to explicitly run main().
        pass
except ImportError as e:
    print(f"Error importing module: {e}")
    sys.exit(1)
except AttributeError:
    print(f"Module documentation_scan_report does not have a main function or failed to execute.")
    sys.exit(1)

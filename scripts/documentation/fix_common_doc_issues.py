#!/usr/bin/env python3
"""
Thin wrapper for fix_common_doc_issues.py.
Logic migrated to codomyrmex.documentation.scripts.fix_common_doc_issues.
"""

import sys
from pathlib import Path

# Ensure src is in python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

try:
    from codomyrmex.documentation.scripts import fix_common_doc_issues
    if hasattr(fix_common_doc_issues, 'main'):
        sys.exit(fix_common_doc_issues.main())
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
    print(f"Module fix_common_doc_issues does not have a main function or failed to execute.")
    sys.exit(1)

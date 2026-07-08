from __future__ import annotations

import sys
from pathlib import Path


def prepare_hermes_imports(root: Path) -> None:
    root = root.resolve()
    root_str = str(root)
    sys.path[:] = [path for path in sys.path if path != root_str]
    sys.path.insert(0, root_str)

    for module_name in ("utils",):
        module = sys.modules.get(module_name)
        if module is None:
            continue
        module_file = getattr(module, "__file__", None)
        if module_file is None:
            sys.modules.pop(module_name, None)
            continue
        try:
            module_path = Path(module_file).resolve()
        except OSError:
            sys.modules.pop(module_name, None)
            continue
        if not module_path.is_relative_to(root):
            sys.modules.pop(module_name, None)

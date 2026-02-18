"""
Static analysis for module exports.
"""

import ast
from pathlib import Path
from typing import List, Tuple, Union, Dict

SKIP_DIRS = {"__pycache__", "py.typed"}


def get_modules(src_dir: Path) -> List[Path]:
    """Return paths to all module directories that have __init__.py."""
    modules = []
    if not src_dir.exists():
        return modules
        
    for entry in sorted(src_dir.iterdir()):
        if entry.is_dir() and entry.name not in SKIP_DIRS and (entry / "__init__.py").exists():
            modules.append(entry)
    return modules


def check_all_defined(init_path: Path) -> Tuple[bool, Union[List[str], None]]:
    """Parse __init__.py and check for __all__."""
    source = init_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, str(init_path))
    except SyntaxError:
        return False, None

    for node in ast.walk(tree):
        # Standard: __all__ = [...]
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        names = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                names.append(elt.value)
                        return True, names
                    return True, None
        # Annotated: __all__: list[str] = [...]
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "__all__":
                if node.value and isinstance(node.value, (ast.List, ast.Tuple)):
                    names = []
                    for elt in node.value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            names.append(elt.value)
                    return True, names
                return True, None
    return False, None


def audit_exports(src_dir: Path) -> List[Dict[str, str]]:
    """Run the audit. Returns list of findings."""
    findings = []
    modules = get_modules(src_dir)

    for mod_path in modules:
        init = mod_path / "__init__.py"
        mod_name = mod_path.name
        has_all, names = check_all_defined(init)

        if not has_all:
            findings.append({
                "module": mod_name,
                "issue": "MISSING_ALL",
                "detail": f"{mod_name}/__init__.py has no __all__ definition",
            })

    return findings

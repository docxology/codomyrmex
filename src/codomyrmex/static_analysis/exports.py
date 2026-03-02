"""Static analysis for module exports and dead code detection.

Provides:
- __all__ audit: detect modules missing __all__ definitions.
- Dead export detection: find exports that are never imported.
- Unused function detection: find module-level functions never referenced
  within the same codebase.
"""

from __future__ import annotations

import ast
logger = get_logger(__name__)
from pathlib import Path
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

SKIP_DIRS = {"__pycache__", "py.typed", ".git", "node_modules", "htmlcov"}


# ─── Module discovery ───────────────────────────────────────────────────


def get_modules(src_dir: Path) -> list[Path]:
    """Return paths to all module directories that have __init__.py."""
    modules = []
    if not src_dir.exists():
        return modules
    for entry in sorted(src_dir.iterdir()):
        if (
            entry.is_dir()
            and entry.name not in SKIP_DIRS
            and not entry.name.startswith(".")
            and (entry / "__init__.py").exists()
        ):
            modules.append(entry)
    return modules


# ─── __all__ auditing ───────────────────────────────────────────────────


def check_all_defined(init_path: Path) -> tuple[bool, list[str] | None]:
    """Parse __init__.py and check for __all__.

    Returns:
        (has_all, names): Whether __all__ exists, and its contents if parseable.
    """
    source = init_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, str(init_path))
    except SyntaxError:
        return False, None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        names = [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
                        return True, names
                    return True, None
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "__all__":
                if node.value and isinstance(node.value, (ast.List, ast.Tuple)):
                    names = [
                        elt.value
                        for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    ]
                    return True, names
                return True, None
    return False, None


def audit_exports(src_dir: Path) -> list[dict[str, str]]:
    """Run the __all__ audit. Returns list of findings."""
    findings = []
    modules = get_modules(src_dir)

    for mod_path in modules:
        init = mod_path / "__init__.py"
        mod_name = mod_path.name
        has_all, names = check_all_defined(init)

        if not has_all:
            findings.append(
                {
                    "module": mod_name,
                    "issue": "MISSING_ALL",
                    "detail": f"{mod_name}/__init__.py has no __all__ definition",
                }
            )

    return findings


# ─── Dead export detection ──────────────────────────────────────────────


def _collect_all_imports(src_dir: Path) -> set[str]:
    """Collect every name imported from codomyrmex across all .py files."""
    imported_names: set[str] = set()
    for py_file in src_dir.rglob("*.py"):
        if any(skip in py_file.parts for skip in SKIP_DIRS):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"), str(py_file))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("codomyrmex.") and node.names:
                    for alias in node.names:
                        imported_names.add(alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("codomyrmex."):
                        imported_names.add(alias.name.split(".")[-1])
    return imported_names


def find_dead_exports(src_dir: Path) -> list[dict[str, Any]]:
    """Find exports in __all__ that are never imported anywhere else.

    Returns:
        List of dicts with module, export_name, and detail.
    """
    all_imports = _collect_all_imports(src_dir)
    dead: list[dict[str, Any]] = []

    for mod_path in get_modules(src_dir):
        init = mod_path / "__init__.py"
        has_all, names = check_all_defined(init)
        if not has_all or names is None:
            continue
        for name in names:
            if name not in all_imports:
                dead.append(
                    {
                        "module": mod_path.name,
                        "export_name": name,
                        "detail": f"'{name}' is in {mod_path.name}.__all__ but never imported elsewhere",
                    }
                )
    return dead


# ─── Unused function detection ──────────────────────────────────────────


def _collect_defined_functions(py_file: Path) -> list[str]:
    """Extract top-level function names from a Python file."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"), str(py_file))
    except SyntaxError as e:
        logger.warning("Skipping file with syntax error %s: %s", py_file, e)
        return []
    return [
        node.name
        for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    ]


def _collect_name_references(py_file: Path) -> set[str]:
    """Collect all Name references in a Python file."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"), str(py_file))
    except SyntaxError:
        return set()
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}


def find_unused_functions(src_dir: Path) -> list[dict[str, Any]]:
    """Find top-level public functions that are never referenced elsewhere.

    Returns:
        List of dicts with file, function_name, and detail.
    """
    # Phase 1: collect all function definitions
    definitions: list[tuple[Path, str]] = []
    for py_file in src_dir.rglob("*.py"):
        if any(skip in py_file.parts for skip in SKIP_DIRS):
            continue
        for func_name in _collect_defined_functions(py_file):
            definitions.append((py_file, func_name))

    # Phase 2: collect all name references across the codebase
    all_references: set[str] = set()
    for py_file in src_dir.rglob("*.py"):
        if any(skip in py_file.parts for skip in SKIP_DIRS):
            continue
        all_references.update(_collect_name_references(py_file))

    # Phase 3: find functions only referenced in their own definition
    unused: list[dict[str, Any]] = []
    for fpath, fname in definitions:
        if fname not in all_references:
            try:
                rel = fpath.relative_to(src_dir)
            except ValueError:
                rel = fpath
            unused.append(
                {
                    "file": str(rel),
                    "function_name": fname,
                    "detail": f"Function '{fname}' is defined but never referenced in the codebase",
                }
            )
    return unused


# ─── Summary report ────────────────────────────────────────────────────


def full_audit(src_dir: Path) -> dict[str, Any]:
    """Run all export/dead-code audits and return a unified report.

    Returns:
        Dict with keys: missing_all, dead_exports, unused_functions, summary.
    """
    missing = audit_exports(src_dir)
    dead = find_dead_exports(src_dir)
    unused = find_unused_functions(src_dir)
    return {
        "missing_all": missing,
        "dead_exports": dead,
        "unused_functions": unused,
        "summary": {
            "modules_missing_all": len(missing),
            "dead_export_count": len(dead),
            "unused_function_count": len(unused),
        },
    }

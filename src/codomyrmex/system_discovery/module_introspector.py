"""Module introspector — deep structural analysis of all Codomyrmex modules.

Scans every module under ``src/codomyrmex/`` and reports structure,
exports, documentation health, test presence, and MCP tool counts.

Example::

    introspector = ModuleIntrospector()
    report = introspector.scan_all()
    print(f"Modules: {report['total_modules']}")
    for m in report["modules"][:3]:
        print(f"  {m['name']}: {m['file_count']} files, {m['loc']} LOC")
"""

from __future__ import annotations

import ast
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SRC_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ModuleInfo:
    """Structural profile of a single module.

    Attributes:
        name: Module directory name.
        path: Absolute path.
        file_count: Number of Python files.
        loc: Total lines of code.
        has_init: Whether ``__init__.py`` exists.
        has_readme: Whether ``README.md`` exists.
        has_agents: Whether ``AGENTS.md`` exists.
        has_spec: Whether ``SPEC.md`` exists.
        has_tests: Whether any test files exist.
        exports: Public names from ``__all__``.
        mcp_tool_count: Number of ``@mcp_tool`` decorators.
        submodule_count: Number of subdirectories with ``__init__.py``.
        classes: Number of class definitions.
        functions: Number of top-level function definitions.
    """

    name: str
    path: str
    file_count: int = 0
    loc: int = 0
    has_init: bool = False
    has_readme: bool = False
    has_agents: bool = False
    has_spec: bool = False
    has_tests: bool = False
    exports: list[str] = field(default_factory=list)
    mcp_tool_count: int = 0
    submodule_count: int = 0
    classes: int = 0
    functions: int = 0

    @property
    def doc_score(self) -> float:
        """Documentation completeness (0.0–1.0)."""
        checks = [self.has_readme, self.has_agents, self.has_spec, self.has_init]
        return sum(checks) / len(checks)

    @property
    def health(self) -> str:
        """Module health: ``healthy``, ``partial``, or ``minimal``."""
        score = self.doc_score
        if score >= 0.75 and self.has_tests:
            return "healthy"
        if score >= 0.5:
            return "partial"
        return "minimal"


class ModuleIntrospector:
    """Deep structural analysis of all Codomyrmex modules.

    Args:
        src_root: Path to ``src/codomyrmex/``.

    Example::

        intro = ModuleIntrospector()
        report = intro.scan_all()
        healthy = [m for m in report["modules"] if m["health"] == "healthy"]
    """

    def __init__(self, src_root: Path | None = None) -> None:
        self._root = src_root or _SRC_ROOT

    def scan_module(self, mod_dir: Path) -> ModuleInfo:
        """Scan a single module directory.

        Args:
            mod_dir: Path to the module directory.

        Returns:
            :class:`ModuleInfo` with structural data.
        """
        info = ModuleInfo(name=mod_dir.name, path=str(mod_dir))

        py_files = list(mod_dir.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]
        info.file_count = len(py_files)

        total_loc = 0
        total_classes = 0
        total_functions = 0
        mcp_count = 0

        for f in py_files:
            try:
                content = f.read_text(errors="replace")
                total_loc += len(content.splitlines())
                mcp_count += content.count("@mcp_tool")

                tree = ast.parse(content, filename=str(f))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        total_classes += 1
                    elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                        total_functions += 1
            except Exception:
                continue

        info.loc = total_loc
        info.classes = total_classes
        info.functions = total_functions
        info.mcp_tool_count = mcp_count

        info.has_init = (mod_dir / "__init__.py").exists()
        info.has_readme = (mod_dir / "README.md").exists()
        info.has_agents = (mod_dir / "AGENTS.md").exists()
        info.has_spec = (mod_dir / "SPEC.md").exists()

        # Test detection
        info.has_tests = bool(list(mod_dir.rglob("test_*.py")))

        # Exports from __init__.py
        init_path = mod_dir / "__init__.py"
        if init_path.exists():
            try:
                tree = ast.parse(init_path.read_text(errors="replace"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "__all__":
                                if isinstance(node.value, ast.List):
                                    info.exports = [
                                        elt.value
                                        for elt in node.value.elts
                                        if isinstance(elt, ast.Constant)
                                        and isinstance(elt.value, str)
                                    ]
            except Exception:
                pass

        # Submodule counting
        info.submodule_count = sum(
            1
            for d in mod_dir.iterdir()
            if d.is_dir()
            and (d / "__init__.py").exists()
            and not d.name.startswith("_")
        )

        return info

    def scan_all(self) -> dict[str, Any]:
        """Scan all modules under src/codomyrmex/.

        Returns:
            Dict with ``total_modules``, ``total_loc``, ``total_files``,
            ``health_distribution``, and ``modules`` list.
        """
        start = time.monotonic()
        modules: list[dict] = []

        for mod_dir in sorted(self._root.iterdir()):
            if (
                not mod_dir.is_dir()
                or mod_dir.name.startswith(("_", "."))
                or mod_dir.name == "tests"
            ):
                continue

            info = self.scan_module(mod_dir)
            modules.append(
                {
                    "name": info.name,
                    "file_count": info.file_count,
                    "loc": info.loc,
                    "classes": info.classes,
                    "functions": info.functions,
                    "mcp_tools": info.mcp_tool_count,
                    "submodules": info.submodule_count,
                    "exports": len(info.exports),
                    "doc_score": round(info.doc_score, 2),
                    "health": info.health,
                    "has_tests": info.has_tests,
                }
            )

        elapsed = (time.monotonic() - start) * 1000
        health_dist = {"healthy": 0, "partial": 0, "minimal": 0}
        for m in modules:
            health_dist[m["health"]] = health_dist.get(m["health"], 0) + 1

        return {
            "total_modules": len(modules),
            "total_loc": sum(m["loc"] for m in modules),
            "total_files": sum(m["file_count"] for m in modules),
            "total_classes": sum(m["classes"] for m in modules),
            "total_functions": sum(m["functions"] for m in modules),
            "total_mcp_tools": sum(m["mcp_tools"] for m in modules),
            "health_distribution": health_dist,
            "scan_duration_ms": round(elapsed, 1),
            "modules": modules,
        }

    def get_top_modules(self, n: int = 10, by: str = "loc") -> list[dict]:
        """Get the top N modules by a metric.

        Args:
            n: Number to return.
            by: Metric to sort by (``loc``, ``file_count``, ``classes``).

        Returns:
            List of module dicts sorted descending.
        """
        report = self.scan_all()
        return sorted(report["modules"], key=lambda m: m.get(by, 0), reverse=True)[:n]


__all__ = [
    "ModuleInfo",
    "ModuleIntrospector",
]

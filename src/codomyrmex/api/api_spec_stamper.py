"""API specification stamper — freezes module public APIs at release.

Scans module ``__init__.py`` files for ``__all__`` exports and builds
a versioned API specification snapshot, enabling breaking-change detection.

Example::

    stamper = APISpecStamper()
    spec = stamper.snapshot()
    stamper.write_spec(spec, "API_SPECIFICATION.md")
    diff = stamper.diff(old_spec, new_spec)
"""

from __future__ import annotations

import ast
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SRC_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ModuleAPI:
    """Public API surface of a single module.

    Attributes:
        name: Module name.
        exports: Names in ``__all__``.
        classes: Public class names.
        functions: Public function names.
    """

    name: str
    exports: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)

    @property
    def surface_size(self) -> int:
        """Total public API surface size."""
        return len(self.exports) or (len(self.classes) + len(self.functions))


class APISpecStamper:
    """Snapshot and diff module public APIs.

    Args:
        src_root: Path to ``src/codomyrmex/``.

    Example::

        stamper = APISpecStamper()
        spec = stamper.snapshot()
        print(f"Total API surface: {spec['total_surface']} symbols")
    """

    def __init__(self, src_root: Path | None = None) -> None:
        self._root = src_root or _SRC_ROOT

    def _scan_module_api(self, mod_dir: Path) -> ModuleAPI:
        """Extract public API from a module's __init__.py."""
        api = ModuleAPI(name=mod_dir.name)
        init = mod_dir / "__init__.py"
        if not init.exists():
            return api

        try:
            tree = ast.parse(init.read_text(errors="replace"))
        except Exception:
            return api

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            api.exports = [
                                elt.value for elt in node.value.elts
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                            ]
            elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                api.classes.append(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                api.functions.append(node.name)

        return api

    def snapshot(self, version: str = "") -> dict[str, Any]:
        """Take a snapshot of all module public APIs.

        Args:
            version: Version tag for the snapshot.

        Returns:
            Dict with ``version``, ``timestamp``, ``modules``, ``total_surface``.
        """
        start = time.monotonic()
        modules: list[dict] = []

        for mod_dir in sorted(self._root.iterdir()):
            if not mod_dir.is_dir() or mod_dir.name.startswith(("_", ".")) or mod_dir.name == "tests":
                continue

            api = self._scan_module_api(mod_dir)
            modules.append({
                "name": api.name,
                "exports": api.exports,
                "classes": api.classes,
                "functions": api.functions,
                "surface_size": api.surface_size,
            })

        elapsed = (time.monotonic() - start) * 1000
        return {
            "version": version or "unknown",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_modules": len(modules),
            "total_surface": sum(m["surface_size"] for m in modules),
            "modules": modules,
            "scan_duration_ms": round(elapsed, 1),
        }

    def diff(self, old: dict, new: dict) -> dict[str, Any]:
        """Diff two API snapshots.

        Args:
            old: Previous snapshot.
            new: Current snapshot.

        Returns:
            Dict with ``added``, ``removed``, ``changed`` module lists.
        """
        old_map = {m["name"]: set(m["exports"]) for m in old.get("modules", [])}
        new_map = {m["name"]: set(m["exports"]) for m in new.get("modules", [])}

        added = [n for n in new_map if n not in old_map]
        removed = [n for n in old_map if n not in new_map]
        changed: list[dict] = []

        for name in sorted(set(old_map) & set(new_map)):
            added_exports = new_map[name] - old_map[name]
            removed_exports = old_map[name] - new_map[name]
            if added_exports or removed_exports:
                changed.append({
                    "module": name,
                    "added_exports": sorted(added_exports),
                    "removed_exports": sorted(removed_exports),
                })

        return {
            "old_version": old.get("version", "?"),
            "new_version": new.get("version", "?"),
            "added_modules": added,
            "removed_modules": removed,
            "changed_modules": changed,
            "is_breaking": bool(removed or any(c["removed_exports"] for c in changed)),
        }

    def write_spec(self, spec: dict, output: str = "API_SPECIFICATION.md") -> Path:
        """Write API specification as markdown.

        Args:
            spec: Snapshot dict.
            output: Output file path.

        Returns:
            Path to written file.
        """
        lines = [
            f"# Codomyrmex API Specification — {spec['version']}",
            "",
            f"**Generated**: {spec['timestamp']} · "
            f"**Modules**: {spec['total_modules']} · "
            f"**Surface**: {spec['total_surface']} symbols",
            "",
        ]

        for mod in spec["modules"]:
            if mod["surface_size"] > 0:
                lines.append(f"## `{mod['name']}`")
                if mod["exports"]:
                    lines.append("")
                    lines.append(f"**Exports** ({len(mod['exports'])}): "
                                 f"`{'`, `'.join(mod['exports'][:20])}`")
                if mod["classes"]:
                    lines.append(f"**Classes**: `{'`, `'.join(mod['classes'][:10])}`")
                if mod["functions"]:
                    lines.append(f"**Functions**: `{'`, `'.join(mod['functions'][:10])}`")
                lines.append("")

        out = Path(output)
        out.write_text("\n".join(lines))
        return out

    def write_json(self, spec: dict, output: str = "api_spec.json") -> Path:
        """Write API specification as JSON."""
        out = Path(output)
        out.write_text(json.dumps(spec, indent=2) + "\n")
        return out


__all__ = [
    "APISpecStamper",
    "ModuleAPI",
]

"""Rule registry — indexed access to all .cursorrules files.

The registry discovers and caches rules by module name, file extension,
and cross-module category, so the engine can look them up without rescanning
the filesystem on every call.
"""

from __future__ import annotations

from pathlib import Path

from .loader import RuleLoader
from .models import Rule

# Maps file extension → rule name in file-specific/
_EXT_TO_RULE: dict[str, str] = {
    ".py": "python",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "README.md",
}

# Maps exact filename → rule name in file-specific/ (takes precedence over extension)
_FILENAME_TO_RULE: dict[str, str] = {
    "CHANGELOG.md": "CHANGELOG",
    "SPEC.md": "SPEC",
    "README.md": "README.md",
}


class RuleRegistry:
    """Discovers and caches rules from a rules root directory.

    Caches loaded Rule objects to avoid redundant filesystem reads.
    Thread-safety is not a requirement here — rules are read-only data.
    """

    def __init__(self, rules_root: Path) -> None:
        self._root = rules_root
        self._cache: dict[str, Rule] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self, path: Path) -> Rule:
        key = str(path)
        if key not in self._cache:
            self._cache[key] = RuleLoader.load(path)
        return self._cache[key]

    def _load_if_exists(self, path: Path) -> Rule | None:
        if path.exists():
            return self._load(path)
        return None

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    def get_general(self) -> Rule | None:
        """Return the single general.cursorrules rule, or None if absent."""
        return self._load_if_exists(self._root / "general.cursorrules")

    def get_module_rule(self, module_name: str) -> Rule | None:
        """Return the module-specific rule for *module_name*, or None."""
        path = self._root / "modules" / f"{module_name}.cursorrules"
        return self._load_if_exists(path)

    def get_cross_module_rules(self) -> list[Rule]:
        """Return all cross-module rules, sorted by name for determinism."""
        cross_dir = self._root / "cross-module"
        if not cross_dir.is_dir():
            return []
        return [
            self._load(f)
            for f in sorted(cross_dir.glob("*.cursorrules"))
        ]

    def get_file_rule(self, file_path: str | Path) -> Rule | None:
        """Infer and return the file-specific rule for *file_path*, or None.

        Checks exact filename match first, then falls back to extension.
        """
        p = Path(file_path)
        rule_name = _FILENAME_TO_RULE.get(p.name) or _EXT_TO_RULE.get(p.suffix)
        if not rule_name:
            return None
        path = self._root / "file-specific" / f"{rule_name}.cursorrules"
        return self._load_if_exists(path)

    def list_module_names(self) -> list[str]:
        """Return sorted list of all module names with defined rules."""
        modules_dir = self._root / "modules"
        if not modules_dir.is_dir():
            return []
        return sorted(
            f.name[: -len(".cursorrules")]
            for f in modules_dir.glob("*.cursorrules")
        )

    def list_cross_module_names(self) -> list[str]:
        """Return sorted list of all cross-module rule names."""
        cross_dir = self._root / "cross-module"
        if not cross_dir.is_dir():
            return []
        return sorted(
            f.name[: -len(".cursorrules")]
            for f in cross_dir.glob("*.cursorrules")
        )

    def list_file_rule_names(self) -> list[str]:
        """Return sorted list of all file-specific rule names."""
        fs_dir = self._root / "file-specific"
        if not fs_dir.is_dir():
            return []
        return sorted(
            f.name[: -len(".cursorrules")]
            for f in fs_dir.glob("*.cursorrules")
        )

    def list_all_rules(self) -> list[Rule]:
        """Return all rules from every level, sorted by priority (FILE_SPECIFIC first).

        Collects and returns every general, cross-module, module, and file-specific
        rule.  The list is sorted by :attr:`RulePriority.value` ascending, so
        ``FILE_SPECIFIC`` (value 1) comes first and ``GENERAL`` (value 4) last.
        """
        all_rules: list[Rule] = []
        general = self.get_general()
        if general is not None:
            all_rules.append(general)
        all_rules.extend(self.get_cross_module_rules())
        for name in self.list_module_names():
            rule = self.get_module_rule(name)
            if rule is not None:
                all_rules.append(rule)
        for name in self.list_file_rule_names():
            rule = self._load_if_exists(self._root / "file-specific" / f"{name}.cursorrules")
            if rule is not None:
                all_rules.append(rule)
        return sorted(all_rules, key=lambda r: r.priority.value)

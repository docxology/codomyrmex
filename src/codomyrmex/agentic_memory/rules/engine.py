"""Rule engine — hierarchy-aware resolution of applicable coding rules.

Given a file path and/or module name, the engine collects all applicable
rules (general → cross-module → module → file-specific) and returns them
as a RuleSet that can be iterated in priority order.
"""

from __future__ import annotations

from pathlib import Path

from .models import Rule, RuleSet
from .registry import RuleRegistry

# Default rules root: the directory containing this file
_DEFAULT_RULES_ROOT = Path(__file__).parent


class RuleEngine:
    """Resolves which coding rules apply to a given context.

    Usage::

        from codomyrmex.agentic_memory.rules import RuleEngine

        engine = RuleEngine()

        # All rules that apply when editing src/codomyrmex/agents/memory.py
        rule_set = engine.get_applicable_rules(
            file_path="src/codomyrmex/agents/memory.py",
            module_name="agents",
        )
        for rule in rule_set.resolved():
            print(rule.priority.name, rule.name)
    """

    def __init__(self, rules_root: Path | None = None) -> None:
        """Initialise the engine.

        Args:
            rules_root: Path to the directory containing ``general.cursorrules``
                and the ``modules/``, ``cross-module/``, and ``file-specific/``
                subdirectories.  Defaults to the ``rules/`` package directory.
        """
        if rules_root is None:
            rules_root = _DEFAULT_RULES_ROOT
        self._registry = RuleRegistry(rules_root)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_applicable_rules(
        self,
        file_path: str | Path | None = None,
        module_name: str | None = None,
    ) -> RuleSet:
        """Return all rules that apply to the given context.

        Rules are gathered from all applicable levels:

        1. **General** — always included (lowest priority)
        2. **Cross-module** — all 8 cross-cutting rules
        3. **Module** — the specific module rule if *module_name* is given
        4. **File-specific** — matched by file extension or filename

        The returned :class:`RuleSet` can be iterated via
        :meth:`~RuleSet.resolved` to get rules in priority order
        (FILE_SPECIFIC first, GENERAL last).

        Args:
            file_path: Path of the file being worked on (used for file-specific rule lookup).
            module_name: Codomyrmex module name, e.g. ``"agentic_memory"``.

        Returns:
            A :class:`RuleSet` containing all applicable rules.
        """
        rules: list[Rule] = []

        general = self._registry.get_general()
        if general is not None:
            rules.append(general)

        rules.extend(self._registry.get_cross_module_rules())

        if module_name:
            mod_rule = self._registry.get_module_rule(module_name)
            if mod_rule is not None:
                rules.append(mod_rule)

        if file_path is not None:
            file_rule = self._registry.get_file_rule(file_path)
            if file_rule is not None:
                rules.append(file_rule)

        return RuleSet(rules=rules)

    def get_module_rule(self, module_name: str) -> Rule | None:
        """Return the module-specific rule for *module_name*, or None."""
        return self._registry.get_module_rule(module_name)

    def list_module_names(self) -> list[str]:
        """Return sorted list of all module names that have a defined rule."""
        return self._registry.list_module_names()

    def list_cross_module_names(self) -> list[str]:
        """Return sorted list of all cross-module rule names."""
        return self._registry.list_cross_module_names()

    def list_file_rule_names(self) -> list[str]:
        """Return sorted list of all file-specific rule names."""
        return self._registry.list_file_rule_names()

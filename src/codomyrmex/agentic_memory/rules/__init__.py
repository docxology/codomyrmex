"""Agentic Memory — Rules submodule.

Provides a Python API over the hierarchical .cursorrules coding governance
system, enabling agents to query applicable coding standards programmatically.

Rule hierarchy (most specific wins):

    FILE_SPECIFIC (1) > MODULE (2) > CROSS_MODULE (3) > GENERAL (4)

Quick usage::

    from codomyrmex.agentic_memory.rules import RuleEngine

    engine = RuleEngine()
    rule_set = engine.get_applicable_rules(file_path="memory.py", module_name="agentic_memory")
    for rule in rule_set.resolved():
        print(rule.priority.name, rule.name)

MCP tools (auto-discovered by PAI bridge):
    - ``rules_list_modules``      — list all modules with rules
    - ``rules_get_module_rule``   — get rule for a specific module
    - ``rules_get_applicable``    — get all applicable rules for a context
"""

from .engine import RuleEngine
from .loader import RuleLoader
from .models import Rule, RulePriority, RuleSection, RuleSet
from .registry import RuleRegistry

__all__ = [
    "Rule",
    "RuleEngine",
    "RuleLoader",
    "RulePriority",
    "RuleRegistry",
    "RuleSection",
    "RuleSet",
]

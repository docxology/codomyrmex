"""Tests for the agentic_memory.rules submodule.

Zero-mock policy: all tests use the real .cursorrules files included
in the rules/ package.  No mocking, no stubs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.agentic_memory.rules import (
    RuleEngine,
    RuleLoader,
    RulePriority,
    RuleSet,
)

# Absolute path to the rules/ package directory (where the .cursorrules files live)
RULES_ROOT = Path(__file__).parent.parent.parent / "rules"

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------


def test_rules_root_exists() -> None:
    assert RULES_ROOT.is_dir(), f"rules/ directory not found at {RULES_ROOT}"


def test_general_cursorrules_present() -> None:
    assert (RULES_ROOT / "general.cursorrules").exists()


def test_modules_directory_present() -> None:
    assert (RULES_ROOT / "modules").is_dir()


def test_cross_module_directory_present() -> None:
    assert (RULES_ROOT / "cross-module").is_dir()


def test_file_specific_directory_present() -> None:
    assert (RULES_ROOT / "file-specific").is_dir()


# ---------------------------------------------------------------------------
# RuleLoader
# ---------------------------------------------------------------------------


def test_loader_general_rule() -> None:
    rule = RuleLoader.load(RULES_ROOT / "general.cursorrules")
    assert rule.name == "general"
    assert rule.priority == RulePriority.GENERAL
    assert len(rule.sections) >= 4
    assert rule.raw_content


def test_loader_module_rule() -> None:
    rule = RuleLoader.load(RULES_ROOT / "modules" / "agentic_memory.cursorrules")
    assert rule.name == "agentic_memory"
    assert rule.priority == RulePriority.MODULE
    # Should have at least the Preamble and a coding-standards section
    assert len(rule.sections) >= 2


def test_loader_cross_module_rule() -> None:
    rule = RuleLoader.load(RULES_ROOT / "cross-module" / "logging_monitoring.cursorrules")
    assert rule.priority == RulePriority.CROSS_MODULE


def test_loader_file_specific_python() -> None:
    rule = RuleLoader.load(RULES_ROOT / "file-specific" / "python.cursorrules")
    assert rule.name == "python"
    assert rule.priority == RulePriority.FILE_SPECIFIC


def test_loader_section_numbering() -> None:
    rule = RuleLoader.load(RULES_ROOT / "general.cursorrules")
    numbers = [s.number for s in rule.sections]
    # Sections 0–8 expected; at minimum 0 through 3 should be present
    assert 0 in numbers
    assert 1 in numbers


def test_loader_get_section() -> None:
    rule = RuleLoader.load(RULES_ROOT / "modules" / "agentic_memory.cursorrules")
    s0 = rule.get_section(0)
    assert s0 is not None
    assert s0.title.lower().startswith("preamble")


def test_loader_to_dict_shape() -> None:
    rule = RuleLoader.load(RULES_ROOT / "general.cursorrules")
    d = rule.to_dict()
    assert "name" in d
    assert "priority" in d
    assert "sections" in d
    assert "raw_content" in d
    assert d["priority"] == "GENERAL"


def test_loader_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        RuleLoader.load(RULES_ROOT / "modules" / "nonexistent_module_xyzzy.cursorrules")


def test_loader_wrong_extension_raises() -> None:
    with pytest.raises(ValueError):
        RuleLoader.load(RULES_ROOT / "README.md")


# ---------------------------------------------------------------------------
# RuleEngine — list helpers
# ---------------------------------------------------------------------------


def test_engine_lists_60_modules() -> None:
    engine = RuleEngine(RULES_ROOT)
    modules = engine.list_module_names()
    assert len(modules) == 60
    assert "agentic_memory" in modules
    assert "agents" in modules
    assert "cloud" in modules


def test_engine_module_list_is_sorted() -> None:
    engine = RuleEngine(RULES_ROOT)
    modules = engine.list_module_names()
    assert modules == sorted(modules)


def test_engine_lists_cross_module_names() -> None:
    engine = RuleEngine(RULES_ROOT)
    cross = engine.list_cross_module_names()
    assert len(cross) == 8
    assert "logging_monitoring" in cross


def test_engine_lists_file_rule_names() -> None:
    engine = RuleEngine(RULES_ROOT)
    file_rules = engine.list_file_rule_names()
    assert "python" in file_rules
    assert "yaml" in file_rules
    assert "json" in file_rules


# ---------------------------------------------------------------------------
# RuleEngine — get_applicable_rules
# ---------------------------------------------------------------------------


def test_engine_applicable_general_only() -> None:
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules()
    # No module or file specified → general + cross-module only
    names = [r.name for r in rule_set.rules]
    assert "general" in names


def test_engine_applicable_with_module() -> None:
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(module_name="agentic_memory")
    resolved = rule_set.resolved()
    priorities = [r.priority for r in resolved]
    assert RulePriority.GENERAL in priorities
    assert RulePriority.MODULE in priorities
    # MODULE rule should appear after GENERAL (lower value = higher priority = earlier)
    module_idx = next(i for i, r in enumerate(resolved) if r.priority == RulePriority.MODULE)
    general_idx = next(i for i, r in enumerate(resolved) if r.priority == RulePriority.GENERAL)
    assert module_idx < general_idx


def test_engine_applicable_with_py_file() -> None:
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="memory.py", module_name="agentic_memory")
    resolved = rule_set.resolved()
    priorities = [r.priority for r in resolved]
    assert RulePriority.FILE_SPECIFIC in priorities
    assert RulePriority.MODULE in priorities
    assert RulePriority.GENERAL in priorities
    # FILE_SPECIFIC must come first
    assert resolved[0].priority == RulePriority.FILE_SPECIFIC


def test_engine_applicable_ordering_is_strict() -> None:
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="test.py", module_name="cloud")
    pv = [r.priority.value for r in rule_set.resolved()]
    assert pv == sorted(pv)


def test_engine_applicable_unknown_module_skips_gracefully() -> None:
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(module_name="nonexistent_module_xyzzy")
    names = [r.name for r in rule_set.rules]
    assert "general" in names
    assert "nonexistent_module_xyzzy" not in names


def test_engine_applicable_unknown_file_extension_skips() -> None:
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="script.rb")
    # No .rb file-specific rule — should not raise
    names = [r.name for r in rule_set.rules]
    assert "general" in names


def test_ruleset_to_dict_structure() -> None:
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(module_name="agents")
    dicts = rule_set.to_dict()
    assert isinstance(dicts, list)
    assert len(dicts) >= 2
    first = dicts[0]
    assert "name" in first
    assert "priority" in first
    assert "sections" in first


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------


def test_mcp_rules_list_modules() -> None:
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_modules

    modules = rules_list_modules()
    assert isinstance(modules, list)
    assert len(modules) == 60
    assert "agentic_memory" in modules


def test_mcp_rules_get_module_rule_found() -> None:
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_module_rule

    result = rules_get_module_rule("agents")
    assert result is not None
    assert result["name"] == "agents"
    assert result["priority"] == "MODULE"
    assert isinstance(result["sections"], list)


def test_mcp_rules_get_module_rule_missing() -> None:
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_module_rule

    result = rules_get_module_rule("nonexistent_module_xyzzy")
    assert result is None


def test_mcp_rules_get_applicable_with_py_and_module() -> None:
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_applicable

    results = rules_get_applicable(file_path="example.py", module_name="coding")
    assert isinstance(results, list)
    assert len(results) >= 2
    # First entry must be FILE_SPECIFIC (priority value 1)
    assert results[0]["priority"] == "FILE_SPECIFIC"


def test_mcp_rules_get_applicable_empty_args() -> None:
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_applicable

    results = rules_get_applicable()
    assert isinstance(results, list)
    # At minimum GENERAL + cross-module rules
    assert len(results) >= 1

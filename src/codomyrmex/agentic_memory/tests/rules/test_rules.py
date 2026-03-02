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


# ---------------------------------------------------------------------------
# Edge cases — caching, path normalization, filename rules, exports
# ---------------------------------------------------------------------------


def test_registry_caches_rule_on_second_load() -> None:
    """Registry returns the same Rule object on repeated loads (dict cache)."""
    from codomyrmex.agentic_memory.rules.registry import RuleRegistry

    reg = RuleRegistry(RULES_ROOT)
    r1 = reg.get_general()
    r2 = reg.get_general()
    assert r1 is r2  # Same object — cached, not re-parsed


def test_registry_changelog_file_rule() -> None:
    """CHANGELOG.md filename maps to CHANGELOG rule, not README.md rule."""
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="CHANGELOG.md")
    names = [r.name for r in rule_set.rules]
    assert "CHANGELOG" in names


def test_registry_spec_md_file_rule() -> None:
    """SPEC.md filename maps to SPEC rule, not README.md rule."""
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="SPEC.md")
    names = [r.name for r in rule_set.rules]
    assert "SPEC" in names


def test_registry_yml_extension_matches_yaml_rule() -> None:
    """.yml extension should resolve to the yaml rule."""
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="config.yml")
    names = [r.name for r in rule_set.rules]
    assert "yaml" in names


def test_engine_absolute_path_resolves_file_rule() -> None:
    """An absolute file path should still resolve the correct file-specific rule."""
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="/some/abs/path/script.py")
    names = [r.name for r in rule_set.rules]
    assert "python" in names


def test_engine_plain_filename_resolves_file_rule() -> None:
    """A bare filename (no directory) should still resolve the file-specific rule."""
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="module.py")
    names = [r.name for r in rule_set.rules]
    assert "python" in names


def test_loader_get_section_missing_returns_none() -> None:
    """get_section(99) returns None when section number does not exist."""
    rule = RuleLoader.load(RULES_ROOT / "general.cursorrules")
    assert rule.get_section(99) is None


def test_empty_ruleset_resolved_returns_empty() -> None:
    """An empty RuleSet resolves to an empty list."""
    empty = RuleSet(rules=[])
    assert empty.resolved() == []
    assert empty.to_dict() == []


def test_engine_no_duplicate_rules() -> None:
    """Engine never includes the same rule twice in a RuleSet."""
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="test.py", module_name="agents")
    names = [r.name for r in rule_set.rules]
    assert len(names) == len(set(names))


def test_parent_module_exports_loader_registry_section() -> None:
    """agentic_memory top-level exports RuleLoader, RuleRegistry, RuleSection."""
    from codomyrmex.agentic_memory import RuleLoader as RL
    from codomyrmex.agentic_memory import RuleRegistry as RR
    from codomyrmex.agentic_memory import RuleSection as RS

    assert RL is not None
    assert RR is not None
    assert RS is not None


def test_py_typed_marker_present() -> None:
    """PEP 561 py.typed marker exists in the rules package."""
    marker = RULES_ROOT / "py.typed"
    assert marker.exists(), f"py.typed not found at {marker}"


def test_rule_to_dict_priority_is_string() -> None:
    """Rule.to_dict() serializes RulePriority as its .name string, not int."""
    rule = RuleLoader.load(RULES_ROOT / "modules" / "agentic_memory.cursorrules")
    d = rule.to_dict()
    assert d["priority"] == "MODULE"
    assert isinstance(d["priority"], str)


def test_ruleset_to_dict_first_entry_highest_priority() -> None:
    """RuleSet.to_dict() returns list with highest-priority (FILE_SPECIFIC) first."""
    engine = RuleEngine(RULES_ROOT)
    rule_set = engine.get_applicable_rules(file_path="code.py", module_name="coding")
    dicts = rule_set.to_dict()
    assert len(dicts) >= 2
    assert dicts[0]["priority"] == "FILE_SPECIFIC"


# ---------------------------------------------------------------------------
# RuleEngine.list_all_rules + RuleRegistry.list_all_rules
# ---------------------------------------------------------------------------


def test_engine_list_all_rules_count() -> None:
    """list_all_rules() returns all 75 rules (1 general + 8 cross + 60 modules + 6 file)."""
    engine = RuleEngine(RULES_ROOT)
    all_rules = engine.list_all_rules()
    assert len(all_rules) == 75


def test_engine_list_all_rules_sorted() -> None:
    """list_all_rules() is sorted FILE_SPECIFIC first, GENERAL last."""
    engine = RuleEngine(RULES_ROOT)
    all_rules = engine.list_all_rules()
    priorities = [r.priority.value for r in all_rules]
    assert priorities == sorted(priorities)
    # First item must be FILE_SPECIFIC (value 1)
    assert all_rules[0].priority.value == 1
    # Last item must be GENERAL (value 4)
    assert all_rules[-1].priority.value == 4


def test_engine_list_all_rules_no_duplicates() -> None:
    """list_all_rules() contains no duplicate (name, priority) pairs.

    The same name can appear at different priority levels (e.g. 'data_visualization'
    exists as both a MODULE rule and a CROSS_MODULE rule).  The uniqueness
    invariant is on (name, priority), not name alone.
    """
    engine = RuleEngine(RULES_ROOT)
    pairs = [(r.name, r.priority) for r in engine.list_all_rules()]
    assert len(pairs) == len(set(pairs))


# ---------------------------------------------------------------------------
# New MCP tools — rules_get_section, rules_search,
# rules_list_cross_module, rules_list_file_specific, rules_list_all
# ---------------------------------------------------------------------------


def test_mcp_rules_get_section_found() -> None:
    """rules_get_section returns section dict for a known module + section 0."""
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_section

    result = rules_get_section("agentic_memory", 0)
    assert result is not None
    assert result["number"] == 0
    assert "title" in result
    assert "content" in result


def test_mcp_rules_get_section_not_found_rule() -> None:
    """rules_get_section returns None for an unknown module."""
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_section

    assert rules_get_section("nonexistent_module_xyzzy", 0) is None


def test_mcp_rules_get_section_not_found_section() -> None:
    """rules_get_section returns None when section number does not exist."""
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_section

    assert rules_get_section("agents", 99) is None


def test_mcp_rules_search_finds_matches() -> None:
    """rules_search returns non-empty list for a common term."""
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_search

    results = rules_search("Python")
    assert isinstance(results, list)
    assert len(results) > 0
    first = results[0]
    assert "name" in first
    assert "priority" in first
    assert "file_path" in first


def test_mcp_rules_search_no_matches() -> None:
    """rules_search returns empty list for an improbable query."""
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_search

    results = rules_search("xyzzy_improbable_string_9999")
    assert results == []


def test_mcp_rules_list_cross_module() -> None:
    """rules_list_cross_module returns exactly 8 names."""
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_cross_module

    names = rules_list_cross_module()
    assert isinstance(names, list)
    assert len(names) == 8
    assert "logging_monitoring" in names


def test_mcp_rules_list_file_specific() -> None:
    """rules_list_file_specific returns at least python and yaml."""
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_file_specific

    names = rules_list_file_specific()
    assert isinstance(names, list)
    assert "python" in names
    assert "yaml" in names


def test_mcp_rules_list_all() -> None:
    """rules_list_all returns 75 summary dicts, FILE_SPECIFIC first."""
    from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_all

    all_rules = rules_list_all()
    assert isinstance(all_rules, list)
    assert len(all_rules) == 75
    assert all_rules[0]["priority"] == "FILE_SPECIFIC"
    assert all_rules[-1]["priority"] == "GENERAL"

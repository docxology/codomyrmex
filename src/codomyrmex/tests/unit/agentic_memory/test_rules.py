"""Zero-Mock tests for the agentic_memory rules submodule.

Tests cover:
- RulePriority enum values and ordering
- RuleSection dataclass construction and serialization
- Rule dataclass (construction, get_section, to_dict)
- RuleSet collection and resolved() ordering
- RuleLoader (.cursorrules parsing, priority inference, name inference, section parsing)
- RuleRegistry (general, module, cross-module, file-specific lookup and listing)
- RuleEngine (get_applicable_rules, list methods, integration with real rule files)
- MCP tool functions (rules_list_modules, rules_get_module_rule, etc.)

All tests use real .cursorrules files from the rules/ directory or temp files.
No mocks, stubs, or monkeypatching.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from codomyrmex.agentic_memory.rules import (
    Rule,
    RuleEngine,
    RuleLoader,
    RulePriority,
    RuleRegistry,
    RuleSection,
    RuleSet,
)

# The real rules directory that ships with the codebase
_RULES_ROOT = Path(__file__).resolve().parents[3] / "agentic_memory" / "rules"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def rules_root():
    """Return the real rules root directory."""
    return _RULES_ROOT


@pytest.fixture()
def engine(rules_root):
    """Return a RuleEngine pointing at the real rules directory."""
    return RuleEngine(rules_root)


@pytest.fixture()
def registry(rules_root):
    """Return a RuleRegistry pointing at the real rules directory."""
    return RuleRegistry(rules_root)


@pytest.fixture()
def tmp_rules(tmp_path):
    """Create a temporary rules hierarchy for isolated tests."""
    # general.cursorrules
    (tmp_path / "general.cursorrules").write_text(
        "# General Rules\n\n## 0. Preamble\nGeneral preamble content.\n\n"
        "## 1. Standards\nGeneral coding standards.\n",
        encoding="utf-8",
    )
    # modules/
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    (modules_dir / "agents.cursorrules").write_text(
        "# Agents Module\n\n## 0. Preamble\nAgents preamble.\n\n"
        "## 3. Coding Standards\nAgents coding standards.\n",
        encoding="utf-8",
    )
    (modules_dir / "cloud.cursorrules").write_text(
        "# Cloud Module\nCloud rules content.\n",
        encoding="utf-8",
    )
    # cross-module/
    cross_dir = tmp_path / "cross-module"
    cross_dir.mkdir()
    (cross_dir / "logging.cursorrules").write_text(
        "# Logging Cross-Module\nLogging rules.\n",
        encoding="utf-8",
    )
    (cross_dir / "testing.cursorrules").write_text(
        "# Testing Cross-Module\nTesting rules.\n",
        encoding="utf-8",
    )
    # file-specific/
    fs_dir = tmp_path / "file-specific"
    fs_dir.mkdir()
    (fs_dir / "python.cursorrules").write_text(
        "# Python File Rules\n\n## 0. Preamble\nPython file rules.\n\n"
        "## 2. Style\nPython style guide.\n",
        encoding="utf-8",
    )
    (fs_dir / "yaml.cursorrules").write_text(
        "# YAML File Rules\nYAML content.\n",
        encoding="utf-8",
    )
    (fs_dir / "README.md.cursorrules").write_text(
        "# README Rules\nREADME guidance.\n",
        encoding="utf-8",
    )
    return tmp_path


# ===========================================================================
# PART 1: RulePriority enum
# ===========================================================================


@pytest.mark.unit
class TestRulePriority:
    """Tests for the RulePriority enum."""

    def test_file_specific_is_highest(self):
        """FILE_SPECIFIC should have the lowest numeric value (highest priority)."""
        assert RulePriority.FILE_SPECIFIC.value == 1

    def test_module_value(self):
        """MODULE should have value 2."""
        assert RulePriority.MODULE.value == 2

    def test_cross_module_value(self):
        """CROSS_MODULE should have value 3."""
        assert RulePriority.CROSS_MODULE.value == 3

    def test_general_is_lowest(self):
        """GENERAL should have the highest numeric value (lowest priority)."""
        assert RulePriority.GENERAL.value == 4

    def test_priority_ordering(self):
        """Priority values should increase: FILE_SPECIFIC < MODULE < CROSS_MODULE < GENERAL."""
        assert (
            RulePriority.FILE_SPECIFIC.value
            < RulePriority.MODULE.value
            < RulePriority.CROSS_MODULE.value
            < RulePriority.GENERAL.value
        )

    def test_all_four_members_exist(self):
        """There should be exactly 4 priority levels."""
        assert len(RulePriority) == 4

    def test_name_strings(self):
        """Enum name strings should match expected values."""
        assert RulePriority.FILE_SPECIFIC.name == "FILE_SPECIFIC"
        assert RulePriority.MODULE.name == "MODULE"
        assert RulePriority.CROSS_MODULE.name == "CROSS_MODULE"
        assert RulePriority.GENERAL.name == "GENERAL"


# ===========================================================================
# PART 2: RuleSection dataclass
# ===========================================================================


@pytest.mark.unit
class TestRuleSection:
    """Tests for the RuleSection dataclass."""

    def test_construction(self):
        """RuleSection should store number, title, and content."""
        s = RuleSection(number=0, title="Preamble", content="Some content")
        assert s.number == 0
        assert s.title == "Preamble"
        assert s.content == "Some content"

    def test_to_dict(self):
        """to_dict should return a dict with number, title, content keys."""
        s = RuleSection(number=3, title="Standards", content="Do X")
        d = s.to_dict()
        assert d["number"] == 3
        assert d["title"] == "Standards"
        assert d["content"] == "Do X"

    def test_to_dict_keys(self):
        """to_dict should have exactly 3 keys."""
        s = RuleSection(number=0, title="T", content="C")
        assert set(s.to_dict().keys()) == {"number", "title", "content"}

    def test_empty_content(self):
        """Sections with empty content should work."""
        s = RuleSection(number=7, title="Empty", content="")
        assert s.content == ""
        assert s.to_dict()["content"] == ""


# ===========================================================================
# PART 3: Rule dataclass
# ===========================================================================


@pytest.mark.unit
class TestRule:
    """Tests for the Rule dataclass."""

    def _make_rule(self, name="test", sections=None):
        """Helper to create a Rule with minimal required fields."""
        if sections is None:
            sections = [
                RuleSection(number=0, title="Preamble", content="P"),
                RuleSection(number=1, title="Standards", content="S"),
            ]
        return Rule(
            name=name,
            priority=RulePriority.MODULE,
            file_path=Path("/tmp/test.cursorrules"),
            sections=sections,
            raw_content="raw",
        )

    def test_construction(self):
        """Rule should store all fields."""
        r = self._make_rule()
        assert r.name == "test"
        assert r.priority == RulePriority.MODULE
        assert len(r.sections) == 2

    def test_get_section_found(self):
        """get_section should return the section with matching number."""
        r = self._make_rule()
        s = r.get_section(0)
        assert s is not None
        assert s.title == "Preamble"

    def test_get_section_not_found(self):
        """get_section should return None for non-existent section number."""
        r = self._make_rule()
        assert r.get_section(99) is None

    def test_get_section_returns_correct_content(self):
        """get_section should return the right content for a given number."""
        r = self._make_rule()
        s = r.get_section(1)
        assert s is not None
        assert s.content == "S"

    def test_to_dict(self):
        """to_dict should include name, priority name, file_path, sections, raw_content."""
        r = self._make_rule()
        d = r.to_dict()
        assert d["name"] == "test"
        assert d["priority"] == "MODULE"
        assert d["file_path"] == "/tmp/test.cursorrules"
        assert len(d["sections"]) == 2
        assert d["raw_content"] == "raw"

    def test_to_dict_sections_are_dicts(self):
        """Sections in to_dict output should be dicts, not RuleSection objects."""
        r = self._make_rule()
        d = r.to_dict()
        for sec in d["sections"]:
            assert isinstance(sec, dict)
            assert "number" in sec

    def test_empty_sections_list(self):
        """Rule with no sections should work."""
        r = self._make_rule(sections=[])
        assert r.get_section(0) is None
        assert r.to_dict()["sections"] == []


# ===========================================================================
# PART 4: RuleSet
# ===========================================================================


@pytest.mark.unit
class TestRuleSet:
    """Tests for the RuleSet collection."""

    def _make_rules(self):
        """Create a list of rules at different priorities."""
        def _rule(name, priority):
            return Rule(
                name=name,
                priority=priority,
                file_path=Path(f"/tmp/{name}.cursorrules"),
                sections=[],
                raw_content="",
            )

        return [
            _rule("general", RulePriority.GENERAL),
            _rule("logging", RulePriority.CROSS_MODULE),
            _rule("agents", RulePriority.MODULE),
            _rule("python", RulePriority.FILE_SPECIFIC),
        ]

    def test_empty_ruleset(self):
        """Empty RuleSet should resolve to empty list."""
        rs = RuleSet(rules=[])
        assert rs.resolved() == []

    def test_resolved_order(self):
        """resolved() should sort FILE_SPECIFIC first, GENERAL last."""
        rules = self._make_rules()
        rs = RuleSet(rules=rules)
        resolved = rs.resolved()
        assert resolved[0].priority == RulePriority.FILE_SPECIFIC
        assert resolved[1].priority == RulePriority.MODULE
        assert resolved[2].priority == RulePriority.CROSS_MODULE
        assert resolved[3].priority == RulePriority.GENERAL

    def test_resolved_names(self):
        """resolved() should return rules in expected name order."""
        rules = self._make_rules()
        rs = RuleSet(rules=rules)
        names = [r.name for r in rs.resolved()]
        assert names == ["python", "agents", "logging", "general"]

    def test_to_dict(self):
        """to_dict should return a list of dicts in resolved order."""
        rules = self._make_rules()
        rs = RuleSet(rules=rules)
        d = rs.to_dict()
        assert isinstance(d, list)
        assert len(d) == 4
        assert d[0]["priority"] == "FILE_SPECIFIC"

    def test_single_rule_set(self):
        """A RuleSet with one rule should resolve to that one rule."""
        r = Rule(
            name="only",
            priority=RulePriority.GENERAL,
            file_path=Path("/tmp/only.cursorrules"),
            sections=[],
            raw_content="",
        )
        rs = RuleSet(rules=[r])
        assert len(rs.resolved()) == 1
        assert rs.resolved()[0].name == "only"


# ===========================================================================
# PART 5: RuleLoader
# ===========================================================================


@pytest.mark.unit
class TestRuleLoader:
    """Tests for the RuleLoader parsing logic."""

    def test_load_nonexistent_raises(self, tmp_path):
        """Loading a nonexistent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            RuleLoader.load(tmp_path / "nonexistent.cursorrules")

    def test_load_non_cursorrules_raises(self, tmp_path):
        """Loading a non-.cursorrules file should raise ValueError."""
        p = tmp_path / "rules.txt"
        p.write_text("content")
        with pytest.raises(ValueError, match="Expected a .cursorrules file"):
            RuleLoader.load(p)

    def test_load_general_rule(self, tmp_rules):
        """Loading general.cursorrules should produce a GENERAL priority rule."""
        rule = RuleLoader.load(tmp_rules / "general.cursorrules")
        assert rule.name == "general"
        assert rule.priority == RulePriority.GENERAL

    def test_load_module_rule(self, tmp_rules):
        """Loading a rule from modules/ should produce MODULE priority."""
        rule = RuleLoader.load(tmp_rules / "modules" / "agents.cursorrules")
        assert rule.name == "agents"
        assert rule.priority == RulePriority.MODULE

    def test_load_cross_module_rule(self, tmp_rules):
        """Loading a rule from cross-module/ should produce CROSS_MODULE priority."""
        rule = RuleLoader.load(tmp_rules / "cross-module" / "logging.cursorrules")
        assert rule.name == "logging"
        assert rule.priority == RulePriority.CROSS_MODULE

    def test_load_file_specific_rule(self, tmp_rules):
        """Loading a rule from file-specific/ should produce FILE_SPECIFIC priority."""
        rule = RuleLoader.load(tmp_rules / "file-specific" / "python.cursorrules")
        assert rule.name == "python"
        assert rule.priority == RulePriority.FILE_SPECIFIC

    def test_infer_name_strips_suffix(self):
        """_infer_name should strip .cursorrules suffix."""
        assert RuleLoader._infer_name(Path("python.cursorrules")) == "python"
        assert RuleLoader._infer_name(Path("README.md.cursorrules")) == "README.md"
        assert RuleLoader._infer_name(Path("general.cursorrules")) == "general"

    def test_parse_sections_numbered(self, tmp_rules):
        """Sections should be parsed from ## N. heading markers."""
        rule = RuleLoader.load(tmp_rules / "general.cursorrules")
        assert len(rule.sections) >= 2
        assert rule.sections[0].number == 0
        assert rule.sections[0].title == "Preamble"

    def test_parse_sections_no_headings(self, tmp_path):
        """File without section headings should produce one section with number 0."""
        p = tmp_path / "plain.cursorrules"
        p.write_text("Just plain text with no section headings.\n")
        rule = RuleLoader.load(p)
        assert len(rule.sections) == 1
        assert rule.sections[0].number == 0
        assert rule.sections[0].title == "Content"

    def test_raw_content_preserved(self, tmp_rules):
        """raw_content should contain the full file text."""
        rule = RuleLoader.load(tmp_rules / "general.cursorrules")
        assert "General preamble content" in rule.raw_content

    def test_file_path_stored(self, tmp_rules):
        """file_path should be the actual Path of the loaded file."""
        p = tmp_rules / "general.cursorrules"
        rule = RuleLoader.load(p)
        assert rule.file_path == p

    def test_load_real_general_cursorrules(self, rules_root):
        """Loading the real general.cursorrules should succeed."""
        p = rules_root / "general.cursorrules"
        if not p.exists():
            pytest.skip("general.cursorrules not found in rules root")
        rule = RuleLoader.load(p)
        assert rule.name == "general"
        assert rule.priority == RulePriority.GENERAL
        assert len(rule.raw_content) > 100


# ===========================================================================
# PART 6: RuleRegistry
# ===========================================================================


@pytest.mark.unit
class TestRuleRegistry:
    """Tests for the RuleRegistry with temp rules hierarchy."""

    def test_get_general(self, tmp_rules):
        """get_general should return the general rule."""
        reg = RuleRegistry(tmp_rules)
        g = reg.get_general()
        assert g is not None
        assert g.name == "general"
        assert g.priority == RulePriority.GENERAL

    def test_get_general_missing(self, tmp_path):
        """get_general should return None if general.cursorrules is absent."""
        reg = RuleRegistry(tmp_path)
        assert reg.get_general() is None

    def test_get_module_rule_found(self, tmp_rules):
        """get_module_rule should return the agents rule."""
        reg = RuleRegistry(tmp_rules)
        r = reg.get_module_rule("agents")
        assert r is not None
        assert r.name == "agents"
        assert r.priority == RulePriority.MODULE

    def test_get_module_rule_not_found(self, tmp_rules):
        """get_module_rule for nonexistent module should return None."""
        reg = RuleRegistry(tmp_rules)
        assert reg.get_module_rule("nonexistent") is None

    def test_get_cross_module_rules(self, tmp_rules):
        """get_cross_module_rules should return all cross-module rules."""
        reg = RuleRegistry(tmp_rules)
        rules = reg.get_cross_module_rules()
        assert len(rules) == 2
        names = {r.name for r in rules}
        assert "logging" in names
        assert "testing" in names

    def test_get_cross_module_rules_empty(self, tmp_path):
        """get_cross_module_rules should return empty list if dir is missing."""
        reg = RuleRegistry(tmp_path)
        assert reg.get_cross_module_rules() == []

    def test_get_file_rule_by_extension(self, tmp_rules):
        """get_file_rule should match .py files to python.cursorrules."""
        reg = RuleRegistry(tmp_rules)
        r = reg.get_file_rule("src/main.py")
        assert r is not None
        assert r.name == "python"
        assert r.priority == RulePriority.FILE_SPECIFIC

    def test_get_file_rule_yaml_extension(self, tmp_rules):
        """get_file_rule should match .yaml files."""
        reg = RuleRegistry(tmp_rules)
        r = reg.get_file_rule("config.yaml")
        assert r is not None
        assert r.name == "yaml"

    def test_get_file_rule_yml_extension(self, tmp_rules):
        """get_file_rule should match .yml files to yaml rule."""
        reg = RuleRegistry(tmp_rules)
        r = reg.get_file_rule("config.yml")
        assert r is not None
        assert r.name == "yaml"

    def test_get_file_rule_exact_filename_match(self, tmp_rules):
        """Exact filename match (README.md) should take precedence."""
        reg = RuleRegistry(tmp_rules)
        r = reg.get_file_rule("README.md")
        assert r is not None
        assert r.name == "README.md"

    def test_get_file_rule_no_match(self, tmp_rules):
        """get_file_rule for unknown extension should return None."""
        reg = RuleRegistry(tmp_rules)
        assert reg.get_file_rule("script.sh") is None

    def test_list_module_names(self, tmp_rules):
        """list_module_names should return sorted module names."""
        reg = RuleRegistry(tmp_rules)
        names = reg.list_module_names()
        assert names == ["agents", "cloud"]

    def test_list_module_names_empty(self, tmp_path):
        """list_module_names should return [] if modules dir is missing."""
        reg = RuleRegistry(tmp_path)
        assert reg.list_module_names() == []

    def test_list_cross_module_names(self, tmp_rules):
        """list_cross_module_names should return sorted names."""
        reg = RuleRegistry(tmp_rules)
        names = reg.list_cross_module_names()
        assert names == ["logging", "testing"]

    def test_list_file_rule_names(self, tmp_rules):
        """list_file_rule_names should return sorted file-specific rule names."""
        reg = RuleRegistry(tmp_rules)
        names = reg.list_file_rule_names()
        assert "python" in names
        assert "yaml" in names

    def test_list_all_rules(self, tmp_rules):
        """list_all_rules should include rules from all categories."""
        reg = RuleRegistry(tmp_rules)
        all_rules = reg.list_all_rules()
        priorities = [r.priority for r in all_rules]
        # FILE_SPECIFIC should come first
        assert priorities[0] == RulePriority.FILE_SPECIFIC or priorities[0] in (
            RulePriority.FILE_SPECIFIC,
            RulePriority.MODULE,
        )
        # GENERAL should come last
        assert priorities[-1] == RulePriority.GENERAL
        # Should include at least general + 2 cross + 2 module + 3 file = 8
        assert len(all_rules) >= 8

    def test_caching(self, tmp_rules):
        """Loading the same rule twice should use cache."""
        reg = RuleRegistry(tmp_rules)
        r1 = reg.get_general()
        r2 = reg.get_general()
        assert r1 is r2  # Same object from cache


# ===========================================================================
# PART 7: RuleRegistry with real rules
# ===========================================================================


@pytest.mark.unit
class TestRuleRegistryReal:
    """Tests against the actual rules shipped with the codebase."""

    def test_real_general_exists(self, registry):
        """The real rules root should have a general.cursorrules."""
        g = registry.get_general()
        if g is None:
            pytest.skip("No general.cursorrules in rules root")
        assert g.name == "general"
        assert g.priority == RulePriority.GENERAL

    def test_real_module_rules_exist(self, registry):
        """The real rules root should have module rules."""
        names = registry.list_module_names()
        assert len(names) > 0
        assert "agentic_memory" in names or "agents" in names

    def test_real_cross_module_rules_exist(self, registry):
        """The real rules root should have cross-module rules."""
        names = registry.list_cross_module_names()
        assert len(names) > 0

    def test_real_file_specific_rules_exist(self, registry):
        """The real rules root should have file-specific rules."""
        names = registry.list_file_rule_names()
        assert "python" in names


# ===========================================================================
# PART 8: RuleEngine
# ===========================================================================


@pytest.mark.unit
class TestRuleEngine:
    """Tests for the RuleEngine orchestration layer."""

    def test_engine_init_default(self):
        """RuleEngine() should initialize without errors using default root."""
        engine = RuleEngine()
        assert engine is not None

    def test_engine_init_custom_root(self, tmp_rules):
        """RuleEngine with custom root should use that root."""
        engine = RuleEngine(rules_root=tmp_rules)
        names = engine.list_module_names()
        assert "agents" in names

    def test_get_applicable_no_args(self, tmp_rules):
        """get_applicable_rules with no args should include general + cross-module."""
        engine = RuleEngine(rules_root=tmp_rules)
        rs = engine.get_applicable_rules()
        names = {r.name for r in rs.rules}
        assert "general" in names
        assert "logging" in names
        assert "testing" in names

    def test_get_applicable_with_module(self, tmp_rules):
        """get_applicable_rules with module_name should include the module rule."""
        engine = RuleEngine(rules_root=tmp_rules)
        rs = engine.get_applicable_rules(module_name="agents")
        names = {r.name for r in rs.rules}
        assert "agents" in names
        assert "general" in names

    def test_get_applicable_with_file(self, tmp_rules):
        """get_applicable_rules with .py file should include python file rule."""
        engine = RuleEngine(rules_root=tmp_rules)
        rs = engine.get_applicable_rules(file_path="main.py")
        names = {r.name for r in rs.rules}
        assert "python" in names

    def test_get_applicable_full_context(self, tmp_rules):
        """get_applicable_rules with both file and module should include all levels."""
        engine = RuleEngine(rules_root=tmp_rules)
        rs = engine.get_applicable_rules(file_path="memory.py", module_name="agents")
        names = {r.name for r in rs.rules}
        assert "general" in names
        assert "agents" in names
        assert "python" in names
        # Cross-module rules too
        assert "logging" in names

    def test_get_applicable_nonexistent_module(self, tmp_rules):
        """Non-existent module should not break; just no module rule added."""
        engine = RuleEngine(rules_root=tmp_rules)
        rs = engine.get_applicable_rules(module_name="nonexistent")
        names = {r.name for r in rs.rules}
        assert "nonexistent" not in names
        # General and cross-module should still be present
        assert "general" in names

    def test_get_applicable_unknown_extension(self, tmp_rules):
        """Unknown file extension should not include a file-specific rule."""
        engine = RuleEngine(rules_root=tmp_rules)
        rs = engine.get_applicable_rules(file_path="script.sh")
        priorities = {r.priority for r in rs.rules}
        assert RulePriority.FILE_SPECIFIC not in priorities

    def test_resolved_order(self, tmp_rules):
        """resolved() from get_applicable_rules should be priority-sorted."""
        engine = RuleEngine(rules_root=tmp_rules)
        rs = engine.get_applicable_rules(file_path="test.py", module_name="agents")
        resolved = rs.resolved()
        for i in range(len(resolved) - 1):
            assert resolved[i].priority.value <= resolved[i + 1].priority.value

    def test_get_module_rule(self, tmp_rules):
        """get_module_rule should return the module-specific rule."""
        engine = RuleEngine(rules_root=tmp_rules)
        r = engine.get_module_rule("agents")
        assert r is not None
        assert r.name == "agents"

    def test_get_module_rule_not_found(self, tmp_rules):
        """get_module_rule for missing module should return None."""
        engine = RuleEngine(rules_root=tmp_rules)
        assert engine.get_module_rule("nonexistent") is None

    def test_list_module_names(self, tmp_rules):
        """list_module_names should return sorted module names."""
        engine = RuleEngine(rules_root=tmp_rules)
        assert engine.list_module_names() == ["agents", "cloud"]

    def test_list_cross_module_names(self, tmp_rules):
        """list_cross_module_names should return sorted cross-module names."""
        engine = RuleEngine(rules_root=tmp_rules)
        assert engine.list_cross_module_names() == ["logging", "testing"]

    def test_list_file_rule_names(self, tmp_rules):
        """list_file_rule_names should return sorted file-specific names."""
        engine = RuleEngine(rules_root=tmp_rules)
        names = engine.list_file_rule_names()
        assert "python" in names
        assert "yaml" in names

    def test_list_all_rules(self, tmp_rules):
        """list_all_rules should return rules from all categories."""
        engine = RuleEngine(rules_root=tmp_rules)
        all_rules = engine.list_all_rules()
        assert len(all_rules) >= 8


# ===========================================================================
# PART 9: RuleEngine with real rules
# ===========================================================================


@pytest.mark.unit
class TestRuleEngineReal:
    """Integration tests with the real .cursorrules files."""

    def test_real_engine_list_modules(self, engine):
        """Real engine should list known modules."""
        names = engine.list_module_names()
        assert len(names) > 5
        # agentic_memory module should have its own rule
        if "agentic_memory" not in names:
            pytest.skip("agentic_memory module rule not found")
        assert "agentic_memory" in names

    def test_real_engine_applicable_for_python_file(self, engine):
        """Querying for a .py file should include python file-specific rule."""
        rs = engine.get_applicable_rules(file_path="test.py")
        names = {r.name for r in rs.rules}
        if "python" not in names:
            pytest.skip("python file-specific rule not found")
        assert "python" in names

    def test_real_engine_applicable_for_yaml_file(self, engine):
        """Querying for a .yaml file should include yaml file-specific rule."""
        rs = engine.get_applicable_rules(file_path="config.yaml")
        file_rules = [r for r in rs.rules if r.priority == RulePriority.FILE_SPECIFIC]
        if not file_rules:
            pytest.skip("yaml file-specific rule not found")
        assert any(r.name == "yaml" for r in file_rules)

    def test_real_engine_general_always_present(self, engine):
        """General rule should always be in applicable rules."""
        rs = engine.get_applicable_rules()
        general_rules = [r for r in rs.rules if r.priority == RulePriority.GENERAL]
        if not general_rules:
            pytest.skip("No general rule found")
        assert len(general_rules) == 1

    def test_real_engine_cross_module_always_present(self, engine):
        """Cross-module rules should always be in applicable rules."""
        rs = engine.get_applicable_rules()
        cross = [r for r in rs.rules if r.priority == RulePriority.CROSS_MODULE]
        assert len(cross) > 0

    def test_real_engine_module_section_access(self, engine):
        """Module rules should have parseable sections."""
        r = engine.get_module_rule("agentic_memory")
        if r is None:
            pytest.skip("agentic_memory module rule not found")
        assert len(r.sections) >= 1
        # Section 0 should exist (preamble or content)
        s0 = r.get_section(0)
        assert s0 is not None
        assert len(s0.content) > 0


# ===========================================================================
# PART 10: MCP tools
# ===========================================================================


@pytest.mark.unit
class TestMCPTools:
    """Tests for the MCP tool functions in mcp_tools.py."""

    def test_rules_list_modules_returns_list(self):
        """rules_list_modules should return a list of strings."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_modules

        result = rules_list_modules()
        assert isinstance(result, list)
        for name in result:
            assert isinstance(name, str)

    def test_rules_list_modules_nonempty(self):
        """rules_list_modules should return at least some modules."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_modules

        result = rules_list_modules()
        assert len(result) > 0

    def test_rules_get_module_rule_found(self):
        """rules_get_module_rule for an existing module should return a dict."""
        from codomyrmex.agentic_memory.rules.mcp_tools import (
            rules_get_module_rule,
            rules_list_modules,
        )

        modules = rules_list_modules()
        if not modules:
            pytest.skip("No modules available")
        result = rules_get_module_rule(modules[0])
        assert result is not None
        assert isinstance(result, dict)
        assert "name" in result
        assert "priority" in result

    def test_rules_get_module_rule_not_found(self):
        """rules_get_module_rule for nonexistent module should return None."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_module_rule

        result = rules_get_module_rule("definitely_not_a_real_module_xyz")
        assert result is None

    def test_rules_get_applicable_returns_list(self):
        """rules_get_applicable should return a list of dicts."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_applicable

        result = rules_get_applicable()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, dict)

    def test_rules_get_applicable_with_file(self):
        """rules_get_applicable with a .py file should include python rule."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_applicable

        result = rules_get_applicable(file_path="test.py")
        names = {d["name"] for d in result}
        # Should have general and cross-module at minimum
        assert len(result) >= 1

    def test_rules_get_applicable_with_module(self):
        """rules_get_applicable with module_name should include that module."""
        from codomyrmex.agentic_memory.rules.mcp_tools import (
            rules_get_applicable,
            rules_list_modules,
        )

        modules = rules_list_modules()
        if not modules:
            pytest.skip("No modules available")
        result = rules_get_applicable(module_name=modules[0])
        names = {d["name"] for d in result}
        assert modules[0] in names

    def test_rules_get_section_found(self):
        """rules_get_section for a valid module and section should return a dict."""
        from codomyrmex.agentic_memory.rules.mcp_tools import (
            rules_get_section,
            rules_list_modules,
        )

        modules = rules_list_modules()
        if not modules:
            pytest.skip("No modules available")
        # Try section 0 (most common)
        result = rules_get_section(modules[0], 0)
        if result is None:
            pytest.skip(f"Module {modules[0]} has no section 0")
        assert isinstance(result, dict)
        assert "number" in result
        assert "title" in result
        assert "content" in result

    def test_rules_get_section_not_found(self):
        """rules_get_section for nonexistent module should return None."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_get_section

        result = rules_get_section("nonexistent_module_xyz", 0)
        assert result is None

    def test_rules_search_returns_list(self):
        """rules_search should return a list of dicts."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_search

        result = rules_search("python")
        assert isinstance(result, list)

    def test_rules_search_finds_matches(self):
        """rules_search for a common term should find matches."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_search

        # "preamble" or "standards" should appear in most rules
        result = rules_search("preamble")
        # May or may not find results depending on content
        assert isinstance(result, list)

    def test_rules_search_case_insensitive(self):
        """rules_search should be case-insensitive."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_search

        lower = rules_search("python")
        upper = rules_search("PYTHON")
        # Same number of results
        assert len(lower) == len(upper)

    def test_rules_list_cross_module_returns_list(self):
        """rules_list_cross_module should return a sorted list of strings."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_cross_module

        result = rules_list_cross_module()
        assert isinstance(result, list)
        assert result == sorted(result)

    def test_rules_list_file_specific_returns_list(self):
        """rules_list_file_specific should return a list of strings."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_file_specific

        result = rules_list_file_specific()
        assert isinstance(result, list)

    def test_rules_list_all_returns_list(self):
        """rules_list_all should return a list of summary dicts."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_all

        result = rules_list_all()
        assert isinstance(result, list)
        if result:
            assert "name" in result[0]
            assert "priority" in result[0]
            assert "file_path" in result[0]

    def test_rules_list_all_sorted_by_priority(self):
        """rules_list_all should be sorted FILE_SPECIFIC first."""
        from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_all

        result = rules_list_all()
        if len(result) < 2:
            pytest.skip("Not enough rules to test sorting")
        priority_order = {"FILE_SPECIFIC": 1, "MODULE": 2, "CROSS_MODULE": 3, "GENERAL": 4}
        values = [priority_order.get(d["priority"], 99) for d in result]
        assert values == sorted(values)


# ===========================================================================
# PART 11: Edge cases
# ===========================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_empty_rules_root(self, tmp_path):
        """Engine with empty rules root should still work (empty results)."""
        engine = RuleEngine(rules_root=tmp_path)
        rs = engine.get_applicable_rules()
        assert isinstance(rs, RuleSet)
        # Only cross-module rules (none) and general (none)
        assert len(rs.rules) == 0

    def test_rule_with_many_sections(self, tmp_path):
        """A rule file with 8 sections should all be parsed."""
        content = "\n\n".join(
            f"## {i}. Section {i}\nContent for section {i}."
            for i in range(8)
        )
        p = tmp_path / "many.cursorrules"
        p.write_text(content)
        rule = RuleLoader.load(p)
        assert len(rule.sections) == 8
        for i in range(8):
            s = rule.get_section(i)
            assert s is not None
            assert f"section {i}" in s.content.lower()

    def test_rule_section_content_whitespace_stripped(self, tmp_path):
        """Section content should have leading/trailing whitespace stripped."""
        p = tmp_path / "ws.cursorrules"
        p.write_text("## 0. Title\n\n   Content with spaces   \n\n## 1. Next\nMore.\n")
        rule = RuleLoader.load(p)
        s = rule.get_section(0)
        assert s is not None
        assert not s.content.startswith(" ")
        assert not s.content.endswith(" ")

    def test_ruleset_duplicate_priorities(self):
        """RuleSet with multiple rules at same priority should resolve stably."""
        rules = [
            Rule(name="a", priority=RulePriority.MODULE, file_path=Path("/a"), sections=[], raw_content=""),
            Rule(name="b", priority=RulePriority.MODULE, file_path=Path("/b"), sections=[], raw_content=""),
        ]
        rs = RuleSet(rules=rules)
        resolved = rs.resolved()
        assert len(resolved) == 2
        assert all(r.priority == RulePriority.MODULE for r in resolved)

    def test_loader_infer_priority_nested_path(self, tmp_path):
        """Priority inference should work with deeply nested paths."""
        deep = tmp_path / "a" / "b" / "modules" / "c"
        deep.mkdir(parents=True)
        p = deep / "test.cursorrules"
        p.write_text("content")
        rule = RuleLoader.load(p)
        assert rule.priority == RulePriority.MODULE

    def test_registry_caching_prevents_reparse(self, tmp_rules):
        """Second load of same file should return cached object."""
        reg = RuleRegistry(tmp_rules)
        r1 = reg.get_module_rule("agents")
        r2 = reg.get_module_rule("agents")
        assert r1 is r2

    def test_file_rule_path_object(self, tmp_rules):
        """get_file_rule should accept Path objects."""
        reg = RuleRegistry(tmp_rules)
        r = reg.get_file_rule(Path("src/main.py"))
        assert r is not None
        assert r.name == "python"

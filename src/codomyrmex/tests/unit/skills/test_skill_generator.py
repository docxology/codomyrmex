"""Tests for skill_generator — SKILL.md file generation logic.

Tests the data constants, tool grouping, phase mapping extraction,
and SKILL.md rendering without touching the filesystem or MCP bridge.
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.skills.skill_generator import (
    CATEGORY_GROUP_MAP,
    DEFAULT_PHASE_MAPS,
    SKILL_DESCRIPTIONS,
    _auto_description,
    _build_key_tools_table,
    _build_phase_mapping,
    _build_trust_note,
    extract_keep_blocks,
    extract_phase_mapping,
    group_by_skill,
    render_skill_md,
    write_skill,
)

# ── Constants ────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_category_group_map_has_expected_entries():
    """CATEGORY_GROUP_MAP should have all major skill groups."""
    assert len(CATEGORY_GROUP_MAP) >= 50
    assert CATEGORY_GROUP_MAP["git_operations"] == "CodomyrmexGit"
    assert CATEGORY_GROUP_MAP["security"] == "CodomyrmexSecurity"
    assert CATEGORY_GROUP_MAP["llm"] == "CodomyrmexAI"
    assert CATEGORY_GROUP_MAP["general"] == "Codomyrmex"


@pytest.mark.unit
def test_skill_descriptions_covers_all_groups():
    """SKILL_DESCRIPTIONS should cover the major skill groups."""
    groups = set(CATEGORY_GROUP_MAP.values())
    described = set(SKILL_DESCRIPTIONS.keys())
    # Every described group should be a real group
    assert described.issubset(groups | {"Codomyrmex"})
    assert len(SKILL_DESCRIPTIONS) >= 10


@pytest.mark.unit
def test_default_phase_maps_structure():
    """DEFAULT_PHASE_MAPS values should map phase names to tool lists."""
    assert len(DEFAULT_PHASE_MAPS) >= 10
    for skill_name, phases in DEFAULT_PHASE_MAPS.items():
        assert isinstance(phases, dict), f"{skill_name} phases should be dict"
        for phase, tools in phases.items():
            assert phase in (
                "OBSERVE", "THINK", "PLAN", "BUILD", "EXECUTE", "VERIFY", "LEARN"
            ), f"Unknown phase {phase} in {skill_name}"
            assert isinstance(tools, list), f"{skill_name}.{phase} should be list"
            assert all(isinstance(t, str) for t in tools)


# ── Grouping ─────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_group_by_skill_known_categories():
    """Tools with known categories should group into the correct skill."""
    tools = [
        {"name": "git_status", "category": "git_operations"},
        {"name": "git_clone", "category": "clone_repository"},
        {"name": "scan_secrets", "category": "security"},
        {"name": "ask_llm", "category": "llm"},
    ]
    groups = group_by_skill(tools)
    assert "CodomyrmexGit" in groups
    assert len(groups["CodomyrmexGit"]) == 2
    assert "CodomyrmexSecurity" in groups
    assert "CodomyrmexAI" in groups


@pytest.mark.unit
def test_group_by_skill_unknown_category():
    """Tools with unknown categories should auto-name the skill."""
    tools = [{"name": "exotic_tool", "category": "exotic_stuff"}]
    groups = group_by_skill(tools)
    assert "CodomyrmexExoticStuff" in groups


@pytest.mark.unit
def test_group_by_skill_no_category():
    """Tools without a category should default to 'general' → Codomyrmex."""
    tools = [{"name": "generic_tool"}]
    groups = group_by_skill(tools)
    assert "Codomyrmex" in groups


# ── Phase Mapping ────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_extract_phase_mapping_defaults():
    """extract_phase_mapping should fall back to DEFAULT_PHASE_MAPS."""
    phases = extract_phase_mapping(["nonexistent_module"], "CodomyrmexGit")
    assert "OBSERVE" in phases
    assert "git_repo_status" in phases["OBSERVE"]


@pytest.mark.unit
def test_extract_phase_mapping_from_pai_md():
    """extract_phase_mapping should extract phases from PAI.md files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a fake PAI.md with phase table
        mod_dir = Path(tmpdir) / "test_module"
        mod_dir.mkdir()
        pai_md = mod_dir / "PAI.md"
        pai_md.write_text(
            "| **OBSERVE** | `scan_stuff`, `check_things` |\n"
            "| **VERIFY** | `verify_stuff` |\n"
        )

        # Monkey-patch _SRC_ROOT temporarily
        import codomyrmex.skills.skill_generator as sg
        orig = sg._SRC_ROOT
        sg._SRC_ROOT = Path(tmpdir)
        try:
            phases = extract_phase_mapping(["test_module"], "UnknownSkill")
            assert "OBSERVE" in phases
            assert "scan_stuff" in phases["OBSERVE"]
            assert "check_things" in phases["OBSERVE"]
            assert "verify_stuff" in phases["VERIFY"]
        finally:
            sg._SRC_ROOT = orig


# ── Keep Blocks ──────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_extract_keep_blocks():
    """Keep blocks should be preserved in existing content."""
    content = (
        "# Skill\n"
        "<!-- keep-start -->Custom user content\nthat spans lines<!-- keep-end -->\n"
        "The rest\n"
        "<!-- keep-start -->Another block<!-- keep-end -->\n"
    )
    blocks = extract_keep_blocks(content)
    assert len(blocks) == 2
    assert "Custom user content" in blocks[0]
    assert "Another block" in blocks[1]


@pytest.mark.unit
def test_extract_keep_blocks_none():
    """No keep blocks should return empty list."""
    assert extract_keep_blocks("# SKILL.md\nNo blocks here.") == []


# ── Rendering ────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_build_trust_note_no_trusted():
    """No trusted tools → empty string."""
    tools = [{"name": "tool1", "trust_level": "VERIFIED"}]
    assert _build_trust_note(tools) == ""


@pytest.mark.unit
def test_build_trust_note_with_trusted():
    """Trusted tools → warning note."""
    tools = [{"name": "run_command", "trust_level": "TRUSTED"}]
    note = _build_trust_note(tools)
    assert "WARNING" in note
    assert "run_command" in note


@pytest.mark.unit
def test_build_key_tools_table():
    """Key Tools table should include all tools sorted."""
    tools = [
        {"name": "b_tool", "description": "Beta tool", "trust_level": "VERIFIED"},
        {"name": "a_tool", "description": "Alpha tool", "trust_level": "TRUSTED"},
    ]
    table = _build_key_tools_table(tools)
    assert "a_tool" in table
    assert "b_tool" in table
    # a_tool should appear before b_tool (sorted)
    assert table.index("a_tool") < table.index("b_tool")


@pytest.mark.unit
def test_build_phase_mapping():
    """Phase mapping table should include all provided phases."""
    phase_map = {"OBSERVE": ["tool1"], "EXECUTE": ["tool2", "tool3"]}
    table = _build_phase_mapping(phase_map)
    assert "OBSERVE" in table
    assert "tool1" in table
    assert "EXECUTE" in table
    assert "tool2" in table


@pytest.mark.unit
def test_build_phase_mapping_empty():
    """Empty phase map → empty string."""
    assert _build_phase_mapping({}) == ""


@pytest.mark.unit
def test_auto_description():
    """Auto-generated descriptions should mention skill and categories."""
    desc = _auto_description("CodomyrmexMagic", ["magic", "wizardry"])
    assert "CodomyrmexMagic" in desc
    assert "magic" in desc


@pytest.mark.unit
def test_render_skill_md_structure():
    """Rendered SKILL.md should have frontmatter, title, and tools table."""
    tools = [
        {"name": "test_tool", "description": "Test", "trust_level": "VERIFIED",
         "category": "general"},
    ]
    result = render_skill_md("TestSkill", tools, ["general"])
    assert "---" in result
    assert "name: TestSkill" in result
    assert "# TestSkill" in result
    assert "test_tool" in result


@pytest.mark.unit
def test_render_skill_md_preserves_keep_blocks():
    """Existing keep blocks should survive re-rendering."""
    existing = "<!-- keep-start -->My custom notes<!-- keep-end -->"
    tools = [{"name": "t1", "description": "D", "trust_level": "VERIFIED", "category": "x"}]
    result = render_skill_md("S", tools, ["x"], existing_content=existing)
    assert "My custom notes" in result


# ── Write ────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_write_skill_dry_run(capsys):
    """Dry-run should print but not write files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        write_skill("TestSkill", "# Content", Path(tmpdir), dry_run=True)
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert not (Path(tmpdir) / "TestSkill" / "SKILL.md").exists()


@pytest.mark.unit
def test_write_skill_creates_file():
    """Write should create the SKILL.md file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        write_skill("TestSkill", "# Content", Path(tmpdir), force=True)
        skill_path = Path(tmpdir) / "TestSkill" / "SKILL.md"
        assert skill_path.exists()
        assert skill_path.read_text() == "# Content"

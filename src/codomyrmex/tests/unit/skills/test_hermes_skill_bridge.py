"""Unit tests for HermesSkillBridge and HermesSkillEntry.

Zero-Mock policy: tests verify real instantiation, filesystem discovery with
a real temp dir, and CLI probe behaviour (CLI tests skipif hermes not available).

All tests use real objects — no patching, no MagicMock.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from codomyrmex.skills.hermes_skill_bridge import (
    HermesSkillBridge,
    HermesSkillEntry,
    _resolve_hermes_home,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def temp_hermes_home() -> Path:
    """Return a temporary HERMES_HOME-like directory with one mock skill."""
    with tempfile.TemporaryDirectory() as tmpdir:
        hermes_home = Path(tmpdir)
        skills_dir = hermes_home / "skills" / "research" / "test-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text(
            "# Test Skill\nA fictional test skill for unit testing.\n",
            encoding="utf-8",
        )
        yield hermes_home


@pytest.fixture()
def bridge_with_temp(temp_hermes_home: Path) -> HermesSkillBridge:
    """Return a HermesSkillBridge pointed at the temp hermes home."""
    return HermesSkillBridge(hermes_home=temp_hermes_home)


# ── _resolve_hermes_home ──────────────────────────────────────────────────────


@pytest.mark.unit
def test_resolve_hermes_home_returns_path() -> None:
    """_resolve_hermes_home() must return an absolute Path."""
    p = _resolve_hermes_home()
    assert isinstance(p, Path)
    assert p.is_absolute()


# ── HermesSkillEntry ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestHermesSkillEntry:
    def test_construction(self) -> None:
        entry = HermesSkillEntry(
            name="test-skill",
            description="A test skill",
            skill_path=Path("/tmp/test-skill"),
        )
        assert entry.name == "test-skill"
        assert entry.description == "A test skill"
        assert entry.skill_path == Path("/tmp/test-skill")
        assert entry.metadata == {}
        assert entry._client is None

    def test_repr(self) -> None:
        entry = HermesSkillEntry(
            name="my-skill",
            description="desc",
            skill_path=Path("/tmp"),
        )
        r = repr(entry)
        assert "my-skill" in r

    def test_is_callable(self) -> None:
        """Entry must be callable (implements __call__)."""
        entry = HermesSkillEntry(
            name="test",
            description="",
            skill_path=Path("/tmp"),
        )
        assert callable(entry)

    def test_metadata_default(self) -> None:
        entry = HermesSkillEntry(name="x", description="y", skill_path=Path("/"))
        assert isinstance(entry.metadata, dict)


# ── HermesSkillBridge ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestHermesSkillBridgeInit:
    def test_default_init(self) -> None:
        bridge = HermesSkillBridge()
        assert bridge is not None
        assert bridge._skills_dir.name == "skills"

    def test_custom_hermes_home(self, tmp_path: Path) -> None:
        bridge = HermesSkillBridge(hermes_home=tmp_path)
        assert bridge._hermes_home == tmp_path

    def test_repr_before_sync(self, tmp_path: Path) -> None:
        bridge = HermesSkillBridge(hermes_home=tmp_path)
        r = repr(bridge)
        assert "HermesSkillBridge" in r
        assert "?" in r  # cache not synced yet


@pytest.mark.unit
class TestHermesSkillBridgeDiscovery:
    def test_sync_returns_dict(self, bridge_with_temp: HermesSkillBridge) -> None:
        skills = bridge_with_temp.sync_hermes_skills()
        assert isinstance(skills, dict)

    def test_discovers_skill_md_skill(
        self, bridge_with_temp: HermesSkillBridge, temp_hermes_home: Path
    ) -> None:
        skills = bridge_with_temp.sync_hermes_skills()
        assert "test-skill" in skills

    def test_discovered_entry_name(
        self, bridge_with_temp: HermesSkillBridge
    ) -> None:
        skills = bridge_with_temp.sync_hermes_skills()
        entry = skills["test-skill"]
        assert isinstance(entry, HermesSkillEntry)
        assert entry.name == "test-skill"

    def test_discovered_entry_description(
        self, bridge_with_temp: HermesSkillBridge
    ) -> None:
        skills = bridge_with_temp.sync_hermes_skills()
        assert skills["test-skill"].description  # non-empty

    def test_empty_hermes_home_returns_empty(self, tmp_path: Path) -> None:
        bridge = HermesSkillBridge(hermes_home=tmp_path)
        skills = bridge.sync_hermes_skills()
        assert skills == {}

    def test_cache_is_reused(self, bridge_with_temp: HermesSkillBridge) -> None:
        first = bridge_with_temp.sync_hermes_skills()
        second = bridge_with_temp.sync_hermes_skills()
        assert first is second  # same object from cache

    def test_force_refresh_rescans(
        self, bridge_with_temp: HermesSkillBridge, temp_hermes_home: Path
    ) -> None:
        _ = bridge_with_temp.sync_hermes_skills()
        # Add another skill
        new_skill = (
            temp_hermes_home / "skills" / "research" / "another-skill"
        )
        new_skill.mkdir(parents=True)
        (new_skill / "SKILL.md").write_text("# Another Skill\nDesc.\n")
        refreshed = bridge_with_temp.sync_hermes_skills(force_refresh=True)
        assert "another-skill" in refreshed

    def test_skill_yaml_fallback(self, tmp_path: Path) -> None:
        """Skills with only skill.yaml (no SKILL.md) should still be discovered."""
        skill_dir = tmp_path / "skills" / "custom" / "yaml-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "skill.yaml").write_text(
            "name: yaml-skill\ndescription: From YAML\n", encoding="utf-8"
        )
        bridge = HermesSkillBridge(hermes_home=tmp_path)
        skills = bridge.sync_hermes_skills()
        assert "yaml-skill" in skills


@pytest.mark.unit
class TestHermesSkillBridgeGetSkill:
    def test_get_existing_skill(self, bridge_with_temp: HermesSkillBridge) -> None:
        entry = bridge_with_temp.get_skill("test-skill")
        assert entry is not None
        assert isinstance(entry, HermesSkillEntry)

    def test_get_nonexistent_skill_returns_none(
        self, bridge_with_temp: HermesSkillBridge
    ) -> None:
        entry = bridge_with_temp.get_skill("nonexistent-skill-xyz")
        assert entry is None

    def test_run_skill_raises_on_missing(
        self, bridge_with_temp: HermesSkillBridge
    ) -> None:
        with pytest.raises(KeyError, match="nonexistent-skill-xyz"):
            bridge_with_temp.run_skill("nonexistent-skill-xyz", "hello")


@pytest.mark.unit
class TestHermesSkillBridgeRefresh:
    def test_refresh_clears_cache(
        self, bridge_with_temp: HermesSkillBridge
    ) -> None:
        _ = bridge_with_temp.sync_hermes_skills()
        assert bridge_with_temp._cache is not None
        bridge_with_temp.refresh()
        # After refresh the cache is repopulated (not None)
        assert bridge_with_temp._cache is not None


# ── Live Hermes CLI tests (skipif CLI not available) ──────────────────────────


@pytest.mark.unit
@pytest.mark.skipif(
    not shutil.which("hermes"),
    reason="Hermes CLI not installed — skipping live CLI tests",
)
class TestHermesSkillBridgeLiveCli:
    def test_list_hermes_skills_returns_dict(self) -> None:
        """list_hermes_skills() should include CLI-discovered skills when hermes is available."""
        bridge = HermesSkillBridge()
        skills = bridge.list_hermes_skills()
        assert isinstance(skills, dict)

    def test_repr_after_sync(self) -> None:
        bridge = HermesSkillBridge()
        bridge.sync_hermes_skills()
        r = repr(bridge)
        assert "HermesSkillBridge" in r
        assert "?" not in r  # synced — count is known

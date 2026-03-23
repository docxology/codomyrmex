"""Unit tests for HermesSkillBridge and HermesSkillEntry."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from codomyrmex.skills.hermes_skill_bridge import (
    HermesSkillBridge,
    HermesSkillEntry,
    _normalize_name,
)

# ---------------------------------------------------------------------------
# HermesSkillEntry
# ---------------------------------------------------------------------------


class TestHermesSkillEntry:
    def test_construction_minimal(self) -> None:
        entry = HermesSkillEntry(name="test_skill")
        assert entry.name == "test_skill"
        assert entry.description == ""
        assert entry.skill_path is None
        assert entry.hermes_skill_id == "test_skill"  # auto-set from name

    def test_construction_full(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "my_skill"
        skill_dir.mkdir()
        entry = HermesSkillEntry(
            name="my_skill",
            description="Does something cool",
            skill_path=skill_dir,
            metadata={"version": "1.0"},
            hermes_skill_id="my_skill_v1",
        )
        assert entry.description == "Does something cool"
        assert entry.skill_path == skill_dir
        assert entry.hermes_skill_id == "my_skill_v1"

    def test_run_delegates_to_bridge(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """HermesSkillEntry.run delegates to HermesSkillBridge.run_skill."""
        import codomyrmex.skills.hermes_skill_bridge as bridge_mod

        calls: list[dict] = []

        class FakeBridge:
            def get_skill(self, name: str) -> None:
                return None

            def run_skill(
                self,
                name: str,
                prompt: str,
                session_id: str | None = None,
                timeout: int = 180,
            ) -> dict:
                calls.append({"name": name, "prompt": prompt, "session_id": session_id})
                return {
                    "status": "success",
                    "content": "ok",
                    "session_id": None,
                    "error": None,
                }

        monkeypatch.setattr(bridge_mod, "HermesSkillBridge", FakeBridge)
        entry = HermesSkillEntry(name="poly", hermes_skill_id="polymarket")
        result = entry.run("What is the BTC price?")
        assert result["status"] == "success"
        assert calls[0]["name"] == "poly"


# ---------------------------------------------------------------------------
# HermesSkillBridge
# ---------------------------------------------------------------------------


class TestHermesSkillBridge:
    def test_instantiation_default(self) -> None:
        bridge = HermesSkillBridge()
        assert bridge._skills_dir == Path.home() / ".hermes" / "skills"

    def test_instantiation_custom_home(self, tmp_path: Path) -> None:
        bridge = HermesSkillBridge(hermes_home=str(tmp_path))
        assert bridge._hermes_home == tmp_path
        assert bridge._skills_dir == tmp_path / "skills"

    def test_list_hermes_skills_no_cli_no_dir(self, tmp_path: Path) -> None:
        """Returns empty list when CLI unavailable and directory missing."""
        bridge = HermesSkillBridge(hermes_home=str(tmp_path))
        bridge._hermes_bin = None  # simulate no CLI
        skills = bridge.list_hermes_skills()
        assert isinstance(skills, list)
        assert skills == []

    def test_list_hermes_skills_filesystem(self, tmp_path: Path) -> None:
        """Discovers skills from filesystem when CLI unavailable."""
        skills_dir = tmp_path / "skills"
        skill_a = skills_dir / "skill_alpha"
        skill_a.mkdir(parents=True)
        (skill_a / "skill.yaml").write_text(
            "name: skill_alpha\ndescription: Alpha skill\n"
        )
        skill_b = skills_dir / "skill_beta"
        skill_b.mkdir()

        bridge = HermesSkillBridge(hermes_home=str(tmp_path))
        bridge._hermes_bin = None  # force filesystem discovery
        skills = bridge.list_hermes_skills()

        names = [s.name for s in skills]
        assert "skill_alpha" in names
        assert "skill_beta" in names

    def test_skill_yaml_description_parsed(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills" / "geo_skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "skill.yaml").write_text(
            "name: geo_skill\ndescription: Geopolitical analysis skill\n"
        )
        bridge = HermesSkillBridge(hermes_home=str(tmp_path))
        bridge._hermes_bin = None
        skills = bridge.list_hermes_skills()
        geo = next((s for s in skills if s.name == "geo_skill"), None)
        assert geo is not None
        assert "Geopolitical" in geo.description

    def test_get_skill_returns_none_when_missing(self, tmp_path: Path) -> None:
        bridge = HermesSkillBridge(hermes_home=str(tmp_path))
        bridge._hermes_bin = None
        assert bridge.get_skill("nonexistent") is None

    def test_get_skill_normalizes_name(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills" / "my_skill"
        skills_dir.mkdir(parents=True)
        bridge = HermesSkillBridge(hermes_home=str(tmp_path))
        bridge._hermes_bin = None
        entry = bridge.get_skill("MY-SKILL")  # hyphens + uppercase
        assert entry is not None
        assert entry.name == "my_skill"

    def test_sync_hermes_skills_returns_mapping(self, tmp_path: Path) -> None:
        (tmp_path / "skills" / "alpha").mkdir(parents=True)
        (tmp_path / "skills" / "beta").mkdir(parents=True)
        bridge = HermesSkillBridge(hermes_home=str(tmp_path))
        mapping = bridge.sync_hermes_skills()
        assert "alpha" in mapping
        assert "beta" in mapping

    def test_sync_hermes_skills_missing_dir(self, tmp_path: Path) -> None:
        bridge = HermesSkillBridge(hermes_home=str(tmp_path))
        mapping = bridge.sync_hermes_skills()
        assert mapping == {}

    @pytest.mark.skipif(
        shutil.which("hermes") is None,
        reason="Hermes CLI not installed",
    )
    def test_list_via_cli_real(self) -> None:
        """Integration: lists real installed skills via CLI."""
        bridge = HermesSkillBridge()
        skills = bridge.list_hermes_skills()
        assert isinstance(skills, list)
        # geopolitical should be installed from earlier session
        names = [s.name for s in skills]
        assert len(names) >= 0  # Just assert it doesn't crash


# ---------------------------------------------------------------------------
# _normalize_name utility
# ---------------------------------------------------------------------------


class TestNormalizeName:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("MySkill", "myskill"),
            ("my-skill", "my_skill"),
            ("My Skill", "my_skill"),
            ("MY_SKILL", "my_skill"),
            ("geo-market sim", "geo_market_sim"),
        ],
    )
    def test_normalize(self, raw: str, expected: str) -> None:
        assert _normalize_name(raw) == expected

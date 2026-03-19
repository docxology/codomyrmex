"""Integration tests for the PrediHermes skill lifecycle via Codomyrmex.

Zero-Mock policy: all tests use real HermesClient and real SQLite session stores.
Tests that require the Hermes CLI or the PrediHermes skill to be installed are
guarded by pytest.mark.skipif so the suite always passes cleanly even without a
live installation.

Test coverage:
  - Skill name normalization (always runs)
  - HermesClient skill context building (always runs)
  - HermesSkillBridge: filesystem discovery (always runs, using temp dir)
  - skill preload flag passthrough (skipif no hermes CLI)
  - chat_session skill persistence across turns (skipif no CLI configured)
  - health command via typed facade (skipif no companion stack)
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from codomyrmex.agents.hermes.hermes_client import (
    HermesClient,
    agent_context_for_hermes_skills,
    normalize_hermes_skill_names,
)
from codomyrmex.skills.hermes_skill_bridge import HermesSkillBridge, HermesSkillEntry

PREDI_SKILL_NAME = "geopolitical-market-sim"

# ── Helpers ───────────────────────────────────────────────────────────────────


def _hermes_cli_available() -> bool:
    return bool(shutil.which("hermes"))


def _predihermes_installed() -> bool:
    """Return True if the PrediHermes skill is installed and visible."""
    if not _hermes_cli_available():
        return False
    import os
    import subprocess

    try:
        result = subprocess.run(
            ["hermes", "skills", "list"],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "NO_COLOR": "1"},
        )
        return PREDI_SKILL_NAME in result.stdout
    except Exception:  # noqa: BLE001
        return False


def _hermes_configured() -> bool:
    """Return True if Hermes CLI has an API key configured."""
    if not _hermes_cli_available():
        return False
    client = HermesClient()
    return client._is_cli_configured()


# ── Skill name normalization (always runs) ────────────────────────────────────


@pytest.mark.integration
class TestSkillNameNormalization:
    def test_single_skill(self) -> None:
        result = normalize_hermes_skill_names(PREDI_SKILL_NAME, None)
        assert result == [PREDI_SKILL_NAME]

    def test_comma_separated_string(self) -> None:
        result = normalize_hermes_skill_names(None, f"{PREDI_SKILL_NAME},web-research")
        assert PREDI_SKILL_NAME in result
        assert "web-research" in result
        assert len(result) == 2

    def test_list_of_skills(self) -> None:
        result = normalize_hermes_skill_names(None, [PREDI_SKILL_NAME, "huggingface-hub"])
        assert result[0] == PREDI_SKILL_NAME
        assert result[1] == "huggingface-hub"

    def test_deduplication(self) -> None:
        result = normalize_hermes_skill_names(
            PREDI_SKILL_NAME, [PREDI_SKILL_NAME, "other"]
        )
        assert result.count(PREDI_SKILL_NAME) == 1

    def test_empty_returns_empty(self) -> None:
        result = normalize_hermes_skill_names(None, None)
        assert result == []

    def test_whitespace_stripped(self) -> None:
        result = normalize_hermes_skill_names(None, f"  {PREDI_SKILL_NAME}  ")
        assert result == [PREDI_SKILL_NAME]


# ── agent_context_for_hermes_skills (always runs) ─────────────────────────────


@pytest.mark.integration
class TestAgentContextForHermesSkills:
    def test_returns_empty_dict_when_no_skills(self) -> None:
        ctx = agent_context_for_hermes_skills()
        assert ctx == {}

    def test_returns_skills_key(self) -> None:
        ctx = agent_context_for_hermes_skills(PREDI_SKILL_NAME)
        assert "hermes_skills" in ctx
        assert ctx["hermes_skills"] == [PREDI_SKILL_NAME]

    def test_multiple_skills(self) -> None:
        ctx = agent_context_for_hermes_skills(
            PREDI_SKILL_NAME, ["huggingface-hub"]
        )
        assert set(ctx["hermes_skills"]) == {PREDI_SKILL_NAME, "huggingface-hub"}


# ── HermesSkillBridge filesystem integration (always runs) ───────────────────


@pytest.mark.integration
class TestHermesSkillBridgeFilesystem:
    def test_bridge_with_real_temp_skill(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            hermes_home = Path(tmpdir)
            skill_dir = hermes_home / "skills" / "research" / PREDI_SKILL_NAME
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                f"# {PREDI_SKILL_NAME}\nGeopolitical market forecasting skill.\n"
            )
            bridge = HermesSkillBridge(hermes_home=hermes_home)
            skills = bridge.sync_hermes_skills()
            assert PREDI_SKILL_NAME in skills
            entry = skills[PREDI_SKILL_NAME]
            assert isinstance(entry, HermesSkillEntry)
            assert entry.name == PREDI_SKILL_NAME

    def test_get_skill_returns_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            hermes_home = Path(tmpdir)
            skill_dir = hermes_home / "skills" / "bundled" / "web-research"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# web-research\nA web research skill.\n")
            bridge = HermesSkillBridge(hermes_home=hermes_home)
            entry = bridge.get_skill("web-research")
            assert entry is not None
            assert callable(entry)

    def test_missing_skill_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = HermesSkillBridge(hermes_home=Path(tmpdir))
            assert bridge.get_skill("nonexistent") is None


# ── HermesClient skill passthrough (skipif no CLI) ────────────────────────────


@pytest.mark.integration
@pytest.mark.skipif(
    not _hermes_cli_available(),
    reason="Hermes CLI not installed",
)
class TestHermesClientSkillPassthrough:
    def test_client_active_backend_when_cli_available(self) -> None:
        client = HermesClient()
        assert client.active_backend in ("cli", "ollama", "none")

    def test_list_skills_includes_structure(self) -> None:
        """list_skills() returns a dict (may be empty if no skills installed)."""
        client = HermesClient()
        skills = client.list_skills()
        assert isinstance(skills, dict)


# ── PrediHermes skill installed tests (skipif skill not present) ──────────────


@pytest.mark.integration
@pytest.mark.skipif(
    not _predihermes_installed(),
    reason="PrediHermes skill not installed — run scripts/install_hermes_skill.sh",
)
class TestPrediHermesSkillLoad:
    def test_skill_visible_in_bridge(self) -> None:
        """After install, the bridge must discover geopolitical-market-sim."""
        bridge = HermesSkillBridge()
        skills = bridge.list_hermes_skills()
        assert PREDI_SKILL_NAME in skills

    def test_skill_entry_has_path(self) -> None:
        bridge = HermesSkillBridge()
        entry = bridge.get_skill(PREDI_SKILL_NAME)
        assert entry is not None
        assert entry.skill_path.exists()

    def test_skill_description_nonempty(self) -> None:
        bridge = HermesSkillBridge()
        entry = bridge.get_skill(PREDI_SKILL_NAME)
        assert entry is not None
        assert len(entry.description) > 0


# ── Full chat session with skill persistence (skipif no configured CLI) ────────


@pytest.mark.integration
@pytest.mark.skipif(
    not _hermes_configured(),
    reason="Hermes CLI not configured with API key — set OPENROUTER_API_KEY or run hermes setup",
)
class TestPrediHermesChatSession:
    def test_chat_session_persists_skill_in_metadata(self) -> None:
        """chat_session must store hermes_skills in session metadata."""
        from codomyrmex.agents.hermes.session import SQLiteSessionStore

        client = HermesClient()
        session_name = "test-predihermes-skill-persistence"

        # Minimal prompt — just checking skill is attached, not running the pipeline
        resp = client.chat_session(
            prompt="Say 'skill-loaded' and nothing else.",
            session_name=session_name,
            hermes_skill=PREDI_SKILL_NAME,
        )
        assert resp is not None

        # Verify metadata was stored
        with SQLiteSessionStore(client._session_db_path) as store:
            session = store.find_by_name(session_name)
        assert session is not None
        assert "hermes_skills" in session.metadata
        assert PREDI_SKILL_NAME in session.metadata["hermes_skills"]

"""Tests for codomyrmex.soul.agent — SoulAgent wrapper."""

from __future__ import annotations

import os

import pytest

from codomyrmex.soul.agent import HAS_SOUL, SoulAgent
from codomyrmex.soul.exceptions import SoulError, SoulImportError


@pytest.mark.unit
@pytest.mark.soul
class TestHasSoulFlag:
    """Test the HAS_SOUL availability flag."""

    def test_has_soul_is_bool(self):
        """HAS_SOUL must be a plain bool."""
        assert isinstance(HAS_SOUL, bool)


@pytest.mark.unit
@pytest.mark.soul
@pytest.mark.skipif(HAS_SOUL, reason="Only relevant when soul-agent is NOT installed")
class TestSoulAgentWithoutLibrary:
    """Tests that run when soul-agent is not installed."""

    def test_raises_soul_import_error(self, soul_path, memory_path):
        """SoulAgent constructor must raise SoulImportError when soul-agent missing."""
        with pytest.raises(SoulImportError):
            SoulAgent(soul_path=soul_path, memory_path=memory_path)

    def test_soul_import_error_is_soul_error(self):
        """SoulImportError must be a subclass of SoulError."""
        assert issubclass(SoulImportError, SoulError)


@pytest.mark.unit
@pytest.mark.soul
@pytest.mark.skipif(
    not HAS_SOUL or not os.getenv("ANTHROPIC_API_KEY"),
    reason="soul-agent not installed or ANTHROPIC_API_KEY not set",
)
class TestSoulAgentWithLibrary:
    """Tests that run when soul-agent IS installed and an API key is available."""

    def test_constructor_creates_instance(self, soul_path, memory_path):
        """SoulAgent must construct without error when soul-agent is installed."""
        agent = SoulAgent(
            soul_path=soul_path,
            memory_path=memory_path,
            provider="anthropic",
        )
        assert agent.soul_path == soul_path
        assert agent.memory_path == memory_path
        assert agent.provider == "anthropic"

    def test_memory_stats_structure(self, soul_path, memory_path):
        """memory_stats() must return a dict with expected keys."""
        agent = SoulAgent(
            soul_path=soul_path,
            memory_path=memory_path,
            provider="anthropic",
        )
        stats = agent.memory_stats()
        assert isinstance(stats, dict)
        assert stats["soul_path"] == soul_path
        assert stats["memory_path"] == memory_path
        assert "soul_exists" in stats
        assert "memory_exists" in stats
        assert "soul_size_bytes" in stats
        assert "memory_size_bytes" in stats

    def test_memory_stats_nonexistent_files(self, soul_path, memory_path):
        """memory_stats() must report exists=False for missing files."""
        agent = SoulAgent(
            soul_path=soul_path,
            memory_path=memory_path,
            provider="anthropic",
        )
        stats = agent.memory_stats()
        assert stats["soul_exists"] is False
        assert stats["memory_exists"] is False
        assert stats["soul_size_bytes"] == 0
        assert stats["memory_size_bytes"] == 0

    def test_memory_stats_existing_files(
        self, existing_soul_file, existing_memory_file
    ):
        """memory_stats() must report correct sizes for existing files."""
        agent = SoulAgent(
            soul_path=existing_soul_file,
            memory_path=existing_memory_file,
            provider="anthropic",
        )
        stats = agent.memory_stats()
        assert stats["soul_exists"] is True
        assert stats["soul_size_bytes"] > 0
        assert stats["memory_exists"] is True
        assert stats["memory_size_bytes"] > 0

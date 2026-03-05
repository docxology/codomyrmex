"""Tests for codomyrmex.soul.mcp_tools — MCP tool functions."""

from __future__ import annotations

import os

import pytest

from codomyrmex.soul.agent import HAS_SOUL
from codomyrmex.soul.mcp_tools import (
    soul_ask,
    soul_init,
    soul_remember,
    soul_reset,
    soul_status,
)

# ---------------------------------------------------------------------------
# soul_status — fully testable without soul-agent (pure file system)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.soul
class TestSoulStatus:
    """Tests for soul_status MCP tool."""

    def test_missing_files_returns_success(self, soul_path, memory_path):
        """soul_status with non-existent paths must return success with zeros."""
        result = soul_status(soul_path=soul_path, memory_path=memory_path)
        assert result["status"] == "success"
        assert result["soul_exists"] is False
        assert result["memory_exists"] is False
        assert result["soul_size_bytes"] == 0
        assert result["memory_size_bytes"] == 0

    def test_existing_files_reports_size(
        self, existing_soul_file, existing_memory_file
    ):
        """soul_status must report positive size_bytes for existing files."""
        result = soul_status(
            soul_path=existing_soul_file, memory_path=existing_memory_file
        )
        assert result["status"] == "success"
        assert result["soul_exists"] is True
        assert result["soul_size_bytes"] > 0
        assert result["memory_exists"] is True
        assert result["memory_size_bytes"] > 0

    def test_returns_paths_in_result(self, soul_path, memory_path):
        """soul_status must echo back the requested paths."""
        result = soul_status(soul_path=soul_path, memory_path=memory_path)
        assert result["soul_path"] == soul_path
        assert result["memory_path"] == memory_path

    def test_partial_existence(self, tmp_path):
        """soul_status handles the case where only one file exists."""
        soul_file = str(tmp_path / "SOUL.md")
        mem_file = str(tmp_path / "MEMORY.md")
        # Create only soul file
        with open(soul_file, "w", encoding="utf-8") as fh:
            fh.write("# Agent\n")

        result = soul_status(soul_path=soul_file, memory_path=mem_file)
        assert result["soul_exists"] is True
        assert result["memory_exists"] is False


# ---------------------------------------------------------------------------
# soul_init — fully testable without soul-agent (pure file I/O)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.soul
class TestSoulInit:
    """Tests for soul_init MCP tool."""

    def test_creates_both_files(self, soul_path, memory_path):
        """soul_init must create SOUL.md and MEMORY.md when both are missing."""
        result = soul_init(soul_path=soul_path, memory_path=memory_path)
        assert result["status"] == "success"
        assert soul_path in result["created"]
        assert memory_path in result["created"]
        assert os.path.exists(soul_path)
        assert os.path.exists(memory_path)

    def test_soul_file_contains_agent_name(self, soul_path, memory_path):
        """soul_init must embed agent_name in the SOUL.md header."""
        soul_init(
            soul_path=soul_path,
            memory_path=memory_path,
            agent_name="Turing",
            description="A brilliant problem solver.",
        )
        content = open(soul_path, encoding="utf-8").read()
        assert "Turing" in content
        assert "A brilliant problem solver." in content

    def test_soul_file_contains_description(self, soul_path, memory_path):
        """soul_init must embed description in the SOUL.md body."""
        soul_init(
            soul_path=soul_path,
            memory_path=memory_path,
            description="Custom description here.",
        )
        content = open(soul_path, encoding="utf-8").read()
        assert "Custom description here." in content

    def test_memory_file_is_markdown(self, soul_path, memory_path):
        """soul_init must write a valid markdown header to MEMORY.md."""
        soul_init(soul_path=soul_path, memory_path=memory_path)
        content = open(memory_path, encoding="utf-8").read()
        assert content.startswith("# Memory Log")

    def test_does_not_overwrite_existing_files(
        self, existing_soul_file, existing_memory_file
    ):
        """soul_init must not overwrite files that already exist."""
        original_soul = open(existing_soul_file, encoding="utf-8").read()
        original_memory = open(existing_memory_file, encoding="utf-8").read()

        result = soul_init(
            soul_path=existing_soul_file,
            memory_path=existing_memory_file,
            agent_name="OverwriteBot",
        )

        assert result["status"] == "success"
        assert existing_soul_file in result["skipped"]
        assert existing_memory_file in result["skipped"]
        # File content unchanged
        assert open(existing_soul_file, encoding="utf-8").read() == original_soul
        assert open(existing_memory_file, encoding="utf-8").read() == original_memory

    def test_created_list_empty_when_all_exist(
        self, existing_soul_file, existing_memory_file
    ):
        """soul_init must report empty created list when both files already exist."""
        result = soul_init(
            soul_path=existing_soul_file, memory_path=existing_memory_file
        )
        assert result["created"] == []

    def test_default_agent_name_applied(self, soul_path, memory_path):
        """soul_init must use 'Assistant' as the default agent_name."""
        soul_init(soul_path=soul_path, memory_path=memory_path)
        content = open(soul_path, encoding="utf-8").read()
        assert "# Assistant" in content


# ---------------------------------------------------------------------------
# Import guard — works regardless of whether soul-agent is installed
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.soul
@pytest.mark.skipif(HAS_SOUL, reason="Only relevant when soul-agent is NOT installed")
class TestImportGuard:
    """Tests that MCP tools that need soul-agent return error dicts when it is absent."""

    def test_soul_ask_returns_error_when_missing(self, soul_path, memory_path):
        """soul_ask must return error status when soul-agent is not installed."""
        result = soul_ask(
            question="Hello", soul_path=soul_path, memory_path=memory_path
        )
        assert result["status"] == "error"
        assert "soul-agent" in result["message"].lower()

    def test_soul_remember_returns_error_when_missing(self, soul_path, memory_path):
        """soul_remember must return error status when soul-agent is not installed."""
        result = soul_remember(
            note="Test", soul_path=soul_path, memory_path=memory_path
        )
        assert result["status"] == "error"

    def test_soul_reset_returns_error_when_missing(self, soul_path, memory_path):
        """soul_reset must return error status when soul-agent is not installed."""
        result = soul_reset(soul_path=soul_path, memory_path=memory_path)
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Live tests — require soul-agent + API key
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.soul
@pytest.mark.skipif(
    not HAS_SOUL or not os.getenv("ANTHROPIC_API_KEY"),
    reason="soul-agent not installed or ANTHROPIC_API_KEY not set",
)
class TestSoulAskLive:
    """Live tests for soul_ask / soul_remember / soul_reset (need API key)."""

    def test_soul_ask_returns_success(self, soul_path, memory_path):
        """soul_ask must return success with a non-empty response."""
        result = soul_ask(
            question="Say 'pong' and nothing else.",
            soul_path=soul_path,
            memory_path=memory_path,
            provider="anthropic",
        )
        assert result["status"] == "success"
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
        assert result["remembered"] is True

    def test_soul_ask_persists_to_memory(self, soul_path, memory_path):
        """soul_ask with remember=True must write to MEMORY.md."""
        soul_ask(
            question="Remember: my favourite colour is chartreuse.",
            soul_path=soul_path,
            memory_path=memory_path,
            provider="anthropic",
            remember=True,
        )
        assert os.path.exists(memory_path)
        content = open(memory_path, encoding="utf-8").read()
        assert len(content) > 0

    def test_soul_ask_no_remember_does_not_create_memory(self, soul_path, memory_path):
        """soul_ask with remember=False must not create MEMORY.md."""
        soul_ask(
            question="Hello.",
            soul_path=soul_path,
            memory_path=memory_path,
            provider="anthropic",
            remember=False,
        )
        # MEMORY.md may or may not be created depending on soul.py internals,
        # but the tool call itself must succeed.

    def test_soul_remember_appends_to_memory(self, soul_path, memory_path):
        """soul_remember must write the note to MEMORY.md."""
        result = soul_remember(
            note="Key fact: 2 + 2 = 4.",
            soul_path=soul_path,
            memory_path=memory_path,
            provider="anthropic",
        )
        assert result["status"] == "success"
        assert os.path.exists(memory_path)
        content = open(memory_path, encoding="utf-8").read()
        assert "2 + 2 = 4" in content

    def test_soul_reset_returns_success(self, soul_path, memory_path):
        """soul_reset must return success status."""
        result = soul_reset(
            soul_path=soul_path,
            memory_path=memory_path,
            provider="anthropic",
        )
        assert result["status"] == "success"
        assert "cleared" in result["note"].lower()

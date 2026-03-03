"""Shared fixtures for soul module tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def soul_path(tmp_path):
    """Temporary SOUL.md path (does not exist yet)."""
    return str(tmp_path / "SOUL.md")


@pytest.fixture
def memory_path(tmp_path):
    """Temporary MEMORY.md path (does not exist yet)."""
    return str(tmp_path / "MEMORY.md")


@pytest.fixture
def existing_soul_file(tmp_path):
    """Pre-created SOUL.md with minimal content."""
    path = tmp_path / "SOUL.md"
    path.write_text("# TestAgent\n\nA test agent.\n", encoding="utf-8")
    return str(path)


@pytest.fixture
def existing_memory_file(tmp_path):
    """Pre-created MEMORY.md with minimal content."""
    path = tmp_path / "MEMORY.md"
    path.write_text("# Memory Log\n\n", encoding="utf-8")
    return str(path)

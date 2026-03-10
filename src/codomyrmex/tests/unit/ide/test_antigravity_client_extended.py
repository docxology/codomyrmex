"""Extended tests for codomyrmex.ide.antigravity.client.AntigravityClient.

Covers areas NOT already tested in test_antigravity_client.py:
  - TOOLS / ARTIFACT_TYPES ClassVar structure in detail
  - get_active_file() fallback logic with isolated filesystem state
  - Tool count alignment with tool_provider._TOOL_SCHEMAS
  - Immutability / structural expectations of class-level data

Zero-mock compliant — no MagicMock, monkeypatch, or unittest.mock.
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

import pytest

from codomyrmex.ide.antigravity.client import AntigravityClient
from codomyrmex.ide.antigravity.models import Artifact
from codomyrmex.ide.antigravity.tool_provider import AntigravityToolProvider

# ---------------------------------------------------------------------------
# TOOLS ClassVar
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestToolsClassVar:
    """AntigravityClient.TOOLS class-level attribute."""

    def test_tools_is_list(self):
        """TOOLS is a list."""
        assert isinstance(AntigravityClient.TOOLS, list)

    def test_tools_count_is_18(self):
        """TOOLS contains exactly 18 tool names."""
        assert len(AntigravityClient.TOOLS) == 18

    def test_tools_has_view_file(self):
        """TOOLS contains 'view_file'."""
        assert "view_file" in AntigravityClient.TOOLS

    def test_tools_has_run_command(self):
        """TOOLS contains 'run_command'."""
        assert "run_command" in AntigravityClient.TOOLS

    def test_tools_has_task_boundary(self):
        """TOOLS contains 'task_boundary'."""
        assert "task_boundary" in AntigravityClient.TOOLS

    def test_tools_has_notify_user(self):
        """TOOLS contains 'notify_user'."""
        assert "notify_user" in AntigravityClient.TOOLS

    def test_tools_has_grep_search(self):
        """TOOLS contains 'grep_search'."""
        assert "grep_search" in AntigravityClient.TOOLS

    def test_tools_has_write_to_file(self):
        """TOOLS contains 'write_to_file'."""
        assert "write_to_file" in AntigravityClient.TOOLS

    def test_tools_has_generate_image(self):
        """TOOLS contains 'generate_image'."""
        assert "generate_image" in AntigravityClient.TOOLS

    def test_tools_all_strings(self):
        """Every entry in TOOLS is a str."""
        for t in AntigravityClient.TOOLS:
            assert isinstance(t, str)

    def test_tools_no_duplicates(self):
        """TOOLS has no duplicate entries."""
        assert len(AntigravityClient.TOOLS) == len(set(AntigravityClient.TOOLS))

    def test_tools_aligned_with_tool_provider(self):
        """Client TOOLS set matches tool_provider list_all_tools() set."""
        client_set = set(AntigravityClient.TOOLS)
        provider_set = set(AntigravityToolProvider.list_all_tools())
        assert client_set == provider_set


# ---------------------------------------------------------------------------
# ARTIFACT_TYPES ClassVar
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestArtifactTypesClassVar:
    """AntigravityClient.ARTIFACT_TYPES class-level attribute."""

    def test_artifact_types_is_list(self):
        """ARTIFACT_TYPES is a list."""
        assert isinstance(AntigravityClient.ARTIFACT_TYPES, list)

    def test_artifact_types_has_task(self):
        """ARTIFACT_TYPES contains 'task'."""
        assert "task" in AntigravityClient.ARTIFACT_TYPES

    def test_artifact_types_has_implementation_plan(self):
        """ARTIFACT_TYPES contains 'implementation_plan'."""
        assert "implementation_plan" in AntigravityClient.ARTIFACT_TYPES

    def test_artifact_types_has_walkthrough(self):
        """ARTIFACT_TYPES contains 'walkthrough'."""
        assert "walkthrough" in AntigravityClient.ARTIFACT_TYPES

    def test_artifact_types_has_other(self):
        """ARTIFACT_TYPES contains 'other'."""
        assert "other" in AntigravityClient.ARTIFACT_TYPES

    def test_artifact_types_count_is_4(self):
        """ARTIFACT_TYPES has exactly 4 entries."""
        assert len(AntigravityClient.ARTIFACT_TYPES) == 4

    def test_artifact_types_all_strings(self):
        """Every entry in ARTIFACT_TYPES is a str."""
        for t in AntigravityClient.ARTIFACT_TYPES:
            assert isinstance(t, str)


# ---------------------------------------------------------------------------
# get_active_file — fallback logic
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetActiveFileFallback:
    """get_active_file() fallback when no context is set."""

    def test_get_active_file_no_crash_disconnected(self):
        """get_active_file() does not raise when client is disconnected."""
        client = AntigravityClient()
        result = client.get_active_file()
        assert result is None or isinstance(result, str)

    def test_get_active_file_returns_existing_path_when_str(self):
        """If get_active_file() returns a str, that path must exist on disk."""
        client = AntigravityClient()
        result = client.get_active_file()
        if result is not None:
            assert Path(result).exists()

    def test_get_active_file_with_isolated_tmpdir(self):
        """get_active_file with a fresh tmpdir as cwd returns str or None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                client = AntigravityClient()
                result = client.get_active_file()
                # Empty tmpdir has no eligible files — must be None
                assert result is None
            finally:
                os.chdir(original_cwd)

    def test_get_active_file_finds_py_file_in_tmpdir(self):
        """get_active_file returns a .py file if one exists in cwd."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create a .py file — eligible by suffix filter
                py_file = Path(tmpdir) / "sample.py"
                py_file.write_text("x = 1\n")
                client = AntigravityClient()
                result = client.get_active_file()
                assert result is not None
                assert Path(result).resolve() == py_file.resolve()
            finally:
                os.chdir(original_cwd)

    def test_get_active_file_finds_md_file_in_tmpdir(self):
        """get_active_file returns a .md file when it is the only eligible file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                md_file = Path(tmpdir) / "notes.md"
                md_file.write_text("# Notes\n")
                client = AntigravityClient()
                result = client.get_active_file()
                assert result is not None
                assert Path(result).resolve() == md_file.resolve()
            finally:
                os.chdir(original_cwd)

    def test_get_active_file_ignores_hidden_directories(self):
        """get_active_file skips files inside dot-prefixed directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create .hidden/file.py — should be excluded
                hidden_dir = Path(tmpdir) / ".hidden"
                hidden_dir.mkdir()
                (hidden_dir / "secret.py").write_text("pass\n")
                client = AntigravityClient()
                result = client.get_active_file()
                assert result is None
            finally:
                os.chdir(original_cwd)

    def test_get_active_file_ignores_unsupported_extensions(self):
        """get_active_file ignores files with non-eligible extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # .bin file — not in the eligible suffix set
                (Path(tmpdir) / "binary.bin").write_bytes(b"\x00\x01")
                client = AntigravityClient()
                result = client.get_active_file()
                assert result is None
            finally:
                os.chdir(original_cwd)

    def test_get_active_file_picks_most_recently_modified(self):
        """get_active_file picks the most recently modified eligible file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                older = Path(tmpdir) / "older.py"
                older.write_text("older\n")
                time.sleep(0.05)
                newer = Path(tmpdir) / "newer.py"
                newer.write_text("newer\n")

                client = AntigravityClient()
                result = client.get_active_file()
                assert result is not None
                assert Path(result).resolve() == newer.resolve()
            finally:
                os.chdir(original_cwd)

    def test_get_active_file_with_context_artifacts_takes_precedence(self, tmp_path):
        """When context has an artifact with valid path, it takes precedence over cwd scan."""
        conv_dir = tmp_path / "conv1"
        conv_dir.mkdir()
        # Create a real .md file to serve as artifact path
        real_file = tmp_path / "real_source.py"
        real_file.write_text("# real source\n")

        client = AntigravityClient(artifact_dir=str(tmp_path))
        client.connect()

        # Manually inject a fake artifact with a real path via context
        art = Artifact(
            name="real_source",
            path=str(real_file),
            artifact_type="other",
            size=real_file.stat().st_size,
            modified=real_file.stat().st_mtime,
        )
        if client._context is not None:
            client._context.artifacts = [art]
            result = client.get_active_file()
            assert result is not None
            assert Path(result) == real_file

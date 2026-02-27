"""Tests for daily notes CLI commands."""

import shutil

import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.daily_notes import (
    append_daily,
    get_daily_path,
    open_daily,
    prepend_daily,
    read_daily,
)

_CLI_AVAILABLE = shutil.which("obsidian") is not None
skip_no_cli = pytest.mark.skipif(
    not _CLI_AVAILABLE,
    reason="Obsidian CLI not available on PATH",
)


class TestDailyNotesUnavailable:
    """All functions raise ObsidianCLINotAvailable when CLI is missing."""

    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_open_daily(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_daily(self._cli())

    def test_open_daily_with_pane_type(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_daily(self._cli(), pane_type="tab")

    def test_get_daily_path(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_daily_path(self._cli())

    def test_read_daily(self):
        with pytest.raises(ObsidianCLINotAvailable):
            read_daily(self._cli())

    def test_append_daily(self):
        with pytest.raises(ObsidianCLINotAvailable):
            append_daily(self._cli(), "content")

    def test_append_daily_with_flags(self):
        with pytest.raises(ObsidianCLINotAvailable):
            append_daily(
                self._cli(), "content",
                pane_type="split", inline=True, open=True,
            )

    def test_prepend_daily(self):
        with pytest.raises(ObsidianCLINotAvailable):
            prepend_daily(self._cli(), "content")

    def test_prepend_daily_with_flags(self):
        with pytest.raises(ObsidianCLINotAvailable):
            prepend_daily(
                self._cli(), "content",
                pane_type="window", inline=True, open=True,
            )


class TestDailyNotesParameterCombinations:
    """All parameter branches eventually invoke CLI, raising ObsidianCLINotAvailable."""

    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    # open_daily variants (3 tests — covers pane_type branches + vault param)
    def test_open_daily_pane_tab(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_daily(self._cli(), pane_type="tab")

    def test_open_daily_pane_split(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_daily(self._cli(), pane_type="split")

    def test_open_daily_with_vault(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_daily(self._cli(), vault="MyVault")

    # append_daily variants (4 tests — flags combinations)
    def test_append_daily_inline_only(self):
        with pytest.raises(ObsidianCLINotAvailable):
            append_daily(self._cli(), "text", inline=True)

    def test_append_daily_open_only(self):
        with pytest.raises(ObsidianCLINotAvailable):
            append_daily(self._cli(), "text", open=True)

    def test_append_daily_all_flags(self):
        with pytest.raises(ObsidianCLINotAvailable):
            append_daily(self._cli(), "text", inline=True, open=True, pane_type="tab")

    def test_append_daily_with_vault(self):
        with pytest.raises(ObsidianCLINotAvailable):
            append_daily(self._cli(), "content", vault="Personal")

    # prepend_daily variants (3 tests)
    def test_prepend_daily_inline_only(self):
        with pytest.raises(ObsidianCLINotAvailable):
            prepend_daily(self._cli(), "text", inline=True)

    def test_prepend_daily_open_only(self):
        with pytest.raises(ObsidianCLINotAvailable):
            prepend_daily(self._cli(), "text", open=True)

    def test_prepend_daily_with_vault(self):
        with pytest.raises(ObsidianCLINotAvailable):
            prepend_daily(self._cli(), "text", vault="Work")

    # get_daily_path + read_daily vault variants (2 tests)
    def test_get_daily_path_with_vault(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_daily_path(self._cli(), vault="Archive")

    def test_read_daily_with_vault(self):
        with pytest.raises(ObsidianCLINotAvailable):
            read_daily(self._cli(), vault="Archive")

"""Tests for workspace, tab, and recents CLI commands."""

import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.workspace import (
    delete_workspace,
    get_active_workspace,
    list_recents,
    list_tabs,
    list_workspaces,
    load_workspace,
    open_tab,
    save_workspace,
)


class TestWorkspaceUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_get_active_workspace(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_active_workspace(self._cli())

    def test_list_workspaces(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_workspaces(self._cli())

    def test_save_workspace(self):
        with pytest.raises(ObsidianCLINotAvailable):
            save_workspace(self._cli(), "my-layout")

    def test_load_workspace(self):
        with pytest.raises(ObsidianCLINotAvailable):
            load_workspace(self._cli(), "default")

    def test_delete_workspace(self):
        with pytest.raises(ObsidianCLINotAvailable):
            delete_workspace(self._cli(), "old-layout")


class TestTabUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_tabs(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_tabs(self._cli())

    def test_open_tab(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_tab(self._cli(), file="note")


class TestRecentsUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_recents(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_recents(self._cli())


class TestWorkspaceSignatures:
    def test_save_workspace_requires_name(self):
        import inspect
        params = list(inspect.signature(save_workspace).parameters.keys())
        assert "name" in params

    def test_load_workspace_requires_name(self):
        import inspect
        params = list(inspect.signature(load_workspace).parameters.keys())
        assert "name" in params

    def test_delete_workspace_requires_name(self):
        import inspect
        params = list(inspect.signature(delete_workspace).parameters.keys())
        assert "name" in params

"""Tests for CLI search commands."""

import shutil
import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.cli_search import (
    cli_search, cli_search_context, cli_search_open,
)


class TestSearchUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_cli_search(self):
        with pytest.raises(ObsidianCLINotAvailable):
            cli_search(self._cli(), "meeting notes")

    def test_cli_search_all_params(self):
        with pytest.raises(ObsidianCLINotAvailable):
            cli_search(
                self._cli(), "meeting",
                path="folder/", limit=10,
                format="json", total=True, case=True,
            )

    def test_cli_search_context(self):
        with pytest.raises(ObsidianCLINotAvailable):
            cli_search_context(self._cli(), "meeting notes")

    def test_cli_search_context_all_params(self):
        with pytest.raises(ObsidianCLINotAvailable):
            cli_search_context(
                self._cli(), "meeting",
                path="folder/", limit=5, case=True,
            )

    def test_cli_search_open(self):
        with pytest.raises(ObsidianCLINotAvailable):
            cli_search_open(self._cli(), "meeting notes")

    def test_cli_search_open_no_query(self):
        with pytest.raises(ObsidianCLINotAvailable):
            cli_search_open(self._cli())


class TestSearchSignatures:
    def test_cli_search_params(self):
        import inspect
        params = list(inspect.signature(cli_search).parameters.keys())
        assert "query" in params
        assert "path" in params
        assert "limit" in params
        assert "format" in params
        assert "total" in params
        assert "case" in params
        assert "vault" in params

    def test_cli_search_context_params(self):
        import inspect
        params = list(inspect.signature(cli_search_context).parameters.keys())
        assert "query" in params
        assert "path" in params
        assert "limit" in params
        assert "case" in params

    def test_cli_search_open_optional_query(self):
        import inspect
        sig = inspect.signature(cli_search_open)
        # query should have a default of None
        param = sig.parameters["query"]
        assert param.default is None

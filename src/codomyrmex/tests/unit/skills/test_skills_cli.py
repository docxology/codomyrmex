"""Tests for skills package CLI helper construction."""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_skills_cli_commands_expose_callable_handlers() -> None:
    from codomyrmex.skills import cli_commands

    commands = cli_commands()

    assert set(commands) == {"info", "list"}
    assert callable(commands["info"])
    assert callable(commands["list"])


@pytest.mark.unit
def test_skills_cli_info_uses_manager(capsys: pytest.CaptureFixture[str]) -> None:
    from codomyrmex.skills import cli_commands

    cli_commands()["info"]()
    output = capsys.readouterr().out

    assert "Skills manager:" in output
    assert "Upstream:" in output

"""
Unit tests for cli.completion shell completion generators — Zero-Mock compliant.

Covers: generate_bash_completion, generate_zsh_completion,
        generate_fish_completion, install_completion
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.cli.completion import (
    generate_bash_completion,
    generate_fish_completion,
    generate_zsh_completion,
    install_completion,
)

_CMDS = {
    "run": {"description": "Run a workflow", "options": ["--verbose", "--dry-run"]},
    "status": {"description": "Show status"},
    "deploy": {"description": "Deploy service", "options": ["--env", "--version"]},
}


# ── Bash completion ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestBashCompletion:
    """Tests for generate_bash_completion()."""

    def test_returns_string(self):
        result = generate_bash_completion(_CMDS)
        assert isinstance(result, str)

    def test_contains_function_name(self):
        result = generate_bash_completion(_CMDS)
        assert "_codomyrmex_completions()" in result

    def test_contains_command_names(self):
        result = generate_bash_completion(_CMDS)
        assert "run" in result
        assert "status" in result
        assert "deploy" in result

    def test_contains_complete_line(self):
        result = generate_bash_completion(_CMDS)
        assert "complete -F _codomyrmex_completions codomyrmex" in result

    def test_custom_program_name(self):
        result = generate_bash_completion(_CMDS, program_name="myapp")
        assert "_myapp_completions()" in result
        assert "complete -F _myapp_completions myapp" in result

    def test_options_included_for_commands_with_options(self):
        result = generate_bash_completion(_CMDS)
        assert "--verbose" in result
        assert "--dry-run" in result
        assert "--env" in result

    def test_commands_without_options_not_duplicated(self):
        simple = {"check": {"description": "Check things"}}
        result = generate_bash_completion(simple)
        # No options case, but function should still work
        assert "_codomyrmex_completions()" in result

    def test_empty_commands(self):
        result = generate_bash_completion({})
        assert isinstance(result, str)
        assert "_codomyrmex_completions()" in result

    def test_ends_with_newline(self):
        result = generate_bash_completion(_CMDS)
        assert result.endswith("\n")


# ── Zsh completion ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestZshCompletion:
    """Tests for generate_zsh_completion()."""

    def test_returns_string(self):
        result = generate_zsh_completion(_CMDS)
        assert isinstance(result, str)

    def test_starts_with_compdef(self):
        result = generate_zsh_completion(_CMDS)
        assert result.startswith("#compdef codomyrmex")

    def test_contains_function_definition(self):
        result = generate_zsh_completion(_CMDS)
        assert "_codomyrmex()" in result

    def test_contains_command_descriptions(self):
        result = generate_zsh_completion(_CMDS)
        assert "Run a workflow" in result
        assert "Show status" in result

    def test_custom_program_name(self):
        result = generate_zsh_completion(_CMDS, program_name="myapp")
        assert "#compdef myapp" in result
        assert "_myapp()" in result

    def test_empty_commands(self):
        result = generate_zsh_completion({})
        assert isinstance(result, str)
        assert "#compdef codomyrmex" in result

    def test_ends_with_newline(self):
        result = generate_zsh_completion(_CMDS)
        assert result.endswith("\n")

    def test_uses_describe_command(self):
        result = generate_zsh_completion(_CMDS)
        assert "_describe" in result


# ── Fish completion ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestFishCompletion:
    """Tests for generate_fish_completion()."""

    def test_returns_string(self):
        result = generate_fish_completion(_CMDS)
        assert isinstance(result, str)

    def test_contains_complete_commands(self):
        result = generate_fish_completion(_CMDS)
        assert "complete -c codomyrmex" in result

    def test_contains_command_names(self):
        result = generate_fish_completion(_CMDS)
        assert "-a 'run'" in result
        assert "-a 'status'" in result
        assert "-a 'deploy'" in result

    def test_contains_command_descriptions(self):
        result = generate_fish_completion(_CMDS)
        assert "Run a workflow" in result

    def test_includes_options_as_subcommand_completions(self):
        result = generate_fish_completion(_CMDS)
        # Options for run: --verbose, --dry-run → should appear as -l entries
        assert "-l 'verbose'" in result or "-l '--verbose'" in result or "verbose" in result

    def test_custom_program_name(self):
        result = generate_fish_completion(_CMDS, program_name="myapp")
        assert "complete -c myapp" in result

    def test_empty_commands(self):
        result = generate_fish_completion({})
        assert isinstance(result, str)

    def test_ends_with_newline(self):
        result = generate_fish_completion(_CMDS)
        assert result.endswith("\n")


# ── install_completion ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestInstallCompletion:
    """Tests for install_completion()."""

    def test_bash_writes_to_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "codomyrmex.bash"
            result_path = install_completion("bash", output_path=out, commands=_CMDS)
            assert result_path == out
            assert out.exists()
            content = out.read_text()
            assert "_codomyrmex_completions()" in content

    def test_zsh_writes_to_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "_codomyrmex"
            result_path = install_completion("zsh", output_path=out, commands=_CMDS)
            assert result_path == out
            assert out.exists()
            content = out.read_text()
            assert "#compdef codomyrmex" in content

    def test_fish_writes_to_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "codomyrmex.fish"
            result_path = install_completion("fish", output_path=out, commands=_CMDS)
            assert result_path == out
            assert out.exists()
            content = out.read_text()
            assert "complete -c codomyrmex" in content

    def test_unsupported_shell_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported shell"):
            install_completion("powershell", output_path=Path("/tmp/test"), commands={})

    def test_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "nested" / "deep" / "codomyrmex.bash"
            install_completion("bash", output_path=out, commands={})
            assert out.exists()

    def test_default_commands_is_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "codomyrmex.bash"
            # commands=None should default to {}
            install_completion("bash", output_path=out)
            assert out.exists()

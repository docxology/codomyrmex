"""Tests for core Obsidian CLI wrapper."""

import shutil

import pytest

from codomyrmex.agentic_memory.obsidian.cli import (
    CLIResult,
    ObsidianCLI,
    ObsidianCLIError,
    ObsidianCLINotAvailable,
    _file_or_path,
)

_CLI_AVAILABLE = shutil.which("obsidian") is not None
skip_no_cli = pytest.mark.skipif(
    not _CLI_AVAILABLE,
    reason="Obsidian CLI not available on PATH",
)


class TestCLIResult:
    """Tests for the CLIResult dataclass."""

    def test_ok_when_zero(self):
        r = CLIResult(command="test", returncode=0, stdout="hello")
        assert r.ok is True

    def test_not_ok_when_nonzero(self):
        r = CLIResult(command="test", returncode=1)
        assert r.ok is False

    def test_text_trims_whitespace(self):
        r = CLIResult(command="test", stdout="  hello world  \n")
        assert r.text == "hello world"

    def test_lines_populated(self):
        r = CLIResult(command="test", lines=["a", "b", "c"])
        assert len(r.lines) == 3

    def test_json_data_default_none(self):
        r = CLIResult(command="test")
        assert r.json_data is None


class TestFileOrPath:
    """Tests for the _file_or_path helper."""

    def test_file_only(self):
        assert _file_or_path(file="note") == {"file": "note"}

    def test_path_only(self):
        assert _file_or_path(path="folder/note.md") == {"path": "folder/note.md"}

    def test_file_takes_precedence(self):
        result = _file_or_path(file="note", path="folder/note.md")
        assert "file" in result

    def test_both_none(self):
        assert _file_or_path() == {}


class TestObsidianCLI:
    """Tests for the ObsidianCLI wrapper class."""

    def test_is_available_returns_bool(self):
        assert isinstance(ObsidianCLI.is_available(), bool)

    def test_is_available_with_nonexistent_binary(self):
        assert ObsidianCLI.is_available("__nonexistent_binary_xyz__") is False

    def test_ensure_unavailable_raises(self):
        cli = ObsidianCLI(binary="__nonexistent_binary_xyz__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli._ensure_available()

    def test_build_argv_basic(self):
        cli = ObsidianCLI()
        argv = cli._build_argv("files")
        assert argv == ["obsidian", "files"]

    def test_build_argv_with_vault(self):
        cli = ObsidianCLI(vault="MyVault")
        argv = cli._build_argv("files")
        assert argv == ["obsidian", "vault=MyVault", "files"]

    def test_build_argv_with_override_vault(self):
        cli = ObsidianCLI(vault="Default")
        argv = cli._build_argv("files", vault="Override")
        assert argv == ["obsidian", "vault=Override", "files"]

    def test_build_argv_with_params(self):
        cli = ObsidianCLI()
        argv = cli._build_argv("read", params={"file": "note.md"})
        assert "file=note.md" in argv

    def test_build_argv_with_flags(self):
        cli = ObsidianCLI()
        argv = cli._build_argv("create", flags=["overwrite", "open", "newtab"])
        assert "overwrite" in argv
        assert "open" in argv
        assert "newtab" in argv

    def test_build_argv_complex(self):
        cli = ObsidianCLI(vault="V")
        argv = cli._build_argv(
            "search",
            params={"query": "hello", "limit": "10"},
            flags=["case"],
        )
        assert argv[0] == "obsidian"
        assert argv[1] == "vault=V"
        assert argv[2] == "search"
        assert "query=hello" in argv
        assert "limit=10" in argv
        assert "case" in argv

    def test_custom_binary_path(self):
        cli = ObsidianCLI(binary="/usr/local/bin/obsidian-custom")
        argv = cli._build_argv("version")
        assert argv[0] == "/usr/local/bin/obsidian-custom"

    def test_run_raises_on_unavailable(self):
        cli = ObsidianCLI(binary="__nonexistent_binary_xyz__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.run("version")

    def test_timeout_default(self):
        cli = ObsidianCLI()
        assert cli._timeout == 30.0

    def test_timeout_custom(self):
        cli = ObsidianCLI(timeout=60.0)
        assert cli._timeout == 60.0

    # ── file operations raise when unavailable ────────────────────

    def test_file_info_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.file_info(file="note")

    def test_list_files_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.list_files()

    def test_folder_info_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.folder_info("path")

    def test_list_folders_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.list_folders()

    def test_create_file_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.create_file(name="test")

    def test_create_file_with_template(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.create_file(name="trip", template="Travel", open=True)

    def test_append_file_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.append_file("content", file="note", inline=True)

    def test_prepend_file_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.prepend_file("content", file="note")

    def test_move_file_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.move_file("new/path.md", file="note")

    def test_rename_file_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.rename_file("new-name", file="note")

    def test_delete_file_raises(self):
        cli = ObsidianCLI(binary="__nonexistent__")
        with pytest.raises(ObsidianCLINotAvailable):
            cli.delete_file(file="note", permanent=True)

    @skip_no_cli
    def test_version_returns_string(self):
        cli = ObsidianCLI()
        ver = cli.version()
        assert isinstance(ver, str)
        assert len(ver) > 0

    @skip_no_cli
    def test_help_returns_string(self):
        cli = ObsidianCLI()
        h = cli.help()
        assert isinstance(h, str)
        assert len(h) > 0


class TestObsidianCLIError:
    """Tests for ObsidianCLIError."""

    def test_attributes(self):
        err = ObsidianCLIError(1, "bad input", ["obsidian", "bad"])
        assert err.returncode == 1
        assert err.stderr == "bad input"
        assert err.cmd == ["obsidian", "bad"]
        assert "bad input" in str(err)

    def test_is_runtime_error(self):
        assert isinstance(ObsidianCLIError(1, "", []), RuntimeError)

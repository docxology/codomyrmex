"""Zero-mock tests for coding.sandbox security and file preparation.

Covers: prepare_code_file, prepare_stdin_file, cleanup_temp_files,
DEFAULT_DOCKER_ARGS structure.

All file I/O uses real temp directories via tmp_path fixture.
No mocks. No MagicMock. No monkeypatch.
"""
from __future__ import annotations

import os
import tempfile

import pytest

from codomyrmex.coding.sandbox.resource_limits import DEFAULT_DOCKER_ARGS
from codomyrmex.coding.sandbox.security import (
    cleanup_temp_files,
    prepare_code_file,
    prepare_stdin_file,
)


@pytest.mark.unit
class TestPrepareCodeFile:
    """Tests for prepare_code_file — writes code to real temp files."""

    def test_returns_tuple_of_two_strings(self):
        """prepare_code_file returns (temp_dir, rel_path) both as strings."""
        temp_dir, rel_path = prepare_code_file("print('hello')", "python")
        try:
            assert isinstance(temp_dir, str)
            assert isinstance(rel_path, str)
        finally:
            cleanup_temp_files(temp_dir)

    def test_python_extension_is_py(self):
        """Python code files get .py extension."""
        temp_dir, rel_path = prepare_code_file("x = 1", "python")
        try:
            assert rel_path.endswith(".py")
        finally:
            cleanup_temp_files(temp_dir)

    def test_javascript_extension_is_js(self):
        """JavaScript code files get .js extension."""
        temp_dir, rel_path = prepare_code_file("console.log('hi')", "javascript")
        try:
            assert rel_path.endswith(".js")
        finally:
            cleanup_temp_files(temp_dir)

    def test_bash_extension_is_sh(self):
        """Bash code files get .sh extension."""
        temp_dir, rel_path = prepare_code_file("echo hello", "bash")
        try:
            assert rel_path.endswith(".sh")
        finally:
            cleanup_temp_files(temp_dir)

    def test_cpp_extension_is_cpp(self):
        """C++ code files get .cpp extension."""
        temp_dir, rel_path = prepare_code_file('#include <iostream>', "cpp")
        try:
            assert rel_path.endswith(".cpp")
        finally:
            cleanup_temp_files(temp_dir)

    def test_file_exists_on_disk(self):
        """The created code file actually exists on disk."""
        temp_dir, rel_path = prepare_code_file("print(42)", "python")
        try:
            abs_path = os.path.join(temp_dir, rel_path)
            assert os.path.isfile(abs_path)
        finally:
            cleanup_temp_files(temp_dir)

    def test_file_contains_exact_code(self):
        """The created file contains the exact code string passed in."""
        code = "def foo():\n    return 42\n"
        temp_dir, rel_path = prepare_code_file(code, "python")
        try:
            abs_path = os.path.join(temp_dir, rel_path)
            with open(abs_path) as f:
                contents = f.read()
            assert contents == code
        finally:
            cleanup_temp_files(temp_dir)

    def test_temp_dir_prefix_contains_codomyrmex(self):
        """Temp directory name contains project prefix for identification."""
        temp_dir, _ = prepare_code_file("x=1", "python")
        try:
            basename = os.path.basename(temp_dir)
            assert "codomyrmex" in basename
        finally:
            cleanup_temp_files(temp_dir)

    def test_unicode_code_written_correctly(self):
        """Unicode characters in code are preserved faithfully."""
        code = '# -*- coding: utf-8 -*-\nprint("héllo wörld")\n'
        temp_dir, rel_path = prepare_code_file(code, "python")
        try:
            abs_path = os.path.join(temp_dir, rel_path)
            with open(abs_path, encoding="utf-8") as f:
                contents = f.read()
            assert contents == code
        finally:
            cleanup_temp_files(temp_dir)

    def test_empty_code_creates_empty_file(self):
        """Empty code string creates an empty file."""
        temp_dir, rel_path = prepare_code_file("", "python")
        try:
            abs_path = os.path.join(temp_dir, rel_path)
            assert os.path.getsize(abs_path) == 0
        finally:
            cleanup_temp_files(temp_dir)

    def test_multiple_calls_produce_separate_dirs(self):
        """Two calls to prepare_code_file produce separate temp directories."""
        temp_dir1, _ = prepare_code_file("x=1", "python")
        temp_dir2, _ = prepare_code_file("x=2", "python")
        try:
            assert temp_dir1 != temp_dir2
        finally:
            cleanup_temp_files(temp_dir1)
            cleanup_temp_files(temp_dir2)

    def test_go_extension_is_go(self):
        """Go code files get .go extension."""
        temp_dir, rel_path = prepare_code_file("package main", "go")
        try:
            assert rel_path.endswith(".go")
        finally:
            cleanup_temp_files(temp_dir)

    def test_rust_extension_is_rs(self):
        """Rust code files get .rs extension."""
        temp_dir, rel_path = prepare_code_file("fn main() {}", "rust")
        try:
            assert rel_path.endswith(".rs")
        finally:
            cleanup_temp_files(temp_dir)


@pytest.mark.unit
class TestPrepareStdinFile:
    """Tests for prepare_stdin_file — creates stdin file when needed."""

    def test_none_stdin_returns_none(self):
        """None stdin input returns None (no file created)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = prepare_stdin_file(None, temp_dir)
            assert result is None

    def test_empty_string_stdin_returns_none(self):
        """Empty string stdin returns None (no file created)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = prepare_stdin_file("", temp_dir)
            assert result is None

    def test_nonempty_stdin_returns_file_path(self):
        """Non-empty stdin returns a path to the stdin file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = prepare_stdin_file("hello\nworld\n", temp_dir)
            assert result is not None
            assert isinstance(result, str)

    def test_stdin_file_exists_on_disk(self):
        """The stdin file actually exists on disk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = prepare_stdin_file("test input", temp_dir)
            assert os.path.isfile(result)

    def test_stdin_file_contains_correct_content(self):
        """The stdin file contains the exact stdin string."""
        stdin_content = "line1\nline2\nline3\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            result = prepare_stdin_file(stdin_content, temp_dir)
            with open(result) as f:
                contents = f.read()
            assert contents == stdin_content

    def test_stdin_file_is_named_stdin_txt(self):
        """Stdin file is named 'stdin.txt'."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = prepare_stdin_file("data", temp_dir)
            assert os.path.basename(result) == "stdin.txt"

    def test_stdin_file_in_temp_dir(self):
        """Stdin file is located inside the provided temp directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = prepare_stdin_file("data", temp_dir)
            assert result.startswith(temp_dir)

    def test_stdin_with_only_whitespace_creates_file(self):
        """Whitespace-only stdin (non-empty) creates a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = prepare_stdin_file("   \n   ", temp_dir)
            assert result is not None


@pytest.mark.unit
class TestCleanupTempFiles:
    """Tests for cleanup_temp_files — removes temp directories."""

    def test_removes_existing_directory(self):
        """cleanup_temp_files removes an existing temp directory."""
        temp_dir = tempfile.mkdtemp()
        assert os.path.isdir(temp_dir)
        cleanup_temp_files(temp_dir)
        assert not os.path.exists(temp_dir)

    def test_removes_directory_with_files(self):
        """cleanup_temp_files removes a directory that contains files."""
        temp_dir = tempfile.mkdtemp()
        # Create a file inside
        file_path = os.path.join(temp_dir, "code.py")
        with open(file_path, "w") as f:
            f.write("x = 1")
        assert os.path.isfile(file_path)
        cleanup_temp_files(temp_dir)
        assert not os.path.exists(temp_dir)

    def test_nonexistent_directory_does_not_raise(self):
        """cleanup_temp_files on a non-existent path doesn't raise."""
        nonexistent = "/tmp/codomyrmex_test_nonexistent_" + "x" * 20
        # Should not raise any exception
        cleanup_temp_files(nonexistent)

    def test_cleanup_after_prepare_code_file(self):
        """After prepare_code_file + cleanup, temp dir is gone."""
        temp_dir, rel_path = prepare_code_file("print('hi')", "python")
        abs_path = os.path.join(temp_dir, rel_path)
        assert os.path.isfile(abs_path)
        cleanup_temp_files(temp_dir)
        assert not os.path.exists(temp_dir)
        assert not os.path.exists(abs_path)


@pytest.mark.unit
class TestDefaultDockerArgs:
    """Tests for DEFAULT_DOCKER_ARGS security configuration."""

    def test_is_a_list(self):
        """DEFAULT_DOCKER_ARGS is a list."""
        assert isinstance(DEFAULT_DOCKER_ARGS, list)

    def test_has_at_least_five_args(self):
        """At minimum 5 security arguments are configured."""
        assert len(DEFAULT_DOCKER_ARGS) >= 5

    def test_no_network_access(self):
        """Container has no network access (--network=none)."""
        assert "--network=none" in DEFAULT_DOCKER_ARGS

    def test_all_capabilities_dropped(self):
        """All capabilities are dropped (--cap-drop=ALL)."""
        assert "--cap-drop=ALL" in DEFAULT_DOCKER_ARGS

    def test_no_new_privileges(self):
        """Privilege escalation is disabled."""
        assert "--security-opt=no-new-privileges" in DEFAULT_DOCKER_ARGS

    def test_memory_limit_present(self):
        """Memory limit argument is present."""
        has_memory_limit = any("--memory=" in arg for arg in DEFAULT_DOCKER_ARGS)
        assert has_memory_limit

    def test_cpu_limit_present(self):
        """CPU limit argument is present."""
        has_cpu_limit = any("--cpus=" in arg for arg in DEFAULT_DOCKER_ARGS)
        assert has_cpu_limit

    def test_pids_limit_present(self):
        """Process ID limit is present to prevent fork bombs."""
        has_pids_limit = any("--pids-limit=" in arg for arg in DEFAULT_DOCKER_ARGS)
        assert has_pids_limit

    def test_all_args_are_strings(self):
        """All Docker arguments are strings."""
        for arg in DEFAULT_DOCKER_ARGS:
            assert isinstance(arg, str), f"Non-string arg: {arg!r}"

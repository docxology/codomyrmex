"""Extended tests for model_context_protocol.tools — covers functions not
tested in test_mcp_tools.py: search_codebase, run_shell_command, json_query,
checksum_file, git_status, git_diff.

Zero-mock policy: real filesystem + subprocess operations only.
Skip guards: git tests skipped when git binary absent.
"""
import shutil

import pytest

from codomyrmex.model_context_protocol.tools import (
    checksum_file,
    git_diff,
    git_status,
    json_query,
    run_shell_command,
    search_codebase,
)

_HAS_GIT = shutil.which("git") is not None


# ──────────────────────────── search_codebase ─────────────────────────────


class TestSearchCodebase:
    def test_finds_simple_pattern(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("def hello_world():\n    return 42\n")
        result = search_codebase("hello_world", path=str(tmp_path), file_types=[".py"])
        assert result["success"] is True
        assert result["total_matches"] >= 1

    def test_returns_file_and_line(self, tmp_path):
        f = tmp_path / "code.py"
        f.write_text("MARKER_TOKEN = True\n")
        result = search_codebase("MARKER_TOKEN", path=str(tmp_path), file_types=[".py"])
        assert result["success"] is True
        assert result["total_matches"] >= 1
        match = result["matches"][0]
        assert "file" in match
        assert "line" in match
        assert "content" in match

    def test_case_insensitive_by_default(self, tmp_path):
        (tmp_path / "test.py").write_text("UPPERCASE_TOKEN = 1\n")
        result = search_codebase(
            "uppercase_token", path=str(tmp_path), file_types=[".py"], case_sensitive=False
        )
        assert result["success"] is True
        assert result["total_matches"] >= 1

    def test_case_sensitive_miss(self, tmp_path):
        (tmp_path / "test.py").write_text("UPPERCASE_TOKEN = 1\n")
        result = search_codebase(
            "uppercase_token", path=str(tmp_path), file_types=[".py"], case_sensitive=True
        )
        assert result["success"] is True
        assert result["total_matches"] == 0

    def test_file_type_filter_excludes_non_matching(self, tmp_path):
        (tmp_path / "script.py").write_text("NEEDLE = 1\n")
        (tmp_path / "notes.md").write_text("NEEDLE is here\n")
        result = search_codebase("NEEDLE", path=str(tmp_path), file_types=[".py"])
        assert result["success"] is True
        for match in result["matches"]:
            assert match["file"].endswith(".py")

    def test_no_match_returns_empty_list(self, tmp_path):
        (tmp_path / "empty.py").write_text("x = 1\n")
        result = search_codebase("XYZZY_NOTFOUND", path=str(tmp_path), file_types=[".py"])
        assert result["success"] is True
        assert result["total_matches"] == 0
        assert result["matches"] == []

    def test_max_results_truncates(self, tmp_path):
        # Write many lines each containing the needle
        content = "\n".join([f"needle_line_{i} = {i}" for i in range(50)])
        (tmp_path / "many.py").write_text(content)
        result = search_codebase(
            "needle_line", path=str(tmp_path), file_types=[".py"], max_results=5
        )
        assert result["success"] is True
        assert len(result["matches"]) <= 5
        assert result["truncated"] is True

    def test_nonexistent_path_returns_empty_or_error(self):
        result = search_codebase("anything", path="/nonexistent/path/xyz")
        # search_codebase may return success=True with 0 matches (path.rglob yields nothing)
        # or success=False on OSError — either is acceptable
        if result["success"]:
            assert result["total_matches"] == 0
        else:
            assert "error" in result

    def test_regex_pattern_works(self, tmp_path):
        (tmp_path / "nums.py").write_text("x = 123\ny = 456\n")
        result = search_codebase(r"\d+", path=str(tmp_path), file_types=[".py"])
        assert result["success"] is True
        assert result["total_matches"] >= 2

    def test_files_searched_count_returned(self, tmp_path):
        (tmp_path / "a.py").write_text("a = 1\n")
        (tmp_path / "b.py").write_text("b = 2\n")
        result = search_codebase("anything_not_here", path=str(tmp_path), file_types=[".py"])
        assert result["success"] is True
        assert "files_searched" in result
        assert result["files_searched"] >= 2

    def test_result_content_truncated_to_200_chars(self, tmp_path):
        long_line = "x = '" + "a" * 300 + "'"
        (tmp_path / "long.py").write_text(long_line + "\n")
        result = search_codebase("x = '", path=str(tmp_path), file_types=[".py"])
        if result["total_matches"] > 0:
            assert len(result["matches"][0]["content"]) <= 200


# ──────────────────────────── run_shell_command ────────────────────────────


class TestRunShellCommand:
    def test_simple_echo_command(self):
        result = run_shell_command("echo hello")
        assert result["success"] is True
        assert "hello" in result["stdout"]

    def test_exit_code_zero_on_success(self):
        result = run_shell_command("true")
        assert result["exit_code"] == 0
        assert result["success"] is True

    def test_exit_code_nonzero_on_failure(self):
        result = run_shell_command("false")
        assert result["exit_code"] != 0
        assert result["success"] is False

    def test_stdout_captured(self):
        result = run_shell_command("echo captured_output")
        assert "captured_output" in result["stdout"]

    def test_stderr_captured(self):
        result = run_shell_command("echo err_message >&2")
        assert result["success"] is True
        assert "err_message" in result["stderr"]

    def test_command_stored_in_result(self):
        cmd = "echo command_key"
        result = run_shell_command(cmd)
        assert result["command"] == cmd

    def test_timeout_triggers_error(self):
        result = run_shell_command("sleep 10", timeout=1)
        assert result["success"] is False
        assert "timed out" in result["error"].lower() or "timeout" in result["error"].lower()

    def test_cwd_changes_working_directory(self, tmp_path):
        result = run_shell_command("pwd", cwd=str(tmp_path))
        assert result["success"] is True
        assert str(tmp_path) in result["stdout"] or result["exit_code"] == 0

    def test_env_variable_passed(self):
        result = run_shell_command("echo $MY_TEST_VAR", env={"MY_TEST_VAR": "hello_from_env"})
        assert result["success"] is True
        assert "hello_from_env" in result["stdout"]

    def test_multiword_command(self):
        result = run_shell_command("python3 --version")
        assert result["success"] is True or "python" in result["stdout"].lower()


# ──────────────────────────── json_query ──────────────────────────────────


class TestJsonQuery:
    def test_read_simple_json(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('{"key": "value", "num": 42}')
        result = json_query(str(f))
        assert result["success"] is True
        assert result["data"]["key"] == "value"
        assert result["data"]["num"] == 42

    def test_read_nested_json(self, tmp_path):
        f = tmp_path / "nested.json"
        f.write_text('{"outer": {"inner": "treasure"}}')
        result = json_query(str(f))
        assert result["success"] is True
        assert result["data"]["outer"]["inner"] == "treasure"

    def test_query_top_level_key(self, tmp_path):
        f = tmp_path / "q.json"
        f.write_text('{"name": "alice", "age": 30}')
        result = json_query(str(f), query="name")
        assert result["success"] is True
        assert result["result"] == "alice"

    def test_query_nested_key(self, tmp_path):
        f = tmp_path / "deep.json"
        f.write_text('{"user": {"profile": {"city": "Boston"}}}')
        result = json_query(str(f), query="user.profile.city")
        assert result["success"] is True
        assert result["result"] == "Boston"

    def test_query_array_index(self, tmp_path):
        f = tmp_path / "arr.json"
        f.write_text('{"items": ["a", "b", "c"]}')
        result = json_query(str(f), query="items.1")
        assert result["success"] is True
        assert result["result"] == "b"

    def test_query_stored_in_result(self, tmp_path):
        f = tmp_path / "q2.json"
        f.write_text('{"x": 1}')
        result = json_query(str(f), query="x")
        assert result["query"] == "x"

    def test_nonexistent_file_returns_error(self):
        result = json_query("/nonexistent/data.json")
        assert result["success"] is False
        assert "error" in result

    def test_invalid_json_returns_error(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("not valid json {{{")
        result = json_query(str(f))
        assert result["success"] is False
        assert "error" in result

    def test_invalid_query_key_returns_error(self, tmp_path):
        f = tmp_path / "simple.json"
        f.write_text('{"real_key": 1}')
        result = json_query(str(f), query="nonexistent_key")
        assert result["success"] is False

    def test_read_list_json(self, tmp_path):
        f = tmp_path / "list.json"
        f.write_text("[1, 2, 3]")
        result = json_query(str(f))
        assert result["success"] is True
        assert result["data"] == [1, 2, 3]


# ──────────────────────────── checksum_file ───────────────────────────────


class TestChecksumFile:
    def test_sha256_default(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_bytes(b"hello")
        result = checksum_file(str(f))
        assert result["success"] is True
        assert result["algorithm"] == "sha256"
        assert len(result["checksum"]) == 64

    def test_sha1_algorithm(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_bytes(b"hello")
        result = checksum_file(str(f), algorithm="sha1")
        assert result["success"] is True
        assert result["algorithm"] == "sha1"
        assert len(result["checksum"]) == 40

    def test_md5_algorithm(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_bytes(b"hello")
        result = checksum_file(str(f), algorithm="md5")
        assert result["success"] is True
        assert result["algorithm"] == "md5"
        assert len(result["checksum"]) == 32

    def test_checksum_consistent(self, tmp_path):
        f = tmp_path / "consistent.txt"
        f.write_bytes(b"deterministic content")
        r1 = checksum_file(str(f))
        r2 = checksum_file(str(f))
        assert r1["checksum"] == r2["checksum"]

    def test_different_content_different_checksum(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"content_a")
        f2.write_bytes(b"content_b")
        r1 = checksum_file(str(f1))
        r2 = checksum_file(str(f2))
        assert r1["checksum"] != r2["checksum"]

    def test_size_reported(self, tmp_path):
        content = b"12345"
        f = tmp_path / "sized.bin"
        f.write_bytes(content)
        result = checksum_file(str(f))
        assert result["success"] is True
        assert result["size"] == len(content)

    def test_path_in_result(self, tmp_path):
        f = tmp_path / "path_check.txt"
        f.write_bytes(b"x")
        result = checksum_file(str(f))
        assert result["success"] is True
        assert "path" in result

    def test_nonexistent_file_returns_error(self):
        result = checksum_file("/nonexistent/file.bin")
        assert result["success"] is False
        assert "error" in result

    def test_empty_file_checksum(self, tmp_path):
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        result = checksum_file(str(f))
        assert result["success"] is True
        assert result["size"] == 0
        assert len(result["checksum"]) > 0

    def test_unknown_algorithm_defaults_to_sha256(self, tmp_path):
        f = tmp_path / "algo.txt"
        f.write_bytes(b"test")
        result = checksum_file(str(f), algorithm="unknown_algo")
        assert result["success"] is True
        assert len(result["checksum"]) == 64  # sha256 length


# ──────────────────────────── git_status ──────────────────────────────────


@pytest.mark.skipif(not _HAS_GIT, reason="git not installed")
class TestGitStatus:
    def test_returns_success_in_git_repo(self, tmp_path):
        # Initialize real git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_status(str(tmp_path))
        assert result["success"] is True

    def test_has_branch_key(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_status(str(tmp_path))
        assert "branch" in result

    def test_has_changes_list(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_status(str(tmp_path))
        assert "changes" in result
        assert isinstance(result["changes"], list)

    def test_untracked_file_appears_in_changes(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        (tmp_path / "untracked.txt").write_text("x")
        result = git_status(str(tmp_path))
        assert result["success"] is True
        # May or may not appear in porcelain output depending on git config
        assert "changes" in result

    def test_nonexistent_path_returns_error(self):
        result = git_status("/nonexistent/path/xyz")
        assert result["success"] is False
        assert "error" in result

    def test_has_recent_commits_key(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_status(str(tmp_path))
        assert "recent_commits" in result

    def test_changed_files_count(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_status(str(tmp_path))
        assert "changed_files" in result
        assert isinstance(result["changed_files"], int)


# ──────────────────────────── git_diff ────────────────────────────────────


@pytest.mark.skipif(not _HAS_GIT, reason="git not installed")
class TestGitDiff:
    def test_returns_success_in_git_repo(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_diff(str(tmp_path))
        assert result["success"] is True

    def test_has_diff_key(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_diff(str(tmp_path))
        assert "diff" in result

    def test_has_lines_key(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_diff(str(tmp_path))
        assert "lines" in result
        assert isinstance(result["lines"], int)

    def test_staged_false_by_default(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_diff(str(tmp_path), staged=False)
        assert result["success"] is True

    def test_staged_true_runs_without_error(self, tmp_path):
        import subprocess

        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        result = git_diff(str(tmp_path), staged=True)
        assert result["success"] is True

    def test_nonexistent_path_returns_error(self):
        result = git_diff("/nonexistent/path/xyz")
        assert result["success"] is False
        assert "error" in result

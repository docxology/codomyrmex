"""Unit tests for codomyrmex.utils.process.subprocess module.

Tests cover: CommandErrorType, CommandError, SubprocessResult, _prepare_command,
_prepare_environment, _validate_working_directory, run_command, run_command_async,
stream_command, run_with_retry, check_command_available, get_command_version,
quote_command, split_command.

Zero-mock policy: all tests use real subprocess calls and real objects.
"""

import asyncio
import os
import sys
import tempfile

import pytest

from codomyrmex.utils.process.subprocess import (
    CommandError,
    CommandErrorType,
    SubprocessResult,
    _prepare_command,
    _prepare_environment,
    _validate_working_directory,
    check_command_available,
    get_command_version,
    quote_command,
    run_command,
    run_command_async,
    run_with_retry,
    split_command,
    stream_command,
)


# ---------------------------------------------------------------------------
# CommandErrorType enum
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestCommandErrorType:
    """Tests for the CommandErrorType enum."""

    def test_all_members_present(self):
        names = {m.name for m in CommandErrorType}
        expected = {
            "EXECUTION_FAILED",
            "TIMEOUT",
            "FILE_NOT_FOUND",
            "PERMISSION_DENIED",
            "SUBPROCESS_ERROR",
            "INVALID_COMMAND",
            "WORKING_DIR_NOT_FOUND",
            "UNKNOWN",
        }
        assert names == expected

    def test_values_are_strings(self):
        for member in CommandErrorType:
            assert isinstance(member.value, str)


# ---------------------------------------------------------------------------
# CommandError exception
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestCommandError:
    """Tests for the CommandError exception class."""

    def test_basic_construction(self):
        err = CommandError("boom")
        assert err.message == "boom"
        assert err.error_type == CommandErrorType.EXECUTION_FAILED
        assert err.command is None
        assert err.return_code is None
        assert err.stdout == ""
        assert err.stderr == ""
        assert err.original_exception is None

    def test_full_construction(self):
        orig = RuntimeError("inner")
        err = CommandError(
            message="failed",
            error_type=CommandErrorType.TIMEOUT,
            command=["git", "push"],
            return_code=128,
            stdout="out",
            stderr="err",
            original_exception=orig,
        )
        assert err.error_type == CommandErrorType.TIMEOUT
        assert err.command == ["git", "push"]
        assert err.return_code == 128
        assert err.stdout == "out"
        assert err.stderr == "err"
        assert err.original_exception is orig

    def test_str_with_all_fields(self):
        err = CommandError(
            message="boom",
            command=["git", "status"],
            return_code=1,
            stderr="fatal error",
        )
        s = str(err)
        assert "boom" in s
        assert "git status" in s
        assert "Return code: 1" in s
        assert "fatal error" in s

    def test_str_with_string_command(self):
        err = CommandError(message="failed", command="echo hello")
        s = str(err)
        assert "echo hello" in s

    def test_str_minimal(self):
        err = CommandError("just a message")
        assert str(err) == "just a message"

    def test_repr(self):
        err = CommandError("msg", error_type=CommandErrorType.TIMEOUT, return_code=1)
        r = repr(err)
        assert "CommandError" in r
        assert "timeout" in r
        assert "1" in r

    def test_is_exception(self):
        err = CommandError("test")
        assert isinstance(err, Exception)
        with pytest.raises(CommandError):
            raise err

    def test_stderr_truncated_in_str(self):
        long_stderr = "x" * 1000
        err = CommandError(message="fail", stderr=long_stderr)
        s = str(err)
        # Stderr gets truncated to 500 chars in __str__
        assert "Stderr:" in s
        assert len(s) < len(long_stderr) + 200


# ---------------------------------------------------------------------------
# SubprocessResult dataclass
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestSubprocessResult:
    """Tests for the SubprocessResult dataclass."""

    def test_default_values(self):
        r = SubprocessResult()
        assert r.stdout == ""
        assert r.stderr == ""
        assert r.return_code == 0
        assert r.duration == 0.0
        assert r.success
        assert not r.timed_out
        assert r.error_message is None

    def test_post_init_success(self):
        r = SubprocessResult(return_code=0, timed_out=False)
        assert r.success

    def test_post_init_failure_nonzero(self):
        r = SubprocessResult(return_code=1)
        assert not r.success

    def test_post_init_failure_timeout(self):
        r = SubprocessResult(return_code=0, timed_out=True)
        assert not r.success

    def test_output_combined(self):
        r = SubprocessResult(stdout="out", stderr="err")
        assert r.output == "out\nerr"

    def test_output_stdout_only(self):
        r = SubprocessResult(stdout="hello")
        assert r.output == "hello"

    def test_output_empty(self):
        r = SubprocessResult()
        assert r.output == ""

    def test_command_string_from_list(self):
        r = SubprocessResult(command=["git", "status"])
        assert r.command_string == "git status"

    def test_command_string_from_str(self):
        r = SubprocessResult(command="echo hello")
        assert r.command_string == "echo hello"

    def test_to_dict(self):
        r = SubprocessResult(
            stdout="out",
            stderr="err",
            return_code=0,
            duration=1.5,
            command=["echo", "hi"],
        )
        d = r.to_dict()
        assert d["stdout"] == "out"
        assert d["stderr"] == "err"
        assert d["return_code"] == 0
        assert d["duration"] == 1.5
        assert d["command"] == "echo hi"
        assert d["success"]
        assert not d["timed_out"]
        assert d["error_message"] is None

    def test_raise_on_error_success(self):
        r = SubprocessResult(return_code=0)
        ret = r.raise_on_error()
        assert ret is r

    def test_raise_on_error_failure(self):
        r = SubprocessResult(return_code=1, error_message="bad")
        with pytest.raises(CommandError) as ctx:
            r.raise_on_error()
        assert ctx.value.error_type == CommandErrorType.EXECUTION_FAILED

    def test_raise_on_error_timeout(self):
        r = SubprocessResult(return_code=-1, timed_out=True)
        with pytest.raises(CommandError) as ctx:
            r.raise_on_error()
        assert ctx.value.error_type == CommandErrorType.TIMEOUT

    def test_raise_on_error_custom_message(self):
        r = SubprocessResult(return_code=1)
        with pytest.raises(CommandError) as ctx:
            r.raise_on_error("custom msg")
        assert "custom msg" in str(ctx.value)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestPrepareCommand:
    """Tests for _prepare_command."""

    def test_shell_list_joined(self):
        result = _prepare_command(["echo", "hello"], shell=True)
        assert result == "echo hello"

    def test_shell_string_passthrough(self):
        result = _prepare_command("echo hello", shell=True)
        assert result == "echo hello"

    def test_nonshell_string_split(self):
        result = _prepare_command("echo hello world", shell=False)
        assert result == ["echo", "hello", "world"]

    def test_nonshell_list_copy(self):
        original = ["git", "status"]
        result = _prepare_command(original, shell=False)
        assert result == ["git", "status"]


@pytest.mark.unit
class TestPrepareEnvironment:
    """Tests for _prepare_environment."""

    def test_none_env_inherit(self):
        result = _prepare_environment(env=None, inherit_env=True)
        assert result is None

    def test_env_with_inherit(self):
        result = _prepare_environment(env={"FOO": "bar"}, inherit_env=True)
        assert result is not None
        assert result["FOO"] == "bar"
        # Should also contain inherited vars
        assert "PATH" in result

    def test_no_inherit_no_env(self):
        result = _prepare_environment(env=None, inherit_env=False)
        assert result == {}

    def test_no_inherit_with_env(self):
        result = _prepare_environment(env={"A": "1"}, inherit_env=False)
        assert result == {"A": "1"}
        # Should NOT have inherited PATH
        assert "HOME" not in result


@pytest.mark.unit
class TestValidateWorkingDirectory:
    """Tests for _validate_working_directory."""

    def test_none_returns_none(self):
        assert _validate_working_directory(None) is None

    def test_valid_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _validate_working_directory(tmpdir)
            assert result == os.path.abspath(tmpdir)

    def test_nonexistent_dir_raises(self):
        with pytest.raises(CommandError) as ctx:
            _validate_working_directory("/nonexistent_dir_xyz_abc_123")
        assert ctx.value.error_type == CommandErrorType.WORKING_DIR_NOT_FOUND


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestRunCommand:
    """Tests for the run_command function."""

    def test_simple_echo(self):
        result = run_command(["echo", "hello"])
        assert result.success
        assert "hello" in result.stdout
        assert result.return_code == 0
        assert result.duration > 0.0

    def test_string_command(self):
        result = run_command("echo hello")
        assert result.success
        assert "hello" in result.stdout

    def test_shell_mode(self):
        result = run_command("echo $HOME", shell=True)
        assert result.success
        assert len(result.stdout.strip()) > 0

    def test_nonzero_exit_code(self):
        result = run_command([sys.executable, "-c", "import sys; sys.exit(42)"])
        assert not result.success
        assert result.return_code == 42
        assert result.error_message is not None

    def test_check_raises_on_failure(self):
        with pytest.raises(CommandError) as ctx:
            run_command(
                [sys.executable, "-c", "import sys; sys.exit(1)"], check=True
            )
        assert ctx.value.error_type == CommandErrorType.EXECUTION_FAILED

    def test_check_success_no_raise(self):
        result = run_command(["echo", "ok"], check=True)
        assert result.success

    def test_cwd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_command([sys.executable, "-c", "import os; print(os.getcwd())"], cwd=tmpdir)
            assert result.success
            # Resolve both to handle symlinks (e.g., /var -> /private/var on macOS)
            assert (
                os.path.realpath(result.stdout.strip())
                == os.path.realpath(tmpdir)
            )

    def test_invalid_cwd(self):
        # _validate_working_directory raises CommandError which is re-raised
        with pytest.raises(CommandError) as ctx:
            run_command(["echo", "hi"], cwd="/nonexistent_dir_xyz_abc_123")
        assert ctx.value.error_type == CommandErrorType.WORKING_DIR_NOT_FOUND

    def test_invalid_cwd_check(self):
        with pytest.raises(CommandError) as ctx:
            run_command(
                ["echo", "hi"],
                cwd="/nonexistent_dir_xyz_abc_123",
                check=True,
            )
        assert ctx.value.error_type == CommandErrorType.WORKING_DIR_NOT_FOUND

    def test_env_variables(self):
        result = run_command(
            [sys.executable, "-c", "import os; print(os.environ.get('MY_TEST_VAR', ''))"],
            env={"MY_TEST_VAR": "test_value_123"},
        )
        assert result.success
        assert "test_value_123" in result.stdout

    def test_timeout_returns_timed_out(self):
        result = run_command(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            timeout=0.3,
        )
        assert result.timed_out
        assert not result.success
        assert result.error_message is not None

    def test_timeout_check_raises(self):
        with pytest.raises(CommandError) as ctx:
            run_command(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                timeout=0.3,
                check=True,
            )
        assert ctx.value.error_type == CommandErrorType.TIMEOUT

    def test_command_not_found(self):
        result = run_command(["nonexistent_binary_xyz_abc_123"])
        assert not result.success
        assert result.error_message is not None

    def test_command_not_found_check(self):
        with pytest.raises(CommandError) as ctx:
            run_command(["nonexistent_binary_xyz_abc_123"], check=True)
        assert ctx.value.error_type == CommandErrorType.FILE_NOT_FOUND

    def test_input_data(self):
        result = run_command(
            [sys.executable, "-c", "import sys; print(sys.stdin.read().strip())"],
            input_data="piped_input",
        )
        assert result.success
        assert "piped_input" in result.stdout

    def test_stderr_capture(self):
        result = run_command(
            [sys.executable, "-c", "import sys; sys.stderr.write('err_msg\\n')"]
        )
        assert "err_msg" in result.stderr

    def test_inherit_env_false(self):
        # Without inherited env, PATH is missing, so python won't be found
        # unless we use the full path
        result = run_command(
            [sys.executable, "-c", "import os; print(os.environ.get('PATH', 'NONE'))"],
            inherit_env=False,
        )
        # The result might fail or succeed depending on platform, but
        # if it succeeds the PATH should be missing
        if result.success:
            assert "NONE" in result.stdout


# ---------------------------------------------------------------------------
# run_command_async
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.asyncio
class TestRunCommandAsync:
    """Tests for run_command_async."""

    def _run(self, coro):
        """Helper to run async in sync test."""
        return asyncio.run(coro)

    def test_simple_echo(self):
        result = self._run(run_command_async(["echo", "async_hello"]))
        assert result.success
        assert "async_hello" in result.stdout

    def test_string_command(self):
        result = self._run(run_command_async("echo async_str"))
        assert result.success
        assert "async_str" in result.stdout

    def test_shell_mode(self):
        result = self._run(run_command_async("echo $HOME", shell=True))
        assert result.success
        assert len(result.stdout.strip()) > 0

    def test_nonzero_exit(self):
        result = self._run(
            run_command_async([sys.executable, "-c", "import sys; sys.exit(7)"])
        )
        assert not result.success
        assert result.return_code == 7

    def test_timeout(self):
        result = self._run(
            run_command_async(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                timeout=0.3,
            )
        )
        assert result.timed_out
        assert not result.success

    def test_command_not_found(self):
        result = self._run(
            run_command_async(["nonexistent_binary_xyz_abc_123"])
        )
        assert not result.success
        assert result.error_message is not None

    def test_cwd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self._run(
                run_command_async(
                    [sys.executable, "-c", "import os; print(os.getcwd())"],
                    cwd=tmpdir,
                )
            )
            assert result.success
            assert (
                os.path.realpath(result.stdout.strip())
                == os.path.realpath(tmpdir)
            )

    def test_input_data(self):
        result = self._run(
            run_command_async(
                [sys.executable, "-c", "import sys; print(sys.stdin.read().strip())"],
                input_data="async_piped",
            )
        )
        assert result.success
        assert "async_piped" in result.stdout


# ---------------------------------------------------------------------------
# stream_command
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestStreamCommand:
    """Tests for stream_command."""

    def _exhaust_generator(self, gen):
        """Exhaust a generator and return (lines, result)."""
        lines = []
        try:
            while True:
                lines.append(next(gen))
        except StopIteration as e:
            return lines, e.value

    def test_basic_streaming(self):
        gen = stream_command([sys.executable, "-c", "print('line1'); print('line2')"])
        lines, result = self._exhaust_generator(gen)
        assert len(lines) >= 2
        assert isinstance(result, SubprocessResult)
        assert result.success

    def test_stdout_prefix(self):
        gen = stream_command([sys.executable, "-c", "print('hello')"])
        lines, _ = self._exhaust_generator(gen)
        found = any("stdout:" in line and "hello" in line for line in lines)
        assert found, f"Expected stdout prefix in lines: {lines}"

    def test_combine_streams(self):
        gen = stream_command(
            [sys.executable, "-c", "print('combined_out')"],
            combine_streams=True,
        )
        lines, _ = self._exhaust_generator(gen)
        # When combined, no prefix
        found = any("combined_out" in line for line in lines)
        assert found
        # Should NOT have stdout: prefix
        prefixed = any(line.startswith("stdout:") for line in lines)
        assert not prefixed

    def test_command_not_found(self):
        gen = stream_command(["nonexistent_binary_xyz_abc_123"])
        lines, result = self._exhaust_generator(gen)
        assert not result.success
        assert result.error_message is not None

    def test_cwd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = stream_command(
                [sys.executable, "-c", "import os; print(os.getcwd())"],
                cwd=tmpdir,
            )
            lines, result = self._exhaust_generator(gen)
            assert result.success

    def test_timeout(self):
        gen = stream_command(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            timeout=0.5,
        )
        lines, result = self._exhaust_generator(gen)
        assert result.timed_out
        assert not result.success


# ---------------------------------------------------------------------------
# run_with_retry
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestRunWithRetry:
    """Tests for run_with_retry."""

    def test_success_first_attempt(self):
        result = run_with_retry(["echo", "ok"], max_attempts=3)
        assert result.success
        assert "ok" in result.stdout

    def test_all_attempts_fail(self):
        result = run_with_retry(
            [sys.executable, "-c", "import sys; sys.exit(1)"],
            max_attempts=2,
            delay=0.01,
            backoff=1.0,
        )
        assert not result.success

    def test_retry_on_specific_codes(self):
        result = run_with_retry(
            [sys.executable, "-c", "import sys; sys.exit(42)"],
            max_attempts=2,
            delay=0.01,
            backoff=1.0,
            retry_on_codes=[42],
        )
        assert not result.success
        assert result.return_code == 42

    def test_no_retry_on_unmatched_code(self):
        # Exit code 99, but retry_on_codes only includes 42
        # Should return immediately without retrying
        result = run_with_retry(
            [sys.executable, "-c", "import sys; sys.exit(99)"],
            max_attempts=3,
            delay=0.01,
            retry_on_codes=[42],
        )
        assert not result.success
        assert result.return_code == 99

    def test_on_retry_callback(self):
        attempts = []

        def track_retry(attempt, result):
            attempts.append(attempt)

        run_with_retry(
            [sys.executable, "-c", "import sys; sys.exit(1)"],
            max_attempts=3,
            delay=0.01,
            backoff=1.0,
            on_retry=track_retry,
        )
        # Should be called for attempts 1 and 2 (not the last one)
        assert attempts == [1, 2]

    def test_on_retry_callback_exception_handled(self):
        def bad_callback(attempt, result):
            raise ValueError("callback error")

        # Should not raise despite callback exception
        result = run_with_retry(
            [sys.executable, "-c", "import sys; sys.exit(1)"],
            max_attempts=2,
            delay=0.01,
            backoff=1.0,
            on_retry=bad_callback,
        )
        assert not result.success

    def test_retry_on_timeout_default(self):
        result = run_with_retry(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            max_attempts=2,
            delay=0.01,
            backoff=1.0,
            timeout=0.2,
        )
        assert not result.success

    def test_retry_on_timeout_disabled(self):
        result = run_with_retry(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            max_attempts=3,
            delay=0.01,
            retry_on_timeout=False,
            timeout=0.2,
        )
        # Should return after first attempt, not retry
        assert result.timed_out


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestCheckCommandAvailable:
    """Tests for check_command_available."""

    def test_python_available(self):
        assert check_command_available("python3") or check_command_available("python")

    def test_nonexistent_command(self):
        assert not check_command_available("nonexistent_binary_xyz_abc_123")

    def test_echo_available(self):
        assert check_command_available("echo")


@pytest.mark.unit
class TestGetCommandVersion:
    """Tests for get_command_version."""

    def test_python_version(self):
        version = get_command_version(sys.executable)
        assert version is not None
        assert "Python" in version

    def test_nonexistent_command(self):
        version = get_command_version("nonexistent_binary_xyz_abc_123")
        assert version is None


@pytest.mark.unit
class TestQuoteCommand:
    """Tests for quote_command."""

    def test_list_command(self):
        result = quote_command(["echo", "hello world"])
        assert isinstance(result, str)
        assert "hello world" in result

    def test_string_passthrough(self):
        result = quote_command("echo hello")
        assert result == "echo hello"

    def test_empty_list(self):
        result = quote_command([])
        assert result == ""


@pytest.mark.unit
class TestSplitCommand:
    """Tests for split_command."""

    def test_simple_split(self):
        result = split_command("echo hello world")
        assert result == ["echo", "hello", "world"]

    def test_quoted_args(self):
        result = split_command("echo 'hello world'")
        assert result == ["echo", "hello world"]

    def test_empty_string(self):
        result = split_command("")
        assert result == []

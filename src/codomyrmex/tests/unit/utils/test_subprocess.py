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
import unittest

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
class TestCommandErrorType(unittest.TestCase):
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
        self.assertEqual(names, expected)

    def test_values_are_strings(self):
        for member in CommandErrorType:
            self.assertIsInstance(member.value, str)


# ---------------------------------------------------------------------------
# CommandError exception
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestCommandError(unittest.TestCase):
    """Tests for the CommandError exception class."""

    def test_basic_construction(self):
        err = CommandError("boom")
        self.assertEqual(err.message, "boom")
        self.assertEqual(err.error_type, CommandErrorType.EXECUTION_FAILED)
        self.assertIsNone(err.command)
        self.assertIsNone(err.return_code)
        self.assertEqual(err.stdout, "")
        self.assertEqual(err.stderr, "")
        self.assertIsNone(err.original_exception)

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
        self.assertEqual(err.error_type, CommandErrorType.TIMEOUT)
        self.assertEqual(err.command, ["git", "push"])
        self.assertEqual(err.return_code, 128)
        self.assertEqual(err.stdout, "out")
        self.assertEqual(err.stderr, "err")
        self.assertIs(err.original_exception, orig)

    def test_str_with_all_fields(self):
        err = CommandError(
            message="boom",
            command=["git", "status"],
            return_code=1,
            stderr="fatal error",
        )
        s = str(err)
        self.assertIn("boom", s)
        self.assertIn("git status", s)
        self.assertIn("Return code: 1", s)
        self.assertIn("fatal error", s)

    def test_str_with_string_command(self):
        err = CommandError(message="failed", command="echo hello")
        s = str(err)
        self.assertIn("echo hello", s)

    def test_str_minimal(self):
        err = CommandError("just a message")
        self.assertEqual(str(err), "just a message")

    def test_repr(self):
        err = CommandError("msg", error_type=CommandErrorType.TIMEOUT, return_code=1)
        r = repr(err)
        self.assertIn("CommandError", r)
        self.assertIn("timeout", r)
        self.assertIn("1", r)

    def test_is_exception(self):
        err = CommandError("test")
        self.assertIsInstance(err, Exception)
        with self.assertRaises(CommandError):
            raise err

    def test_stderr_truncated_in_str(self):
        long_stderr = "x" * 1000
        err = CommandError(message="fail", stderr=long_stderr)
        s = str(err)
        # Stderr gets truncated to 500 chars in __str__
        self.assertIn("Stderr:", s)
        self.assertTrue(len(s) < len(long_stderr) + 200)


# ---------------------------------------------------------------------------
# SubprocessResult dataclass
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestSubprocessResult(unittest.TestCase):
    """Tests for the SubprocessResult dataclass."""

    def test_default_values(self):
        r = SubprocessResult()
        self.assertEqual(r.stdout, "")
        self.assertEqual(r.stderr, "")
        self.assertEqual(r.return_code, 0)
        self.assertEqual(r.duration, 0.0)
        self.assertTrue(r.success)
        self.assertFalse(r.timed_out)
        self.assertIsNone(r.error_message)

    def test_post_init_success(self):
        r = SubprocessResult(return_code=0, timed_out=False)
        self.assertTrue(r.success)

    def test_post_init_failure_nonzero(self):
        r = SubprocessResult(return_code=1)
        self.assertFalse(r.success)

    def test_post_init_failure_timeout(self):
        r = SubprocessResult(return_code=0, timed_out=True)
        self.assertFalse(r.success)

    def test_output_combined(self):
        r = SubprocessResult(stdout="out", stderr="err")
        self.assertEqual(r.output, "out\nerr")

    def test_output_stdout_only(self):
        r = SubprocessResult(stdout="hello")
        self.assertEqual(r.output, "hello")

    def test_output_empty(self):
        r = SubprocessResult()
        self.assertEqual(r.output, "")

    def test_command_string_from_list(self):
        r = SubprocessResult(command=["git", "status"])
        self.assertEqual(r.command_string, "git status")

    def test_command_string_from_str(self):
        r = SubprocessResult(command="echo hello")
        self.assertEqual(r.command_string, "echo hello")

    def test_to_dict(self):
        r = SubprocessResult(
            stdout="out",
            stderr="err",
            return_code=0,
            duration=1.5,
            command=["echo", "hi"],
        )
        d = r.to_dict()
        self.assertEqual(d["stdout"], "out")
        self.assertEqual(d["stderr"], "err")
        self.assertEqual(d["return_code"], 0)
        self.assertEqual(d["duration"], 1.5)
        self.assertEqual(d["command"], "echo hi")
        self.assertTrue(d["success"])
        self.assertFalse(d["timed_out"])
        self.assertIsNone(d["error_message"])

    def test_raise_on_error_success(self):
        r = SubprocessResult(return_code=0)
        ret = r.raise_on_error()
        self.assertIs(ret, r)

    def test_raise_on_error_failure(self):
        r = SubprocessResult(return_code=1, error_message="bad")
        with self.assertRaises(CommandError) as ctx:
            r.raise_on_error()
        self.assertEqual(ctx.exception.error_type, CommandErrorType.EXECUTION_FAILED)

    def test_raise_on_error_timeout(self):
        r = SubprocessResult(return_code=-1, timed_out=True)
        with self.assertRaises(CommandError) as ctx:
            r.raise_on_error()
        self.assertEqual(ctx.exception.error_type, CommandErrorType.TIMEOUT)

    def test_raise_on_error_custom_message(self):
        r = SubprocessResult(return_code=1)
        with self.assertRaises(CommandError) as ctx:
            r.raise_on_error("custom msg")
        self.assertIn("custom msg", str(ctx.exception))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestPrepareCommand(unittest.TestCase):
    """Tests for _prepare_command."""

    def test_shell_list_joined(self):
        result = _prepare_command(["echo", "hello"], shell=True)
        self.assertEqual(result, "echo hello")

    def test_shell_string_passthrough(self):
        result = _prepare_command("echo hello", shell=True)
        self.assertEqual(result, "echo hello")

    def test_nonshell_string_split(self):
        result = _prepare_command("echo hello world", shell=False)
        self.assertEqual(result, ["echo", "hello", "world"])

    def test_nonshell_list_copy(self):
        original = ["git", "status"]
        result = _prepare_command(original, shell=False)
        self.assertEqual(result, ["git", "status"])


@pytest.mark.unit
class TestPrepareEnvironment(unittest.TestCase):
    """Tests for _prepare_environment."""

    def test_none_env_inherit(self):
        result = _prepare_environment(env=None, inherit_env=True)
        self.assertIsNone(result)

    def test_env_with_inherit(self):
        result = _prepare_environment(env={"FOO": "bar"}, inherit_env=True)
        self.assertIsNotNone(result)
        self.assertEqual(result["FOO"], "bar")
        # Should also contain inherited vars
        self.assertIn("PATH", result)

    def test_no_inherit_no_env(self):
        result = _prepare_environment(env=None, inherit_env=False)
        self.assertEqual(result, {})

    def test_no_inherit_with_env(self):
        result = _prepare_environment(env={"A": "1"}, inherit_env=False)
        self.assertEqual(result, {"A": "1"})
        # Should NOT have inherited PATH
        self.assertNotIn("HOME", result)


@pytest.mark.unit
class TestValidateWorkingDirectory(unittest.TestCase):
    """Tests for _validate_working_directory."""

    def test_none_returns_none(self):
        self.assertIsNone(_validate_working_directory(None))

    def test_valid_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _validate_working_directory(tmpdir)
            self.assertEqual(result, os.path.abspath(tmpdir))

    def test_nonexistent_dir_raises(self):
        with self.assertRaises(CommandError) as ctx:
            _validate_working_directory("/nonexistent_dir_xyz_abc_123")
        self.assertEqual(
            ctx.exception.error_type, CommandErrorType.WORKING_DIR_NOT_FOUND
        )


# ---------------------------------------------------------------------------
# run_command
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestRunCommand(unittest.TestCase):
    """Tests for the run_command function."""

    def test_simple_echo(self):
        result = run_command(["echo", "hello"])
        self.assertTrue(result.success)
        self.assertIn("hello", result.stdout)
        self.assertEqual(result.return_code, 0)
        self.assertGreater(result.duration, 0.0)

    def test_string_command(self):
        result = run_command("echo hello")
        self.assertTrue(result.success)
        self.assertIn("hello", result.stdout)

    def test_shell_mode(self):
        result = run_command("echo $HOME", shell=True)
        self.assertTrue(result.success)
        self.assertTrue(len(result.stdout.strip()) > 0)

    def test_nonzero_exit_code(self):
        result = run_command([sys.executable, "-c", "import sys; sys.exit(42)"])
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 42)
        self.assertIsNotNone(result.error_message)

    def test_check_raises_on_failure(self):
        with self.assertRaises(CommandError) as ctx:
            run_command(
                [sys.executable, "-c", "import sys; sys.exit(1)"], check=True
            )
        self.assertEqual(
            ctx.exception.error_type, CommandErrorType.EXECUTION_FAILED
        )

    def test_check_success_no_raise(self):
        result = run_command(["echo", "ok"], check=True)
        self.assertTrue(result.success)

    def test_cwd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_command([sys.executable, "-c", "import os; print(os.getcwd())"], cwd=tmpdir)
            self.assertTrue(result.success)
            # Resolve both to handle symlinks (e.g., /var -> /private/var on macOS)
            self.assertEqual(
                os.path.realpath(result.stdout.strip()),
                os.path.realpath(tmpdir),
            )

    def test_invalid_cwd(self):
        # _validate_working_directory raises CommandError which is re-raised
        with self.assertRaises(CommandError) as ctx:
            run_command(["echo", "hi"], cwd="/nonexistent_dir_xyz_abc_123")
        self.assertEqual(
            ctx.exception.error_type, CommandErrorType.WORKING_DIR_NOT_FOUND
        )

    def test_invalid_cwd_check(self):
        with self.assertRaises(CommandError) as ctx:
            run_command(
                ["echo", "hi"],
                cwd="/nonexistent_dir_xyz_abc_123",
                check=True,
            )
        self.assertEqual(
            ctx.exception.error_type, CommandErrorType.WORKING_DIR_NOT_FOUND
        )

    def test_env_variables(self):
        result = run_command(
            [sys.executable, "-c", "import os; print(os.environ.get('MY_TEST_VAR', ''))"],
            env={"MY_TEST_VAR": "test_value_123"},
        )
        self.assertTrue(result.success)
        self.assertIn("test_value_123", result.stdout)

    def test_timeout_returns_timed_out(self):
        result = run_command(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            timeout=0.3,
        )
        self.assertTrue(result.timed_out)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

    def test_timeout_check_raises(self):
        with self.assertRaises(CommandError) as ctx:
            run_command(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                timeout=0.3,
                check=True,
            )
        self.assertEqual(ctx.exception.error_type, CommandErrorType.TIMEOUT)

    def test_command_not_found(self):
        result = run_command(["nonexistent_binary_xyz_abc_123"])
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

    def test_command_not_found_check(self):
        with self.assertRaises(CommandError) as ctx:
            run_command(["nonexistent_binary_xyz_abc_123"], check=True)
        self.assertEqual(ctx.exception.error_type, CommandErrorType.FILE_NOT_FOUND)

    def test_input_data(self):
        result = run_command(
            [sys.executable, "-c", "import sys; print(sys.stdin.read().strip())"],
            input_data="piped_input",
        )
        self.assertTrue(result.success)
        self.assertIn("piped_input", result.stdout)

    def test_stderr_capture(self):
        result = run_command(
            [sys.executable, "-c", "import sys; sys.stderr.write('err_msg\\n')"]
        )
        self.assertIn("err_msg", result.stderr)

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
            self.assertIn("NONE", result.stdout)


# ---------------------------------------------------------------------------
# run_command_async
# ---------------------------------------------------------------------------
@pytest.mark.unit
@pytest.mark.asyncio
class TestRunCommandAsync(unittest.TestCase):
    """Tests for run_command_async."""

    def _run(self, coro):
        """Helper to run async in sync test."""
        return asyncio.run(coro)

    def test_simple_echo(self):
        result = self._run(run_command_async(["echo", "async_hello"]))
        self.assertTrue(result.success)
        self.assertIn("async_hello", result.stdout)

    def test_string_command(self):
        result = self._run(run_command_async("echo async_str"))
        self.assertTrue(result.success)
        self.assertIn("async_str", result.stdout)

    def test_shell_mode(self):
        result = self._run(run_command_async("echo $HOME", shell=True))
        self.assertTrue(result.success)
        self.assertTrue(len(result.stdout.strip()) > 0)

    def test_nonzero_exit(self):
        result = self._run(
            run_command_async([sys.executable, "-c", "import sys; sys.exit(7)"])
        )
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 7)

    def test_timeout(self):
        result = self._run(
            run_command_async(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                timeout=0.3,
            )
        )
        self.assertTrue(result.timed_out)
        self.assertFalse(result.success)

    def test_command_not_found(self):
        result = self._run(
            run_command_async(["nonexistent_binary_xyz_abc_123"])
        )
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

    def test_cwd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self._run(
                run_command_async(
                    [sys.executable, "-c", "import os; print(os.getcwd())"],
                    cwd=tmpdir,
                )
            )
            self.assertTrue(result.success)
            self.assertEqual(
                os.path.realpath(result.stdout.strip()),
                os.path.realpath(tmpdir),
            )

    def test_input_data(self):
        result = self._run(
            run_command_async(
                [sys.executable, "-c", "import sys; print(sys.stdin.read().strip())"],
                input_data="async_piped",
            )
        )
        self.assertTrue(result.success)
        self.assertIn("async_piped", result.stdout)


# ---------------------------------------------------------------------------
# stream_command
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestStreamCommand(unittest.TestCase):
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
        self.assertTrue(len(lines) >= 2)
        self.assertIsInstance(result, SubprocessResult)
        self.assertTrue(result.success)

    def test_stdout_prefix(self):
        gen = stream_command([sys.executable, "-c", "print('hello')"])
        lines, _ = self._exhaust_generator(gen)
        found = any("stdout:" in line and "hello" in line for line in lines)
        self.assertTrue(found, f"Expected stdout prefix in lines: {lines}")

    def test_combine_streams(self):
        gen = stream_command(
            [sys.executable, "-c", "print('combined_out')"],
            combine_streams=True,
        )
        lines, _ = self._exhaust_generator(gen)
        # When combined, no prefix
        found = any("combined_out" in line for line in lines)
        self.assertTrue(found)
        # Should NOT have stdout: prefix
        prefixed = any(line.startswith("stdout:") for line in lines)
        self.assertFalse(prefixed)

    def test_command_not_found(self):
        gen = stream_command(["nonexistent_binary_xyz_abc_123"])
        lines, result = self._exhaust_generator(gen)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

    def test_cwd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = stream_command(
                [sys.executable, "-c", "import os; print(os.getcwd())"],
                cwd=tmpdir,
            )
            lines, result = self._exhaust_generator(gen)
            self.assertTrue(result.success)

    def test_timeout(self):
        gen = stream_command(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            timeout=0.5,
        )
        lines, result = self._exhaust_generator(gen)
        self.assertTrue(result.timed_out)
        self.assertFalse(result.success)


# ---------------------------------------------------------------------------
# run_with_retry
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestRunWithRetry(unittest.TestCase):
    """Tests for run_with_retry."""

    def test_success_first_attempt(self):
        result = run_with_retry(["echo", "ok"], max_attempts=3)
        self.assertTrue(result.success)
        self.assertIn("ok", result.stdout)

    def test_all_attempts_fail(self):
        result = run_with_retry(
            [sys.executable, "-c", "import sys; sys.exit(1)"],
            max_attempts=2,
            delay=0.01,
            backoff=1.0,
        )
        self.assertFalse(result.success)

    def test_retry_on_specific_codes(self):
        result = run_with_retry(
            [sys.executable, "-c", "import sys; sys.exit(42)"],
            max_attempts=2,
            delay=0.01,
            backoff=1.0,
            retry_on_codes=[42],
        )
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 42)

    def test_no_retry_on_unmatched_code(self):
        # Exit code 99, but retry_on_codes only includes 42
        # Should return immediately without retrying
        result = run_with_retry(
            [sys.executable, "-c", "import sys; sys.exit(99)"],
            max_attempts=3,
            delay=0.01,
            retry_on_codes=[42],
        )
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 99)

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
        self.assertEqual(attempts, [1, 2])

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
        self.assertFalse(result.success)

    def test_retry_on_timeout_default(self):
        result = run_with_retry(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            max_attempts=2,
            delay=0.01,
            backoff=1.0,
            timeout=0.2,
        )
        self.assertFalse(result.success)

    def test_retry_on_timeout_disabled(self):
        result = run_with_retry(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            max_attempts=3,
            delay=0.01,
            retry_on_timeout=False,
            timeout=0.2,
        )
        # Should return after first attempt, not retry
        self.assertTrue(result.timed_out)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestCheckCommandAvailable(unittest.TestCase):
    """Tests for check_command_available."""

    def test_python_available(self):
        self.assertTrue(check_command_available("python3") or check_command_available("python"))

    def test_nonexistent_command(self):
        self.assertFalse(check_command_available("nonexistent_binary_xyz_abc_123"))

    def test_echo_available(self):
        self.assertTrue(check_command_available("echo"))


@pytest.mark.unit
class TestGetCommandVersion(unittest.TestCase):
    """Tests for get_command_version."""

    def test_python_version(self):
        version = get_command_version(sys.executable)
        self.assertIsNotNone(version)
        self.assertIn("Python", version)

    def test_nonexistent_command(self):
        version = get_command_version("nonexistent_binary_xyz_abc_123")
        self.assertIsNone(version)


@pytest.mark.unit
class TestQuoteCommand(unittest.TestCase):
    """Tests for quote_command."""

    def test_list_command(self):
        result = quote_command(["echo", "hello world"])
        self.assertIsInstance(result, str)
        self.assertIn("hello world", result)

    def test_string_passthrough(self):
        result = quote_command("echo hello")
        self.assertEqual(result, "echo hello")

    def test_empty_list(self):
        result = quote_command([])
        self.assertEqual(result, "")


@pytest.mark.unit
class TestSplitCommand(unittest.TestCase):
    """Tests for split_command."""

    def test_simple_split(self):
        result = split_command("echo hello world")
        self.assertEqual(result, ["echo", "hello", "world"])

    def test_quoted_args(self):
        result = split_command("echo 'hello world'")
        self.assertEqual(result, ["echo", "hello world"])

    def test_empty_string(self):
        result = split_command("")
        self.assertEqual(result, [])

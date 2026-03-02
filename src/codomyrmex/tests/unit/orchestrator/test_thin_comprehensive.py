"""Comprehensive tests for orchestrator/thin.py composable utilities.

Zero-mock policy: uses real subprocess calls (echo, true, false).
Covers edge cases, boundary conditions, and integration paths not in test_thin.py.
"""
import asyncio
import os
import tempfile
import time
from pathlib import Path

import pytest

from codomyrmex.orchestrator.thin import (
    StepResult,
    Steps,
    batch,
    chain_scripts,
    condition,
    pipe,
    python_func,
    retry,
    run,
    run_async,
    shell,
    step,
    timeout,
    workflow,
)

pytestmark = [pytest.mark.orchestrator, pytest.mark.unit]


# ---------------------------------------------------------------------------
# shell() -- edge cases
# ---------------------------------------------------------------------------

class TestShellEdgeCases:
    """Edge-case tests for the shell() function."""

    def test_shell_empty_command(self):
        """shell() with empty string completes without crash."""
        result = shell("")
        # Empty command may succeed or fail depending on shell, but should not raise
        assert "success" in result
        assert "command" in result

    def test_shell_multiline_output(self):
        """shell() captures multiline stdout."""
        result = shell("printf 'line1\\nline2\\nline3'")
        assert result["success"] is True
        lines = result["stdout"].strip().split("\n")
        assert len(lines) == 3
        assert lines[0] == "line1"
        assert lines[2] == "line3"

    def test_shell_with_cwd(self):
        """shell() respects cwd parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = shell("pwd", cwd=Path(tmpdir))
            assert result["success"] is True
            # Resolve symlinks (macOS /private/var vs /var, /private/tmp vs /tmp)
            assert os.path.realpath(tmpdir) == os.path.realpath(result["stdout"].strip())

    def test_shell_env_merged_with_system_env(self):
        """shell() merges custom env with os.environ (PATH still works)."""
        result = shell("echo $MY_CUSTOM_123", env={"MY_CUSTOM_123": "found_it"})
        assert result["success"] is True
        assert "found_it" in result["stdout"]
        # PATH is still present (ls/echo work), so system env was merged
        result2 = shell("which echo", env={"MY_CUSTOM_123": "irrelevant"})
        assert result2["success"] is True

    def test_shell_returncode_nonzero(self):
        """shell() returns exact non-zero exit code."""
        result = shell("exit 42")
        assert result["success"] is False
        assert result["returncode"] == 42

    def test_shell_stderr_only(self):
        """shell() captures stderr when stdout is empty."""
        result = shell("echo errormsg >&2")
        assert result["success"] is True
        assert "errormsg" in result["stderr"]
        # stdout should be empty or just whitespace
        assert result["stdout"].strip() == ""

    def test_shell_both_stdout_and_stderr(self):
        """shell() captures both stdout and stderr simultaneously."""
        result = shell("echo out && echo err >&2")
        assert result["success"] is True
        assert "out" in result["stdout"]
        assert "err" in result["stderr"]

    def test_shell_timeout_returns_none_returncode(self):
        """shell() sets returncode to None on timeout."""
        result = shell("sleep 10", timeout=1)
        assert result["success"] is False
        assert result["returncode"] is None
        assert "Timeout" in result.get("error", "")

    def test_shell_execution_time_positive(self):
        """shell() execution_time is always positive."""
        result = shell("true")
        assert result["execution_time"] >= 0.0


# ---------------------------------------------------------------------------
# pipe() -- edge cases
# ---------------------------------------------------------------------------

class TestPipeEdgeCases:
    """Edge-case tests for the pipe() function."""

    def test_pipe_empty_list(self):
        """pipe() with empty list returns success with 0 completed."""
        result = pipe([])
        assert result["success"] is True
        assert result["completed"] == 0
        assert result["commands"] == 0
        assert result["results"] == []

    def test_pipe_single_command(self):
        """pipe() with single command works correctly."""
        result = pipe(["echo single"])
        assert result["success"] is True
        assert result["completed"] == 1
        assert "single" in result["final_output"]

    def test_pipe_env_variables_set(self):
        """pipe() sets PIPE_INPUT and PIPE_INDEX env for each command."""
        # Second command sees PIPE_INPUT from first command's stdout
        result = pipe(["echo hello_pipe", "echo $PIPE_INPUT"])
        assert result["success"] is True
        assert result["completed"] == 2
        # The second command should have access to PIPE_INPUT
        second_stdout = result["results"][1]["stdout"]
        assert "hello_pipe" in second_stdout

    def test_pipe_index_increments(self):
        """pipe() PIPE_INDEX increments for each command."""
        result = pipe(["echo $PIPE_INDEX", "echo $PIPE_INDEX", "echo $PIPE_INDEX"])
        assert result["success"] is True
        assert result["results"][0]["stdout"].strip() == "0"
        assert result["results"][1]["stdout"].strip() == "1"
        assert result["results"][2]["stdout"].strip() == "2"

    def test_pipe_final_output_is_last_success(self):
        """pipe() final_output is stdout of last successful command."""
        result = pipe(["echo first", "echo second", "echo third"])
        assert result["success"] is True
        assert "third" in result["final_output"]

    def test_pipe_stop_on_error_preserves_partial_results(self):
        """pipe() with stop_on_error preserves results up to failure."""
        result = pipe(["echo ok", "false", "echo unreachable"], stop_on_error=True)
        assert result["success"] is False
        assert result["completed"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["success"] is True
        assert result["results"][1]["success"] is False

    def test_pipe_continue_on_error_runs_all(self):
        """pipe() with stop_on_error=False runs all commands."""
        result = pipe(
            ["echo first", "false", "echo third"],
            stop_on_error=False
        )
        assert result["success"] is False
        assert result["completed"] == 3
        assert len(result["results"]) == 3
        # Third command still ran and succeeded
        assert result["results"][2]["success"] is True

    def test_pipe_execution_time_cumulative(self):
        """pipe() execution_time covers total duration."""
        result = pipe(["sleep 0.1", "sleep 0.1"])
        assert result["success"] is True
        assert result["execution_time"] >= 0.2

    def test_pipe_timeout_per_command_respected(self):
        """pipe() respects timeout_per_command for individual steps."""
        result = pipe(["sleep 10"], timeout_per_command=1)
        assert result["success"] is False
        assert result["results"][0]["success"] is False


# ---------------------------------------------------------------------------
# run() -- edge cases
# ---------------------------------------------------------------------------

class TestRunEdgeCases:
    """Edge-case tests for the run() function."""

    def test_run_dispatches_to_shell_for_nonpy(self):
        """run() dispatches non-.py targets to shell()."""
        result = run("echo dispatched")
        assert result["success"] is True
        assert "dispatched" in result.get("stdout", "")

    def test_run_dispatches_to_shell_for_nonexistent_py(self):
        """run() dispatches nonexistent .py file to shell() (file doesn't exist)."""
        result = run("/nonexistent/path/script.py")
        # Path doesn't exist, so run() falls through to shell()
        assert result["success"] is False

    def test_run_real_python_script_with_env(self):
        """run() passes env to Python script execution."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("import os; print(os.environ.get('RUN_TEST_VAR', 'MISSING'))")
            f.flush()
            script_path = f.name

        try:
            result = run(script_path, env={"RUN_TEST_VAR": "found_it"}, timeout=30)
            assert result is not None
            # run_script returns "status" key, not "success"
            assert result.get("status") == "passed" or result.get("success") is True
            assert "found_it" in result.get("stdout", "")
        finally:
            os.unlink(script_path)

    def test_run_python_script_failure(self):
        """run() captures Python script failure."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("raise SystemExit(1)")
            f.flush()
            script_path = f.name

        try:
            result = run(script_path, timeout=30)
            assert result is not None
            # Failed script should not have "passed" status
            assert result.get("status") != "passed" or result.get("success") is False
        finally:
            os.unlink(script_path)


# ---------------------------------------------------------------------------
# run_async() -- edge cases
# ---------------------------------------------------------------------------

class TestRunAsyncEdgeCases:
    """Edge-case tests for the run_async() function."""

    @pytest.mark.asyncio
    async def test_run_async_with_timeout(self):
        """run_async() respects timeout parameter."""
        result = await run_async("echo async_timeout_test", timeout=10)
        assert result["success"] is True
        assert "async_timeout_test" in result.get("stdout", "")

    @pytest.mark.asyncio
    async def test_run_async_failing_command(self):
        """run_async() handles failing commands."""
        result = await run_async("false", timeout=10)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_run_async_concurrent_isolation(self):
        """run_async() tasks don't interfere with each other."""
        results = await asyncio.gather(
            run_async("echo task_a"),
            run_async("echo task_b"),
        )
        assert results[0]["success"] is True
        assert results[1]["success"] is True
        assert "task_a" in results[0].get("stdout", "")
        assert "task_b" in results[1].get("stdout", "")


# ---------------------------------------------------------------------------
# batch() -- edge cases
# ---------------------------------------------------------------------------

class TestBatchEdgeCases:
    """Edge-case tests for the batch() function."""

    def test_batch_nonexistent_targets(self):
        """batch() with all nonexistent targets returns empty result."""
        from codomyrmex.orchestrator.execution.parallel_runner import ExecutionResult

        result = batch(["/nonexistent/a.py", "/nonexistent/b.py"])
        assert isinstance(result, ExecutionResult)
        assert result.total == 0

    def test_batch_mixed_existing_nonexisting(self):
        """batch() filters to only existing script paths."""
        from codomyrmex.orchestrator.execution.parallel_runner import ExecutionResult

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("print('exists')")
            f.flush()
            existing = f.name

        try:
            result = batch([existing, "/nonexistent/script.py"], timeout=30)
            assert isinstance(result, ExecutionResult)
            # Only one existing script, so total should be 1
            assert result.total == 1
        except PermissionError:
            pytest.skip("ProcessPoolExecutor not available in sandbox")
        finally:
            os.unlink(existing)


# ---------------------------------------------------------------------------
# chain_scripts() -- edge cases
# ---------------------------------------------------------------------------

class TestChainScriptsEdgeCases:
    """Edge-case tests for the chain_scripts() function."""

    def test_chain_scripts_empty_list(self):
        """chain_scripts() with empty list returns success."""
        result = chain_scripts([])
        assert result["success"] is True
        assert result["scripts"] == 0
        assert result["completed"] == 0

    def test_chain_scripts_pass_results_false(self):
        """chain_scripts() with pass_results=False doesn't set PREV_RESULT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script1 = Path(tmpdir) / "s1.py"
            script2 = Path(tmpdir) / "s2.py"
            script1.write_text("import os; print('step1')")
            script2.write_text(
                "import os; prev = os.environ.get('PREV_RESULT', 'NONE'); print(prev)"
            )

            result = chain_scripts(
                [script1, script2],
                pass_results=False,
                timeout_per_script=30
            )
            assert result["scripts"] == 2
            assert result["completed"] == 2
            # With pass_results=False, second script should NOT see PREV_RESULT
            assert "NONE" in result["results"][1].get("stdout", "")

    def test_chain_scripts_continue_on_error(self):
        """chain_scripts() with stop_on_error=False continues past failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script1 = Path(tmpdir) / "s1.py"
            script2 = Path(tmpdir) / "s2.py"
            script3 = Path(tmpdir) / "s3.py"
            script1.write_text("raise ValueError('fail')")
            script2.write_text("print('script2_ok')")
            script3.write_text("print('script3_ok')")

            result = chain_scripts(
                [script1, script2, script3],
                stop_on_error=False,
                timeout_per_script=30
            )
            assert result["success"] is False
            assert result["completed"] == 3
            assert result["scripts"] == 3

    def test_chain_scripts_nonexistent_stop_on_error(self):
        """chain_scripts() stops at nonexistent script with stop_on_error=True."""
        result = chain_scripts(
            ["/nonexistent/first.py", "/nonexistent/second.py"],
            stop_on_error=True,
            timeout_per_script=10
        )
        assert result["success"] is False
        assert result["completed"] == 1  # Stopped after first not-found

    def test_chain_scripts_nonexistent_continue(self):
        """chain_scripts() with stop_on_error=False skips nonexistent and continues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            real_script = Path(tmpdir) / "real.py"
            real_script.write_text("print('real_ok')")

            result = chain_scripts(
                ["/nonexistent/fake.py", real_script],
                stop_on_error=False,
                timeout_per_script=30
            )
            assert result["success"] is False  # Overall fails because one failed
            assert result["completed"] == 2
            # First result is a not-found error
            assert result["results"][0]["error"] == "Not found"
            assert result["results"][0]["success"] is False

    def test_chain_scripts_passed_count(self):
        """chain_scripts() counts passed scripts correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            s1 = Path(tmpdir) / "s1.py"
            s2 = Path(tmpdir) / "s2.py"
            s1.write_text("print('ok1')")
            s2.write_text("print('ok2')")

            result = chain_scripts([s1, s2], timeout_per_script=30)
            assert result["success"] is True
            assert result["passed"] == 2

    def test_chain_scripts_execution_time(self):
        """chain_scripts() tracks total execution time."""
        with tempfile.TemporaryDirectory() as tmpdir:
            s1 = Path(tmpdir) / "s1.py"
            s1.write_text("import time; time.sleep(0.1); print('done')")

            result = chain_scripts([s1], timeout_per_script=30)
            assert result["execution_time"] >= 0.1


# ---------------------------------------------------------------------------
# Steps -- edge cases
# ---------------------------------------------------------------------------

class TestStepsEdgeCases:
    """Edge-case tests for the Steps workflow builder."""

    def test_steps_fluent_chaining(self):
        """Steps.add() returns self, enabling method chaining."""
        w = workflow("fluent_test")
        returned = w.add("a", lambda: 1).add("b", lambda: 2).add("c", lambda: 3)
        assert returned is w
        assert len(w._steps) == 3

    def test_steps_auto_dependency(self):
        """Steps auto-depends on previous step when depends_on is None."""
        w = workflow("auto_deps")
        w.add("first", lambda: 1)
        w.add("second", lambda: 2)
        w.add("third", lambda: 3)
        # After adding "second", it should depend on "first"
        # After adding "third", it should depend on "second"
        # We can verify via the underlying workflow tasks
        tasks = w.workflow.tasks
        if "second" in tasks:
            assert "first" in tasks["second"].dependencies
        if "third" in tasks:
            assert "second" in tasks["third"].dependencies

    def test_steps_explicit_dependency_override(self):
        """Steps with explicit depends_on overrides auto-dependency."""
        w = workflow("explicit_deps")
        w.add("step_a", lambda: "a")
        w.add("step_b", lambda: "b")
        w.add("step_c", lambda: "c", depends_on=["step_a"])  # Skips step_b
        tasks = w.workflow.tasks
        if "step_c" in tasks:
            assert "step_a" in tasks["step_c"].dependencies
            assert "step_b" not in tasks["step_c"].dependencies

    def test_steps_add_parallel_with_depends_on(self):
        """Steps.add_parallel() with explicit depends_on."""
        w = workflow("parallel_explicit")
        w.add("setup", lambda: "setup_done")
        w.add_parallel(
            [("p1", lambda: "p1"), ("p2", lambda: "p2")],
            depends_on=["setup"]
        )
        assert "p1" in w._steps
        assert "p2" in w._steps
        tasks = w.workflow.tasks
        if "p1" in tasks:
            assert "setup" in tasks["p1"].dependencies
        if "p2" in tasks:
            assert "setup" in tasks["p2"].dependencies

    def test_steps_add_parallel_no_prior_steps(self):
        """Steps.add_parallel() with no prior steps sets no auto-depends."""
        w = workflow("parallel_no_prior")
        w.add_parallel([("a", lambda: 1), ("b", lambda: 2)])
        assert "a" in w._steps
        assert "b" in w._steps
        tasks = w.workflow.tasks
        if "a" in tasks:
            assert len(tasks["a"].dependencies) == 0

    def test_steps_add_parallel_returns_self(self):
        """Steps.add_parallel() returns self for chaining."""
        w = workflow("parallel_chain")
        returned = w.add_parallel([("x", lambda: 1)])
        assert returned is w

    def test_steps_workflow_name(self):
        """Steps preserves workflow name."""
        w = workflow("custom_name")
        assert w.workflow.name == "custom_name"

    def test_steps_default_name(self):
        """Steps() with default name uses 'workflow'."""
        s = Steps()
        assert s.workflow.name == "workflow"

    def test_steps_with_timeout(self):
        """Steps.add() with timeout parameter."""
        w = workflow("timeout_test")
        w.add("timed_step", lambda: "done", timeout=5.0)
        assert "timed_step" in w._steps

    def test_steps_with_retry_gt_1(self):
        """Steps.add() with retry > 1 creates RetryPolicy."""
        w = workflow("retry_test")
        w.add("retried_step", lambda: "ok", retry=3)
        tasks = w.workflow.tasks
        if "retried_step" in tasks:
            assert tasks["retried_step"].retry_policy is not None
            assert tasks["retried_step"].retry_policy.max_attempts == 3

    def test_steps_with_retry_eq_1(self):
        """Steps.add() with retry=1 does not create RetryPolicy."""
        w = workflow("no_retry")
        w.add("single_try", lambda: "ok", retry=1)
        tasks = w.workflow.tasks
        if "single_try" in tasks:
            assert tasks["single_try"].retry_policy is None

    def test_steps_run_sync_simple(self):
        """Steps.run_sync() executes workflow and returns result."""
        w = workflow("sync_run")
        w.add("only_step", lambda: "done")
        result = w.run_sync()
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_steps_run_async(self):
        """Steps.run() executes workflow asynchronously."""
        w = workflow("async_run")
        w.add("async_step", lambda: "async_done")
        result = await w.run()
        assert result is not None
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# step() decorator -- edge cases
# ---------------------------------------------------------------------------

class TestStepDecoratorEdgeCases:
    """Edge-case tests for the step() decorator."""

    def test_step_defaults(self):
        """step() decorator with minimal args sets correct defaults."""
        @step(name="minimal")
        def my_func():
            return 42

        assert my_func._step_name == "minimal"
        assert my_func._step_timeout is None
        assert my_func._step_retry == 1

    def test_step_preserves_return_value(self):
        """step() decorator does not alter function return value."""
        @step(name="return_test", timeout=10.0, retry=5)
        def compute():
            return {"result": 42}

        assert compute() == {"result": 42}

    def test_step_preserves_function_name(self):
        """step() decorator preserves original function __name__."""
        @step(name="named_step")
        def original_name():
            pass

        # The decorator returns the original function with attributes added
        assert original_name.__name__ == "original_name"

    def test_step_with_args(self):
        """step() decorated function can accept arguments."""
        @step(name="arg_step")
        def add(a, b):
            return a + b

        assert add(3, 4) == 7


# ---------------------------------------------------------------------------
# python_func() -- edge cases
# ---------------------------------------------------------------------------

class TestPythonFuncEdgeCases:
    """Edge-case tests for the python_func() function.

    Note: python_func uses multiprocessing; only picklable functions work.
    """

    def test_python_func_result_structure(self):
        """python_func() returns dict with expected keys."""
        result = python_func(len, args=([1, 2, 3],))
        assert isinstance(result, dict)
        assert "name" in result
        assert "type" in result
        assert "status" in result
        assert "execution_time" in result
        assert result["type"] == "function"

    def test_python_func_success_status(self):
        """python_func() sets status='passed' for successful execution."""
        result = python_func(sum, args=([1, 2, 3],))
        assert result["status"] == "passed"
        assert result["result"] == 6

    def test_python_func_with_kwargs(self):
        """python_func() passes kwargs correctly."""
        result = python_func(sorted, args=([3, 1, 2],), kwargs={"reverse": True})
        assert result["status"] == "passed"
        assert result["result"] == [3, 2, 1]

    def test_python_func_function_name_captured(self):
        """python_func() captures function name."""
        result = python_func(len, args=([],))
        assert result["name"] == "len"

    def test_python_func_with_timeout(self):
        """python_func() respects timeout parameter."""
        result = python_func(len, args=([1],), timeout=30)
        assert result is not None
        assert result["status"] == "passed"


# ---------------------------------------------------------------------------
# condition() -- edge cases
# ---------------------------------------------------------------------------

class TestConditionEdgeCases:
    """Edge-case tests for the condition() function."""

    def test_condition_identity(self):
        """condition() returns the exact same predicate object."""
        def pred(r):
            return True
        assert condition(pred) is pred

    def test_condition_with_empty_results(self):
        """condition() predicate handles empty results dict."""
        cond = condition(lambda r: len(r) == 0)
        assert cond({}) is True
        assert cond({"key": "val"}) is False

    def test_condition_with_nested_logic(self):
        """condition() works with predicates that check nested data."""
        cond = condition(
            lambda r: r.get("step1", {}).get("value", 0) > 10
        )
        assert cond({"step1": {"value": 20}}) is True
        assert cond({"step1": {"value": 5}}) is False
        assert cond({}) is False


# ---------------------------------------------------------------------------
# retry() -- edge cases
# ---------------------------------------------------------------------------

class TestRetryEdgeCases:
    """Edge-case tests for the retry() wrapper."""

    @pytest.mark.asyncio
    async def test_retry_single_attempt(self):
        """retry() with max_attempts=1 does not retry."""
        call_count = 0

        def fail_once():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        wrapped = retry(fail_once, max_attempts=1, delay=0.01)
        with pytest.raises(ValueError, match="fail"):
            await wrapped()
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_passes_args_through(self):
        """retry() passes positional and keyword args to action."""
        def greet(name, greeting="hello"):
            return f"{greeting} {name}"

        wrapped = retry(greet, max_attempts=1, delay=0.01)
        result = await wrapped("world", greeting="hi")
        assert result == "hi world"

    @pytest.mark.asyncio
    async def test_retry_backoff_timing(self):
        """retry() applies exponential backoff between attempts."""
        call_times = []

        def track_time():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("not yet")
            return "done"

        wrapped = retry(track_time, max_attempts=3, delay=0.05, backoff=2.0)
        result = await wrapped()
        assert result == "done"
        assert len(call_times) == 3
        # Second delay should be >= first delay (backoff)
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        assert delay1 >= 0.04  # ~0.05s initial delay
        assert delay2 >= 0.08  # ~0.10s after backoff

    @pytest.mark.asyncio
    async def test_retry_async_action(self):
        """retry() works with async coroutine action."""
        call_count = 0

        async def async_flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("async fail")
            return "async_success"

        wrapped = retry(async_flaky, max_attempts=3, delay=0.01)
        result = await wrapped()
        assert result == "async_success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_last_error_raised(self):
        """retry() raises the last error after all attempts fail."""
        attempt = 0

        def different_errors():
            nonlocal attempt
            attempt += 1
            raise ValueError(f"error_{attempt}")

        wrapped = retry(different_errors, max_attempts=3, delay=0.01)
        with pytest.raises(ValueError, match="error_3"):
            await wrapped()

    def test_retry_returns_callable(self):
        """retry() returns a callable async wrapper."""
        wrapped = retry(lambda: "ok", max_attempts=2, delay=0.01)
        assert callable(wrapped)
        assert asyncio.iscoroutinefunction(wrapped)


# ---------------------------------------------------------------------------
# timeout() -- edge cases
# ---------------------------------------------------------------------------

class TestTimeoutEdgeCases:
    """Edge-case tests for the timeout() decorator."""

    @pytest.mark.asyncio
    async def test_timeout_returns_value(self):
        """timeout() passes through return value of wrapped function."""
        @timeout(5.0)
        def compute():
            return {"answer": 42}

        result = await compute()
        assert result == {"answer": 42}

    @pytest.mark.asyncio
    async def test_timeout_with_args(self):
        """timeout() wrapped function accepts arguments."""
        @timeout(5.0)
        def add(a, b):
            return a + b

        result = await add(3, 7)
        assert result == 10

    @pytest.mark.asyncio
    async def test_timeout_async_within_limit(self):
        """timeout() with async function that completes in time."""
        @timeout(5.0)
        async def async_fast():
            await asyncio.sleep(0.01)
            return "fast"

        result = await async_fast()
        assert result == "fast"

    @pytest.mark.asyncio
    async def test_timeout_async_exceeds(self):
        """timeout() with async function that exceeds limit."""
        @timeout(0.05)
        async def async_slow():
            await asyncio.sleep(5.0)
            return "slow"

        with pytest.raises(asyncio.TimeoutError):
            await async_slow()

    def test_timeout_returns_decorator(self):
        """timeout() returns a decorator (callable)."""
        deco = timeout(5.0)
        assert callable(deco)

    @pytest.mark.asyncio
    async def test_timeout_decorator_produces_coroutine(self):
        """timeout() decorated function returns a coroutine when called."""
        @timeout(5.0)
        def sync_func():
            return "sync"

        result = await sync_func()
        assert result == "sync"


# ---------------------------------------------------------------------------
# StepResult dataclass -- edge cases
# ---------------------------------------------------------------------------

class TestStepResultEdgeCases:
    """Edge-case tests for the StepResult dataclass."""

    def test_step_result_with_complex_value(self):
        """StepResult stores complex value types."""
        r = StepResult(success=True, value={"nested": [1, 2, 3]})
        assert r.value == {"nested": [1, 2, 3]}

    def test_step_result_all_fields(self):
        """StepResult with all fields specified."""
        r = StepResult(
            success=True,
            value="result_data",
            error=None,
            execution_time=2.5
        )
        assert r.success is True
        assert r.value == "result_data"
        assert r.error is None
        assert r.execution_time == 2.5

    def test_step_result_equality(self):
        """StepResult dataclass supports equality comparison."""
        r1 = StepResult(success=True, value="x", execution_time=1.0)
        r2 = StepResult(success=True, value="x", execution_time=1.0)
        assert r1 == r2

    def test_step_result_inequality(self):
        """StepResult dataclass detects inequality."""
        r1 = StepResult(success=True)
        r2 = StepResult(success=False)
        assert r1 != r2


# ---------------------------------------------------------------------------
# Integration: combining multiple thin utilities
# ---------------------------------------------------------------------------

class TestThinIntegration:
    """Integration tests combining multiple thin.py utilities."""

    def test_shell_then_pipe(self):
        """shell() result can inform pipe() commands."""
        shell_result = shell("echo integration_input")
        assert shell_result["success"] is True
        text = shell_result["stdout"].strip()
        pipe_result = pipe([f"echo {text}", "wc -c"])
        assert pipe_result["success"] is True
        assert pipe_result["completed"] == 2

    def test_workflow_with_shell_steps(self):
        """workflow() can use shell() as step actions."""
        w = workflow("shell_workflow")
        w.add("check_dir", lambda: shell("ls /tmp"))
        w.add("check_user", lambda: shell("whoami"))
        assert len(w._steps) == 2

    def test_step_decorator_in_workflow(self):
        """step()-decorated functions can be used in workflow."""
        @step(name="decorated")
        def my_step():
            return shell("echo from_decorator")

        w = workflow("decorator_workflow")
        w.add(my_step._step_name, my_step)
        assert "decorated" in w._steps

    def test_chain_then_pipe(self):
        """chain_scripts result informs subsequent pipe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            s1 = Path(tmpdir) / "s1.py"
            s1.write_text("print('chain_output')")

            chain_result = chain_scripts([s1], timeout_per_script=30)
            assert chain_result["success"] is True

            # Use the passed count in a pipe
            passed = chain_result["passed"]
            pipe_result = pipe([f"echo passed_count={passed}"])
            assert pipe_result["success"] is True
            assert "passed_count=1" in pipe_result["final_output"]

    @pytest.mark.asyncio
    async def test_retry_with_shell(self):
        """retry() wrapping shell() for resilient execution."""
        def flaky_shell():
            return shell("echo resilient")

        wrapped = retry(flaky_shell, max_attempts=2, delay=0.01)
        result = await wrapped()
        assert result["success"] is True
        assert "resilient" in result["stdout"]

    def test_condition_controls_step_logic(self):
        """condition() can be used to gate workflow step logic."""
        check_pass = condition(lambda r: r.get("status") == "go")
        assert check_pass({"status": "go"}) is True
        assert check_pass({"status": "no"}) is False

        # Use in a simple if-then pattern
        gate = {"status": "go"}
        if check_pass(gate):
            result = shell("echo passed_gate")
            assert result["success"] is True
            assert "passed_gate" in result["stdout"]


# ---------------------------------------------------------------------------
# Module exports / __all__
# ---------------------------------------------------------------------------

class TestModuleExports:
    """Verify all __all__ exports are importable and correct types."""

    def test_all_exports_importable(self):
        """Every name in __all__ is importable from thin module."""
        import codomyrmex.orchestrator.thin as thin_mod

        for name in thin_mod.__all__:
            assert hasattr(thin_mod, name), f"{name} listed in __all__ but not found"

    def test_run_is_callable(self):
        """run is a callable function."""
        assert callable(run)

    def test_run_async_is_coroutine_function(self):
        """run_async is a coroutine function."""
        assert asyncio.iscoroutinefunction(run_async)

    def test_pipe_is_callable(self):
        """pipe is a callable function."""
        assert callable(pipe)

    def test_batch_is_callable(self):
        """batch is a callable function."""
        assert callable(batch)

    def test_chain_scripts_is_callable(self):
        """chain_scripts is a callable function."""
        assert callable(chain_scripts)

    def test_workflow_is_callable(self):
        """workflow is a callable function."""
        assert callable(workflow)

    def test_step_is_callable(self):
        """step is a callable function."""
        assert callable(step)

    def test_shell_is_callable(self):
        """shell is a callable function."""
        assert callable(shell)

    def test_python_func_is_callable(self):
        """python_func is a callable function."""
        assert callable(python_func)

    def test_retry_is_callable(self):
        """retry is a callable function."""
        assert callable(retry)

    def test_timeout_is_callable(self):
        """timeout is a callable function."""
        assert callable(timeout)

    def test_condition_is_callable(self):
        """condition is a callable function."""
        assert callable(condition)

    def test_steps_is_class(self):
        """Steps is a class."""
        assert isinstance(Steps, type)

    def test_step_result_is_dataclass(self):
        """StepResult is a dataclass."""
        import dataclasses
        assert dataclasses.is_dataclass(StepResult)

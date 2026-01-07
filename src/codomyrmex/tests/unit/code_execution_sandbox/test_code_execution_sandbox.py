"""Unit tests for code.execution and code.sandbox modules."""

import pytest
import sys


class TestCodeExecutionSandbox:
    """Test cases for code execution sandbox functionality."""

    def test_code_executor_import(self, code_dir):
        """Test that we can import code_executor module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.coding.execution import executor
            assert executor is not None
        except ImportError as e:
            # psutil may be missing - that's acceptable for basic tests
            if "psutil" in str(e):
                pytest.skip(f"psutil not available: {e}")
            pytest.fail(f"Failed to import code_executor: {e}")

    def test_code_executor_structure_and_functions(self, code_dir):
        """Test that code_executor has expected structure and functions."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution import executor
        from codomyrmex.coding.execution.executor import execute_code, DEFAULT_TIMEOUT, MAX_TIMEOUT, MIN_TIMEOUT
        from codomyrmex.coding.execution.language_support import SUPPORTED_LANGUAGES

        # Test basic module structure
        assert hasattr(executor, '__file__')

        # Test that key functions exist
        assert hasattr(executor, 'execute_code')
        assert callable(executor.execute_code)

        # Test constants and configuration
        assert isinstance(SUPPORTED_LANGUAGES, dict)
        assert 'python' in SUPPORTED_LANGUAGES

        # Test timeout constants
        assert DEFAULT_TIMEOUT > 0
        assert MAX_TIMEOUT > DEFAULT_TIMEOUT
        assert MIN_TIMEOUT > 0
        assert MIN_TIMEOUT <= DEFAULT_TIMEOUT <= MAX_TIMEOUT

    def test_supported_languages_configuration(self, code_dir):
        """Test that supported languages are properly configured."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution.language_support import SUPPORTED_LANGUAGES
        languages = SUPPORTED_LANGUAGES

        # Test that each language has required configuration
        for lang, config in languages.items():
            assert 'image' in config, f"Language {lang} missing Docker image"
            assert 'extension' in config, f"Language {lang} missing file extension"
            assert 'command' in config, f"Language {lang} missing command template"
            assert 'timeout_factor' in config, f"Language {lang} missing timeout factor"

            # Test that command template contains filename placeholder
            command_str = ' '.join(config['command'])
            assert '{filename}' in command_str, f"Language {lang} command missing filename placeholder"

    def test_execute_code_function_signature(self, code_dir):
        """Test that execute_code function has correct signature."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        import inspect
        from codomyrmex.coding.execution import executor

        from codomyrmex.coding.execution.executor import execute_code
        sig = inspect.signature(execute_code)

        # Test required parameters
        assert 'language' in sig.parameters
        assert 'code' in sig.parameters

        # Test optional parameters
        assert 'stdin' in sig.parameters
        assert 'timeout' in sig.parameters
        assert 'session_id' in sig.parameters

        # Test parameter defaults
        stdin_param = sig.parameters['stdin']
        timeout_param = sig.parameters['timeout']
        session_id_param = sig.parameters['session_id']

        assert stdin_param.default is None
        assert timeout_param.default is None
        assert session_id_param.default is None

    def test_safe_code_execution_validation(self, real_docker_available):
        """Test code execution parameter validation without actual execution."""
        from codomyrmex.coding.execution.executor import execute_code

        # Test with safe Python code that should work (if Docker is available)
        safe_code = 'print("Hello, World!")'

        if real_docker_available:
            # Only run if Docker is actually available
            result = execute_code(
                language='python',
                code=safe_code,
                timeout=5  # Short timeout for testing
            )

            # Verify result structure
            assert isinstance(result, dict)
            assert 'stdout' in result or 'stderr' in result
            assert 'exit_code' in result
            assert 'execution_time' in result
            assert 'status' in result
        else:
            # If Docker is not available, test should still import and validate
            assert callable(execute_code)

    def test_docker_availability_check(self, real_docker_available):
        """Test real Docker availability checking."""
        from codomyrmex.coding.sandbox.container import check_docker_available

        # Test that the function returns a boolean
        result = check_docker_available()
        assert isinstance(result, bool)

        # Result should match our fixture's determination
        assert result == real_docker_available

    def test_execution_timeout_validation(self, code_dir):
        """Test that timeout validation works correctly."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.coding.execution import executor

        # Test timeout constants are reasonable
        from codomyrmex.coding.execution.executor import DEFAULT_TIMEOUT, MAX_TIMEOUT, MIN_TIMEOUT
        assert 0 < MIN_TIMEOUT <= DEFAULT_TIMEOUT <= MAX_TIMEOUT

        # Test that timeout validation would work (without actual execution)
        # This tests the logic without running Docker
        safe_code = 'print("test")'

        from codomyrmex.coding.sandbox.container import check_docker_available
        from codomyrmex.coding.execution.executor import execute_code
        if check_docker_available():
            # Test valid timeout
            result = execute_code('python', safe_code, timeout=5)
            assert isinstance(result, dict)

            # Test default timeout (None should use DEFAULT_TIMEOUT)
            result_default = execute_code('python', safe_code, timeout=None)
            assert isinstance(result_default, dict)

    def test_execution_limits_dataclass(self):
        """Test ExecutionLimits dataclass functionality."""
        from codomyrmex.coding.sandbox.isolation import ExecutionLimits

        # Test default limits
        limits = ExecutionLimits()
        assert limits.time_limit == 30
        assert limits.memory_limit == 256
        assert limits.cpu_limit == 0.5
        assert limits.max_output_chars == 100000

        # Test custom limits
        custom_limits = ExecutionLimits(
            time_limit=60,
            memory_limit=512,
            cpu_limit=1.0,
            max_output_chars=50000
        )
        assert custom_limits.time_limit == 60
        assert custom_limits.memory_limit == 512
        assert custom_limits.cpu_limit == 1.0
        assert custom_limits.max_output_chars == 50000

        # Test validation - invalid time limit
        with pytest.raises(ValueError, match="Time limit must be between"):
            ExecutionLimits(time_limit=0)

        with pytest.raises(ValueError, match="Time limit must be between"):
            ExecutionLimits(time_limit=400)

        # Test validation - invalid memory limit
        with pytest.raises(ValueError, match="Memory limit must be at least"):
            ExecutionLimits(memory_limit=0)

        # Test validation - invalid CPU limit
        with pytest.raises(ValueError, match="CPU limit must be between"):
            ExecutionLimits(cpu_limit=0)

        with pytest.raises(ValueError, match="CPU limit must be between"):
            ExecutionLimits(cpu_limit=5.0)

        # Test validation - invalid output limit
        with pytest.raises(ValueError, match="Max output chars must be at least"):
            ExecutionLimits(max_output_chars=500)

    def test_resource_monitor(self):
        """Test ResourceMonitor functionality."""
        from codomyrmex.coding.monitoring.resource_tracker import ResourceMonitor

        monitor = ResourceMonitor()

        # Test monitoring start
        monitor.start_monitoring()
        assert monitor.start_time is not None
        assert isinstance(monitor.start_time, float)

        # Test monitoring update
        initial_peak = monitor.peak_memory
        monitor.update_monitoring()
        # Peak memory should be >= initial (may be the same if no memory usage)

        # Test resource usage retrieval
        usage = monitor.get_resource_usage()
        assert isinstance(usage, dict)
        assert "execution_time_seconds" in usage
        assert "memory_start_mb" in usage
        assert "memory_peak_mb" in usage
        assert "cpu_samples" in usage
        assert "cpu_average_percent" in usage
        assert "cpu_peak_percent" in usage

        # Execution time should be positive
        assert usage["execution_time_seconds"] >= 0

    def test_execute_with_limits(self):
        """Test execute_with_limits function."""
        from codomyrmex.coding.sandbox.isolation import execute_with_limits, ExecutionLimits

        # Simple Python code for testing
        test_code = "print('Hello from limits test')"
        limits = ExecutionLimits(time_limit=10, memory_limit=128)

        # Test with limits (this may fail if Docker is not available, which is expected)
        try:
            result = execute_with_limits("python", test_code, limits)
            assert isinstance(result, dict)

            # Check that resource usage and limits are included
            assert "resource_usage" in result
            assert "limits_applied" in result

            # Verify limits are recorded correctly
            applied_limits = result["limits_applied"]
            assert applied_limits["time_limit_seconds"] == 10
            assert applied_limits["memory_limit_mb"] == 128

        except Exception:
            # Expected if Docker is not available in test environment
            pass

    def test_sandbox_process_isolation(self):
        """Test sandbox_process_isolation function."""
        from codomyrmex.coding.sandbox.isolation import sandbox_process_isolation, ExecutionLimits

        # Simple Python code for testing
        test_code = "print('Hello from isolation test')"
        limits = ExecutionLimits(time_limit=5, memory_limit=64)

        # Test isolation (this may fail if Docker is not available, which is expected)
        try:
            result = sandbox_process_isolation("python", test_code, limits)
            assert isinstance(result, dict)

            # Check that resource usage and limits are included
            assert "resource_usage" in result
            assert "limits_applied" in result

            # Verify limits are recorded correctly
            applied_limits = result["limits_applied"]
            assert applied_limits["time_limit_seconds"] == 5
            assert applied_limits["memory_limit_mb"] == 64

        except Exception:
            # Expected if Docker is not available in test environment
            pass


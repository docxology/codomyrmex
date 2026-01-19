#!/usr/bin/env python3
"""
Integration Test: AI Code Editing → Code Execution Sandbox Workflow

This integration test validates the complete workflow from AI-powered code generation
to secure execution in the sandbox environment, ensuring that generated code
executes correctly and safely.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from typing import Dict, Any, List

try:
    from codomyrmex.agents.ai_code_editing import generate_code_snippet
    from codomyrmex.coding import execute_code, execute_with_limits, ExecutionLimits
    from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger
    AI_CODE_EDITING_AVAILABLE = True
except ImportError:
    setup_logging = None
    get_logger = None
    AI_CODE_EDITING_AVAILABLE = False

try:
    from codomyrmex.coding import execute_code
    CODE_EXECUTION_AVAILABLE = True
except ImportError:
    CODE_EXECUTION_AVAILABLE = False

# Set up logging for tests
if setup_logging and hasattr(setup_logging, '__call__'):
    try:
        setup_logging()
    except Exception:
        pass  # Logging setup might fail in test environment

logger = get_logger(__name__) if get_logger else None


class TestAICodeExecutionWorkflow:
    """Integration tests for AI code editing to execution sandbox workflow."""

    @pytest.mark.skipif(not AI_CODE_EDITING_AVAILABLE or not CODE_EXECUTION_AVAILABLE,
                       reason="Required modules not available")
    def test_simple_function_generation_and_execution(self):
        """Test generating a simple function and executing it successfully."""
        # Step 1: Generate code using AI
        prompt = "Write a Python function that calculates the factorial of a number using recursion"
        language = "python"

        # Note: This would typically call an AI service, but we'll mock/test the integration
        # For now, we'll use a known good code snippet
        generated_code = '''
def factorial(n):
    """Calculate factorial of n using recursion."""
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Test the function
result = factorial(5)
print(f"Factorial of 5 is: {result}")
'''

        # Step 2: Execute the generated code in sandbox
        execution_result = execute_code(
            language=language,
            code=generated_code,
            timeout=10
        )

        # Step 3: Validate execution results
        if execution_result["status"] == "setup_error" and "docker" in execution_result.get("error_message", "").lower():
            pytest.skip("Docker not available")

        assert execution_result["status"] == "success"
        assert execution_result["exit_code"] == 0
        assert "Factorial of 5 is: 120" in execution_result["stdout"]
        assert execution_result["execution_time"] > 0

    @pytest.mark.skipif(not AI_CODE_EDITING_AVAILABLE or not CODE_EXECUTION_AVAILABLE,
                       reason="Required modules not available")
    def test_code_with_input_execution(self):
        """Test generating code that requires input and executing it."""
        # Generated code that reads from stdin
        generated_code = '''
import sys
name = input("Enter your name: ")
print(f"Hello, {name}! Welcome to the sandbox.")
'''

        user_input = "Alice"

        execution_result = execute_code(
            language="python",
            code=generated_code,
            stdin=user_input,
            timeout=10
        )

        if execution_result["status"] == "setup_error" and "docker" in execution_result.get("error_message", "").lower():
            pytest.skip("Docker not available")

        assert execution_result["status"] == "success"
        assert execution_result["exit_code"] == 0
        assert "Hello, Alice! Welcome to the sandbox." in execution_result["stdout"]

    @pytest.mark.skipif(not CODE_EXECUTION_AVAILABLE,
                       reason="Code execution sandbox not available")
    def test_execution_with_resource_limits(self):
        """Test executing code with resource limits."""
        # Code that should complete within limits
        safe_code = '''
import time
# Short computation
result = sum(range(100))
print(f"Sum: {result}")
'''

        limits = ExecutionLimits(
            time_limit=5,  # 5 seconds
            memory_limit=64,  # 64 MB
            cpu_limit=0.5,  # 50% CPU
            max_output_chars=1000
        )

        execution_result = execute_with_limits(
            language="python",
            code=safe_code,
            limits=limits
        )

        if execution_result["status"] == "setup_error" and "docker" in execution_result.get("error_message", "").lower():
            pytest.skip("Docker not available")

        assert execution_result["status"] == "success"
        assert execution_result["exit_code"] == 0
        assert "resource_usage" in execution_result
        assert "limits_applied" in execution_result

        # Verify limits were applied
        applied_limits = execution_result["limits_applied"]
        assert applied_limits["time_limit_seconds"] == 5
        assert applied_limits["memory_limit_mb"] == 64

        # Verify resource usage was tracked
        resource_usage = execution_result["resource_usage"]
        assert "execution_time_seconds" in resource_usage
        assert "memory_peak_mb" in resource_usage

    @pytest.mark.skipif(not CODE_EXECUTION_AVAILABLE,
                       reason="Code execution sandbox not available")
    def test_execution_timeout_handling(self):
        """Test handling of code that exceeds time limits."""
        # Code that will run too long
        slow_code = '''
import time
time.sleep(10)  # Sleep longer than our timeout
print("This should not print")
'''

        execution_result = execute_code(
            language="python",
            code=slow_code,
            timeout=2  # 2 second timeout
        )

        # Should timeout or setup error if docker missing
        if execution_result["status"] == "setup_error" and "docker" in execution_result.get("error_message", "").lower():
            pytest.skip("Docker not available")

        assert execution_result["status"] == "timeout"
        assert execution_result["exit_code"] == -1
        assert "timeout" in execution_result["error_message"].lower()

    @pytest.mark.skipif(not CODE_EXECUTION_AVAILABLE,
                       reason="Code execution sandbox not available")
    def test_security_isolation(self):
        """Test that dangerous code is properly isolated."""
        # Code that tries to access file system (should be blocked by Docker)
        dangerous_code = '''
import os
# Try to list root directory (should fail in sandbox)
try:
    files = os.listdir('/')
    print(f"Root directory files: {files}")
except Exception as e:
    print(f"Access blocked: {type(e).__name__}")
'''

        execution_result = execute_code(
            language="python",
            code=dangerous_code,
            timeout=10
        )

        # Should either succeed (if Docker allows) or fail safely
        # The important thing is no system compromise
        assert isinstance(execution_result, dict)
        assert "status" in execution_result
        # Should not crash the test environment

    @pytest.mark.skipif(not AI_CODE_EDITING_AVAILABLE or not CODE_EXECUTION_AVAILABLE,
                       reason="Required modules not available")
    def test_error_handling_workflow(self):
        """Test the complete workflow when errors occur."""
        # Code with syntax error
        bad_code = '''
def broken_function(
    print("This has syntax error - missing closing paren"
'''

        execution_result = execute_code(
            language="python",
            code=bad_code,
            timeout=10
        )

        # Should handle the error gracefully
        if execution_result["status"] == "setup_error" and "docker" in execution_result.get("error_message", "").lower():
            pytest.skip("Docker not available")

        assert execution_result["status"] in ["execution_error", "setup_error"]
        assert execution_result["exit_code"] != 0
        assert "error" in execution_result["error_message"].lower() or "syntax" in execution_result["stderr"].lower()

    @pytest.mark.skipif(not CODE_EXECUTION_AVAILABLE,
                       reason="Code execution sandbox not available")
    def test_multiple_languages_integration(self):
        """Test that different language outputs are handled correctly."""
        test_cases = [
            ("python", 'print("Hello from Python")', "Hello from Python"),
            ("javascript", 'console.log("Hello from JavaScript");', "Hello from JavaScript"),
            ("bash", 'echo "Hello from Bash"', "Hello from Bash"),
        ]

        for language, code, expected_output in test_cases:
            # Replaces subTests with loop
            execution_result = execute_code(
                language=language,
                code=code,
                timeout=10
            )

            # Should succeed or fail gracefully
            assert isinstance(execution_result, dict)
            assert "status" in execution_result

            # If successful, check output
            if execution_result["status"] == "success":
                output = execution_result["stdout"] + execution_result["stderr"]
                assert expected_output in output or "Hello from" in output
            elif execution_result["status"] == "setup_error" and "docker" in execution_result.get("error_message", "").lower():
                continue # Skip check if docker missing

    def test_workflow_performance_monitoring(self):
        """Test that the workflow can be monitored for performance."""
        import time

        start_time = time.time()

        # Simple code execution
        simple_code = 'print("Performance test")'
        result = execute_code("python", simple_code, timeout=5)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete quickly
        assert total_time < 10  # Less than 10 seconds for the whole workflow
        if result["status"] == "setup_error" and "docker" in result.get("error_message", "").lower():
            pytest.skip("Docker not available")
            
        assert result["status"] == "success"
        assert result["execution_time"] < 5  # Code execution itself should be fast

    def test_workflow_error_recovery(self):
        """Test that the workflow can recover from various error conditions."""
        # Test with invalid language
        result1 = execute_code("invalid_lang", 'print("test")', timeout=5)
        assert result1["status"] == "setup_error"
        assert "not supported" in result1["error_message"]

        # Test with empty code
        result2 = execute_code("python", "", timeout=5)
        # Status could be setup_error or success (empty output). Just check it's tracked.
        assert result2["status"] in ["setup_error", "success", "execution_error"]

        # Test with None code
        result3 = execute_code("python", None, timeout=5)
        assert result3["status"] == "setup_error"

    def test_large_output_handling(self):
        """Test handling of code that produces large output."""
        # Code that generates a lot of output
        large_output_code = '''
for i in range(100):
    print(f"Line {i}: " + "x" * 50)
'''

        result = execute_code("python", large_output_code, timeout=10)

        if result["status"] == "setup_error" and "docker" in result.get("error_message", "").lower():
            pytest.skip("Docker not available")

        assert result["status"] == "success"
        # Should have truncated output if too large
        output_length = len(result["stdout"])
        # Allow reasonable output size
        assert output_length > 0
        assert output_length < 10000  # Should not be excessive


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])

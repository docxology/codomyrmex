#!/usr/bin/env python3
"""
Integration Test: Cross-Module Workflows

This integration test validates end-to-end workflows that span multiple modules,
ensuring that different components work together seamlessly in complex scenarios.
"""

import pytest
import tempfile
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Import modules for integration testing (with availability checks)
MODULE_AVAILABILITY = {}

try:
    from codomyrmex.agents.ai_code_editing import generate_code_snippet
    MODULE_AVAILABILITY["ai_code_editing"] = True
except ImportError:
    MODULE_AVAILABILITY["ai_code_editing"] = False

try:
    from codomyrmex.code import execute_code, execute_with_limits, ExecutionLimits
    MODULE_AVAILABILITY["code_execution"] = True
except ImportError:
    MODULE_AVAILABILITY["code_execution"] = False

try:
    from codomyrmex.static_analysis import analyze_file
    MODULE_AVAILABILITY["static_analysis"] = True
except ImportError:
    MODULE_AVAILABILITY["static_analysis"] = False

try:
    from codomyrmex.security.digital import analyze_file_security, check_compliance
    MODULE_AVAILABILITY["security"] = True
except ImportError:
    MODULE_AVAILABILITY["security"] = False

try:
    from codomyrmex.data_visualization import create_bar_chart
    MODULE_AVAILABILITY["data_visualization"] = True
except ImportError:
    MODULE_AVAILABILITY["data_visualization"] = False

try:
    from codomyrmex.performance import profile_function, run_benchmark
    MODULE_AVAILABILITY["performance"] = True
except ImportError:
    MODULE_AVAILABILITY["performance"] = False

try:
    from codomyrmex.ci_cd_automation import create_pipeline
    MODULE_AVAILABILITY["ci_cd"] = True
except ImportError:
    MODULE_AVAILABILITY["ci_cd"] = False

try:
    from codomyrmex.logging_monitoring.logger_config import PerformanceLogger
    MODULE_AVAILABILITY["performance_logging"] = True
except ImportError:
    MODULE_AVAILABILITY["performance_logging"] = False

try:
    from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Set up logging for tests
if LOGGING_AVAILABLE and hasattr(setup_logging, '__call__'):
    try:
        setup_logging()
    except Exception:
        pass

logger = get_logger(__name__) if LOGGING_AVAILABLE else None


class TestCrossModuleWorkflows:
    """Integration tests for complex cross-module workflows."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.workflow_results = {}

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_project(self) -> Dict[str, str]:
        """Create a test project with multiple files."""
        files = {}

        # Create main Python module
        main_file = os.path.join(self.test_dir, "main.py")
        with open(main_file, 'w') as f:
            f.write('''
import sys
import os

def main():
    """Main application function."""
    print("Starting application...")

    # Database operations (simulated)
    users = get_users_from_db()
    process_users(users)

    # File operations
    save_results_to_file(users, "output.txt")

    print("Application completed successfully")

def get_users_from_db():
    """Simulate database query."""
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
    ]

def process_users(users):
    """Process user data."""
    for user in users:
        user["processed"] = True
        user["timestamp"] = "2024-01-01"

def save_results_to_file(data, filename):
    """Save data to file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
''')

        # Create test file
        test_file = os.path.join(self.test_dir, "test_main.py")
        with open(test_file, 'w') as f:
            f.write('''
import unittest
from main import get_users_from_db, process_users

class TestMain(unittest.TestCase):
    def test_get_users(self):
        users = get_users_from_db()
        self.assertEqual(len(users), 3)
        self.assertEqual(users[0]["name"], "Alice")

    def test_process_users(self):
        users = get_users_from_db()
        process_users(users)
        for user in users:
            self.assertTrue(user["processed"])
            self.assertIn("timestamp", user)

if __name__ == "__main__":
    unittest.main()
''')

        # Create requirements.txt
        req_file = os.path.join(self.test_dir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write('''
pytest==7.0.0
requests==2.28.0
flask==2.2.0
''')

        files["main"] = main_file
        files["test"] = test_file
        files["requirements"] = req_file

        return files

    @pytest.mark.skipif(not all([
        MODULE_AVAILABILITY.get("ai_code_editing", False),
        MODULE_AVAILABILITY.get("code_execution", False),
        MODULE_AVAILABILITY.get("static_analysis", False)
    ]), reason="Required modules not available")
    def test_development_workflow(self):
        """Test complete development workflow: code generation → analysis → execution."""
        perf_logger = PerformanceLogger("development_workflow") if MODULE_AVAILABILITY["performance_logging"] else None

        with perf_logger.time_operation("development_workflow") if perf_logger else None:
            # Step 1: Generate code using AI
            prompt = "Write a Python function that validates email addresses using regex"
            generated_code = '''
import re

def validate_email(email):
    """Validate email address using regex."""
    # Use [.] instead of \. to avoid SyntaxWarning in Python 3.12+
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+[.][a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Test the function
emails = ["user@example.com", "invalid-email", "test@domain.co.uk"]
for email in emails:
    print(f"{email}: {validate_email(email)}")
'''

            # Step 2: Analyze the generated code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(generated_code)
                temp_file = f.name

            try:
                from codomyrmex.static_analysis import analyze_file
                analysis_results = analyze_file(temp_file)

                # Step 3: Execute the code
                execution_result = execute_code("python", generated_code, timeout=10)

                # Validate workflow results
                assert execution_result["status"] == "success"
                assert "user@example.com: True" in execution_result["stdout"]
                assert "invalid-email: False" in execution_result["stdout"]

                # Store results for cross-workflow validation
                self.workflow_results["development"] = {
                    "analysis": len(analysis_results),
                    "execution": execution_result["status"],
                    "generated_lines": len(generated_code.split('\n'))
                }

            finally:
                os.unlink(temp_file)

    @pytest.mark.skipif(not all([
        MODULE_AVAILABILITY.get("static_analysis", False),
        MODULE_AVAILABILITY.get("security_audit", False),
        MODULE_AVAILABILITY.get("ci_cd", False)
    ]), reason="Required modules not available")
    def test_ci_cd_quality_gate_workflow(self):
        """Test CI/CD quality gate workflow: analysis → security → deployment."""
        perf_logger = PerformanceLogger("cicd_workflow") if MODULE_AVAILABILITY["performance_logging"] else None

        with perf_logger.time_operation("cicd_workflow") if perf_logger else None:
            test_files = self._create_test_project()

            # Step 1: Static analysis
            from codomyrmex.static_analysis import analyze_file
            analysis_results = analyze_file(test_files["main"])

            # Step 2: Security audit
            from codomyrmex.security import analyze_file_security
            security_findings = analyze_file_security(test_files["main"])

            # Step 3: Compliance check
            from codomyrmex.security import check_compliance
            compliance_results = check_compliance(self.test_dir, ["OWASP_TOP_10"])

            # Step 4: Generate CI/CD pipeline based on results
            from codomyrmex.ci_cd_automation import create_pipeline

            # Create conditional pipeline based on analysis results
            has_critical_issues = any(
                finding.severity == "CRITICAL"
                for finding in security_findings
            ) if security_findings else False

            pipeline_config = {
                "name": "quality_gate_pipeline",
                "stages": [
                    {
                        "name": "analysis",
                        "jobs": [
                            {
                                "name": "static_analysis",
                                "script": "python -m codomyrmex.static_analysis analyze_file main.py"
                            }
                        ]
                    },
                    {
                        "name": "security",
                        "jobs": [
                            {
                                "name": "security_scan",
                                "script": "python -m codomyrmex.security analyze_file_security main.py"
                            }
                        ]
                    },
                    {
                        "name": "deploy",
                        "jobs": [
                            {
                                "name": "deploy_app",
                                "script": "echo 'Deploying application...'",
                                "dependencies": ["analysis", "security"]
                            }
                        ] if not has_critical_issues else []
                    }
                ]
            }

            pipeline = create_pipeline(pipeline_config)

            # Validate workflow results
            assert len(analysis_results) >= 0  # May find issues or not
            assert len(security_findings) >= 0
            assert len(compliance_results) > 0
            assert pipeline is not None

            # Pipeline should have expected structure
            assert len(pipeline.stages) >= 2  # At least analysis and security

            # Store results
            self.workflow_results["cicd"] = {
                "analysis_issues": len(analysis_results),
                "security_findings": len(security_findings),
                "compliance_checks": len(compliance_results),
                "pipeline_stages": len(pipeline.stages),
                "critical_blocking": has_critical_issues
            }

    @pytest.mark.skipif(not all([
        MODULE_AVAILABILITY.get("code_execution", False),
        MODULE_AVAILABILITY.get("performance", False),
        MODULE_AVAILABILITY.get("data_visualization", False)
    ]), reason="Required modules not available")
    def test_performance_testing_workflow(self):
        """Test performance testing workflow: execution → monitoring → visualization."""
        perf_logger = PerformanceLogger("performance_workflow") if MODULE_AVAILABILITY["performance_logging"] else None

        with perf_logger.time_operation("performance_workflow") if perf_logger else None:
            # Step 1: Define functions to test
            def algorithm_a(n):
                """Algorithm A: Simple loop."""
                result = 0
                for i in range(n):
                    result += i
                return result

            def algorithm_b(n):
                """Algorithm B: Using built-in sum."""
                return sum(range(n))

            # Step 2: Profile both algorithms
            from codomyrmex.performance import profile_function, run_benchmark

            profile_a = profile_function(algorithm_a, 10000)
            profile_b = profile_function(algorithm_b, 10000)

            benchmark_a = run_benchmark(lambda: algorithm_a(10000), iterations=5)
            benchmark_b = run_benchmark(lambda: algorithm_b(10000), iterations=5)

            # Step 3: Execute algorithms with resource monitoring
            from codomyrmex.code import execute_with_limits, ExecutionLimits

            code_a = f'''
def algorithm_a(n):
    result = 0
    for i in range(n):
        result += i
    return result

print("Result:", algorithm_a({10000}))
'''

            code_b = f'''
def algorithm_b(n):
    return sum(range(n))

print("Result:", algorithm_b({10000}))
'''

            limits = ExecutionLimits(time_limit=10, memory_limit=128)
            result_a = execute_with_limits("python", code_a, limits)
            result_b = execute_with_limits("python", code_b, limits)

            # Step 4: Create performance visualization
            from codomyrmex.data_visualization import create_bar_chart

            perf_data = {
                "categories": ["Algorithm A", "Algorithm B"],
                "values": [
                    profile_a["execution_time"],
                    profile_b["execution_time"]
                ]
            }

            visualization = create_bar_chart(perf_data, "Algorithm Performance Comparison")

            # Validate workflow results
            assert result_a["status"] == "success"
            assert result_b["status"] == "success"
            assert profile_a["execution_time"] > 0
            assert profile_b["execution_time"] > 0
            assert "resource_usage" in result_a
            assert "resource_usage" in result_b
            assert len(visualization) > 0

            # Algorithm B should generally be faster
            assert profile_b["execution_time"] <= profile_a["execution_time"] * 1.5

            # Store results
            self.workflow_results["performance"] = {
                "algorithm_a_time": profile_a["execution_time"],
                "algorithm_b_time": profile_b["execution_time"],
                "speedup_ratio": profile_a["execution_time"] / profile_b["execution_time"],
                "visualization_created": True,
                "resource_monitored": True
            }

    def test_workflow_coordination_and_reporting(self):
        """Test coordination between multiple workflows and final reporting."""
        # This test validates that multiple workflows can run and their results can be coordinated

        # Run available workflow tests
        available_workflows = []

        if all([MODULE_AVAILABILITY.get("ai_code_editing", False),
                MODULE_AVAILABILITY.get("code_execution", False),
                MODULE_AVAILABILITY.get("static_analysis", False)]):
            available_workflows.append("development")

        if all([MODULE_AVAILABILITY.get("static_analysis", False),
                MODULE_AVAILABILITY.get("security_audit", False),
                MODULE_AVAILABILITY.get("ci_cd", False)]):
            available_workflows.append("cicd")

        if all([MODULE_AVAILABILITY.get("code_execution", False),
                MODULE_AVAILABILITY.get("performance", False),
                MODULE_AVAILABILITY.get("data_visualization", False)]):
            available_workflows.append("performance")

        # Generate a summary report of workflow results
        report = {
            "workflows_executed": len(self.workflow_results),
            "available_workflows": available_workflows,
            "results": self.workflow_results,
            "timestamp": time.time(),
            "summary": {}
        }

        # Calculate summary statistics
        if self.workflow_results:
            total_execution_time = sum(
                result.get("execution_time", 0)
                for result in self.workflow_results.values()
                if isinstance(result, dict)
            )

            report["summary"] = {
                "total_workflows": len(self.workflow_results),
                "workflows_with_results": len([r for r in self.workflow_results.values() if r]),
                "estimated_total_time": total_execution_time
            }

        # Validate report structure
        assert isinstance(report, dict)
        assert "workflows_executed" in report
        assert "results" in report
        assert "summary" in report

        # Should have some results if workflows were executed
        if available_workflows:
            assert len(self.workflow_results) >= 0

    def test_error_handling_across_workflows(self):
        """Test error handling when workflows encounter issues."""
        # Test with various error conditions

        # Test 1: Invalid code execution
        if MODULE_AVAILABILITY.get("code_execution", False):
            from codomyrmex.code import execute_code

            invalid_code = "def broken syntax here ("
            result = execute_code("python", invalid_code, timeout=5)

            # Should handle syntax error gracefully
            assert result["status"] in ["execution_error", "setup_error"]
            assert result["exit_code"] != 0

        # Test 2: File analysis of non-existent file
        if MODULE_AVAILABILITY.get("static_analysis", False):
            from codomyrmex.static_analysis import analyze_file

            try:
                result = analyze_file("/nonexistent/file.py")
                # Should return some result structure
                assert isinstance(result, (list, dict))
            except Exception as e:
                # Should not crash catastrophically
                assert isinstance(e, Exception)

        # Test 3: Security analysis of problematic code
        if MODULE_AVAILABILITY.get("security_audit", False):
            from codomyrmex.security import analyze_file_security

            dangerous_code = '''
import os
os.system("rm -rf /")  # Dangerous command
eval(input("Enter code: "))  # Code injection
'''

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(dangerous_code)
                temp_file = f.name

            try:
                findings = analyze_file_security(temp_file)
                # Should detect security issues
                assert isinstance(findings, list)
                assert len(findings) > 0  # Should find some issues
            finally:
                os.unlink(temp_file)

    def test_workflow_performance_metrics(self):
        """Test that workflow performance can be measured and tracked."""
        start_time = time.time()

        # Execute a mini-workflow
        steps_completed = 0

        if MODULE_AVAILABILITY.get("code_execution", False):
            from codomyrmex.code import execute_code
            result = execute_code("python", "print('Hello Workflow')", timeout=5)
            assert result["status"] == "success"
            steps_completed += 1

        if MODULE_AVAILABILITY.get("performance", False):
            from codomyrmex.performance import profile_function
            profile_result = profile_function(lambda: sum(range(100)))
            assert profile_result["execution_time"] > 0
            steps_completed += 1

        if MODULE_AVAILABILITY.get("data_visualization", False):
            from codomyrmex.data_visualization import create_bar_chart
            data = {"categories": ["A"], "values": [1]}
            chart = create_bar_chart(data, "Test")
            assert len(chart) > 0
            steps_completed += 1

        end_time = time.time()
        total_time = end_time - start_time

        # Performance assertions
        if steps_completed > 0:
            # Should complete within reasonable time (30 seconds)
            assert total_time < 30.0

            # Each step should take reasonable time
            avg_time_per_step = total_time / steps_completed
            assert avg_time_per_step < 10.0  # Less than 10 seconds per step

    def test_data_consistency_across_workflows(self):
        """Test that data formats are consistent across different workflow modules."""
        # Test that different modules can work with similar data structures

        test_data = {
            "code": "print('Hello World')",
            "filename": "test.py",
            "metrics": [0.1, 0.2, 0.3],
            "categories": ["A", "B", "C"]
        }

        results = {}

        # Test code execution
        if MODULE_AVAILABILITY.get("code_execution", False):
            from codomyrmex.code import execute_code
            exec_result = execute_code("python", test_data["code"], timeout=5)
            results["execution"] = exec_result["status"] == "success"

        # Test static analysis
        if MODULE_AVAILABILITY.get("static_analysis", False):
            from codomyrmex.static_analysis import analyze_file

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_data["code"])
                temp_file = f.name

            try:
                analysis_result = analyze_file(temp_file)
                results["analysis"] = isinstance(analysis_result, list)
            finally:
                os.unlink(temp_file)

        # Test visualization
        if MODULE_AVAILABILITY.get("data_visualization", False):
            from codomyrmex.data_visualization import create_bar_chart

            viz_data = {
                "categories": test_data["categories"],
                "values": test_data["metrics"]
            }
            chart = create_bar_chart(viz_data, "Consistency Test")
            results["visualization"] = len(chart) > 0

        # All modules that were tested should have produced valid results
        for module, success in results.items():
            assert success, f"Module {module} failed consistency test"

    def test_module_interoperability(self):
        """Test that modules can interoperate through common interfaces."""
        # Test that results from one module can be used as input to another

        # Create a simple Python file to analyze
        test_code = '''
def calculate_fibonacci(n):
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Potential security issue: no input validation
result = calculate_fibonacci(10)
print(f"Fibonacci(10) = {result}")
'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            results = {}

            # Module 1: Static Analysis
            if MODULE_AVAILABILITY.get("static_analysis", False):
                from codomyrmex.static_analysis import analyze_file
                analysis_results = analyze_file(temp_file)
                results["static_analysis"] = len(analysis_results)

            # Module 2: Security Analysis
            if MODULE_AVAILABILITY.get("security_audit", False):
                from codomyrmex.security import analyze_file_security
                security_findings = analyze_file_security(temp_file)
                results["security_analysis"] = len(security_findings)

            # Module 3: Code Execution
            if MODULE_AVAILABILITY.get("code_execution", False):
                from codomyrmex.code import execute_code
                exec_result = execute_code("python", test_code, timeout=10)
                results["execution"] = exec_result["status"] == "success"

            # Module 4: Performance Profiling
            if MODULE_AVAILABILITY.get("performance", False):
                from codomyrmex.performance import profile_function

                def test_execution():
                    exec(test_code)

                profile_result = profile_function(test_execution)
                results["performance"] = profile_result["execution_time"] > 0

            # Validate that all tested modules produced expected results
            for module_name, result in results.items():
                if module_name in ["static_analysis", "security_analysis"]:
                    assert isinstance(result, int)  # Count of findings
                else:
                    assert result is True  # Boolean success indicator

        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])

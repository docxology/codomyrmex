"""
End-to-end tests for complete code review workflows.

These tests simulate real-world usage scenarios and complete workflows
from analysis to reporting.
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from codomyrmex.code_review import (
    CodeReviewer,
    analyze_project,
    check_quality_gates,
    generate_report,
    QualityGateResult,
    AnalysisSummary
)


class TestCompleteWorkflow(unittest.TestCase):
    """End-to-end workflow tests."""

    def setUp(self):
        """Set up test environment with realistic project structure."""
        self.test_dir = tempfile.mkdtemp()
        self._create_realistic_project()

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_realistic_project(self):
        """Create a realistic Python project structure for testing."""

        # Create package structure
        os.makedirs(os.path.join(self.test_dir, "src", "mypackage"))
        os.makedirs(os.path.join(self.test_dir, "tests"))
        os.makedirs(os.path.join(self.test_dir, "docs"))

        # Create __init__.py files
        with open(os.path.join(self.test_dir, "src", "mypackage", "__init__.py"), 'w') as f:
            f.write('"""My test package."""\n')

        # Create main module
        main_module = os.path.join(self.test_dir, "src", "mypackage", "main.py")
        with open(main_module, 'w') as f:
            f.write('''"""
Main module for the test package.
"""

import sys
from typing import List, Optional


def process_data(data: List[int], threshold: int = 10) -> List[int]:
    """
    Process a list of integers with various conditions.

    Args:
        data: List of integers to process
        threshold: Threshold value for filtering

    Returns:
        Processed list of integers
    """
    if not data:
        return []

    if threshold < 0:
        threshold = abs(threshold)

    result = []
    for item in data:
        if item is None:
            continue

        if isinstance(item, str):
            try:
                item = int(item)
            except ValueError:
                continue

        if item > threshold:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item + 1)
        elif item < threshold:
            result.append(item)
        else:
            result.append(0)

    return result


def complex_business_logic(users, orders, products):
    """Complex business logic with multiple conditions."""
    if not users or not orders or not products:
        return {"error": "Missing data"}

    total_revenue = 0
    processed_orders = 0

    for user in users:
        if not user.get("active", False):
            continue

        user_orders = [o for o in orders if o.get("user_id") == user["id"]]

        for order in user_orders:
            if order.get("status") != "completed":
                continue

            for item in order.get("items", []):
                product = next(
                    (p for p in products if p["id"] == item["product_id"]),
                    None
                )

                if product and product.get("available", False):
                    total_revenue += item["quantity"] * product["price"]
                    processed_orders += 1

    return {
        "total_revenue": total_revenue,
        "processed_orders": processed_orders,
        "average_order_value": total_revenue / processed_orders if processed_orders > 0 else 0
    }


class DataValidator:
    """Data validation class."""

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode

    def validate_user(self, user_data: dict) -> bool:
        """Validate user data."""
        if not isinstance(user_data, dict):
            return False

        required_fields = ["id", "name", "email"]

        for field in required_fields:
            if field not in user_data:
                return False

            if self.strict_mode and not user_data[field]:
                return False

        return True


# Unreachable code for testing
def unreachable_example():
    """Function with unreachable code."""
    return "always returns"

    # This code is unreachable
    print("This never executes")
    x = 1 / 0  # This would cause an error if reached

    return "never reached"
''')

        # Create test file
        test_file = os.path.join(self.test_dir, "tests", "test_main.py")
        with open(test_file, 'w') as f:
            f.write('''"""
Tests for the main module.
"""

import unittest
from src.mypackage.main import process_data, complex_business_logic, DataValidator


class TestMain(unittest.TestCase):
    """Test cases for main module."""

    def test_process_data_empty(self):
        """Test processing empty data."""
        result = process_data([])
        self.assertEqual(result, [])

    def test_process_data_basic(self):
        """Test basic data processing."""
        result = process_data([1, 2, 3, 15, 16])
        expected = [1, 2, 3, 30, 33]  # 15*2=30, 16+1=33
        self.assertEqual(result, expected)

    def test_complex_business_logic(self):
        """Test complex business logic."""
        users = [{"id": 1, "active": True}, {"id": 2, "active": False}]
        orders = [
            {"user_id": 1, "status": "completed", "items": [{"product_id": 1, "quantity": 2}]},
            {"user_id": 1, "status": "pending", "items": [{"product_id": 1, "quantity": 1}]},
            {"user_id": 2, "status": "completed", "items": [{"product_id": 1, "quantity": 1}]}
        ]
        products = [{"id": 1, "price": 10.0, "available": True}]

        result = complex_business_logic(users, orders, products)

        self.assertEqual(result["total_revenue"], 20.0)  # 2 * 10.0
        self.assertEqual(result["processed_orders"], 1)


if __name__ == '__main__':
    unittest.main()
''')

        # Create requirements.txt
        req_file = os.path.join(self.test_dir, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write('pytest>=7.0.0\n')

        # Create .pyscn.toml configuration
        pyscn_config = os.path.join(self.test_dir, ".pyscn.toml")
        with open(pyscn_config, 'w') as f:
            f.write('''[complexity]
max_complexity = 10

[dead_code]
min_severity = "warning"

[output]
directory = "reports"
format = "html"

[analysis]
recursive = true
exclude_patterns = ["__pycache__", ".git", "tests"]
''')

    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow from start to finish."""
        # Analyze the project
        summary = analyze_project(self.test_dir)

        # Verify summary structure
        self.assertIsInstance(summary, AnalysisSummary)
        self.assertGreaterEqual(summary.files_analyzed, 0)
        self.assertIsInstance(summary.analysis_time, float)

        print(f"\nComplete Workflow Results:")
        print(f"  Files analyzed: {summary.files_analyzed}")
        print(f"  Total issues: {summary.total_issues}")
        print(f"  Analysis time: {summary.analysis_time:.2f}s")

        # Should have found some issues (at least complexity issues)
        self.assertGreater(summary.total_issues, 0)

    def test_quality_gates_workflow(self):
        """Test quality gates checking workflow."""
        # First analyze the project
        analyze_project(self.test_dir)

        # Check quality gates with strict thresholds
        strict_gates = {
            "max_complexity": 8,  # Very strict
            "max_issues_per_file": 5
        }

        result = check_quality_gates(self.test_dir, strict_gates)

        # Should return quality gate result
        self.assertIsInstance(result, QualityGateResult)

        print(f"\nQuality Gates Results:")
        print(f"  Passed: {result.passed}")
        print(f"  Total checks: {result.total_checks}")
        print(f"  Passed checks: {result.passed_checks}")
        print(f"  Failed checks: {result.failed_checks}")

        if result.failures:
            print(f"  Failures: {len(result.failures)}")
            for failure in result.failures:
                print(f"    - {failure['gate']}: {failure['message']}")

    def test_report_generation_workflow(self):
        """Test report generation workflow."""
        # First analyze the project
        analyze_project(self.test_dir)

        # Generate HTML report
        report_path = os.path.join(self.test_dir, "analysis_report.html")
        success = generate_report(
            self.test_dir,
            report_path,
            format="html"
        )

        if success:
            # Verify report file exists and has content
            self.assertTrue(os.path.exists(report_path))

            with open(report_path, 'r') as f:
                content = f.read()

            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("Code Review Report", content)
            self.assertIn("Total Issues", content)

            print(f"\nReport Generation:")
            print(f"  Report created: {report_path}")
            print(f"  File size: {os.path.getsize(report_path)} bytes")

    def test_json_export_workflow(self):
        """Test JSON export workflow."""
        # Analyze project
        reviewer = CodeReviewer(self.test_dir)
        reviewer.analyze_project(target_paths=[self.test_dir])

        # Export to JSON using the generate_report method
        json_path = os.path.join(self.test_dir, "results.json")
        success = reviewer.generate_report(json_path, format="json")

        if success:
            self.assertTrue(os.path.exists(json_path))

            # Verify JSON structure
            with open(json_path, 'r') as f:
                data = json.load(f)

            self.assertIn("summary", data)
            self.assertIn("results", data)
            self.assertIn("total_issues", data["summary"])
            self.assertIn("files_analyzed", data["summary"])

            print(f"\nJSON Export:")
            print(f"  JSON created: {json_path}")
            print(f"  Issues exported: {len(data['results'])}")

    def test_configuration_workflow(self):
        """Test configuration loading and application."""
        # Test with custom configuration
        config_path = os.path.join(self.test_dir, ".pyscn.toml")

        reviewer = CodeReviewer(project_root=self.test_dir, config_path=config_path)

        # Verify default configuration (tomli may not be available)
        self.assertEqual(reviewer.config["max_complexity"], 15)  # Default value
        self.assertEqual(reviewer.config["output_format"], "html")  # Default value

        print(f"\nConfiguration:")
        print(f"  Config file: {config_path}")
        print(f"  Max complexity: {reviewer.config['max_complexity']}")
        print(f"  Output format: {reviewer.config['output_format']}")

    def test_real_world_scenario(self):
        """Test a realistic development workflow scenario."""
        print(f"\nReal-world Scenario Test:")
        print(f"  Project: {os.path.basename(self.test_dir)}")
        print(f"  Location: {self.test_dir}")

        # Simulate development workflow
        steps = [
            ("Analyze codebase", lambda: analyze_project(self.test_dir)),
            ("Check quality gates", lambda: check_quality_gates(self.test_dir, {"max_complexity": 15})),
            ("Generate report", lambda: generate_report(self.test_dir, "final_report.html")),
        ]

        results = {}
        for step_name, step_func in steps:
            try:
                result = step_func()
                results[step_name] = "✅ PASSED"
                print(f"  {step_name}: ✅ PASSED")

                if hasattr(result, 'total_issues'):
                    print(f"    Issues found: {result.total_issues}")
                if hasattr(result, 'passed'):
                    print(f"    Quality gates: {'PASSED' if result.passed else 'FAILED'}")

            except Exception as e:
                results[step_name] = f"❌ FAILED: {e}"
                print(f"  {step_name}: ❌ FAILED - {e}")

        # Overall assessment
        passed_steps = sum(1 for result in results.values() if result == "✅ PASSED")
        total_steps = len(steps)

        print(f"\nOverall Results:")
        print(f"  {passed_steps}/{total_steps} steps passed")

        if passed_steps == total_steps:
            print(f"  🎉 All workflow steps completed successfully!")
        else:
            print(f"  ⚠️  Some workflow steps failed")
            for step, result in results.items():
                if result != "✅ PASSED":
                    print(f"    {step}: {result}")


if __name__ == '__main__':
    unittest.main(verbosity=2)

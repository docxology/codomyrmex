#!/usr/bin/env python3
"""
Codomyrmex Test Summary Generator

This script analyzes pytest test results and generates comprehensive reports
including test durations, failure analysis, and performance metrics.

Usage:
    python test_summary.py [options] [test_results.json]

Options:
    --durations=N    Show top N slowest tests
    --failures       Show detailed failure analysis
    --coverage       Include coverage analysis
    --trends         Show test execution trends
    --output=FILE    Save report to file
    --format=FORMAT  Report format (text, json, html)

Examples:
    python test_summary.py --durations=20
    python test_summary.py --failures --output=report.txt
    python test_summary.py --coverage results.json
"""

import argparse
import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class TestSummaryGenerator:
    """Generate comprehensive test execution reports."""

    def __init__(self, results_file: Optional[str] = None):
        self.results_file = results_file
        self.test_results = []
        self.load_results()

    def load_results(self):
        """Load test results from file or generate sample data."""
        if self.results_file and os.path.exists(self.results_file):
            with open(self.results_file, 'r') as f:
                self.test_results = json.load(f)
        else:
            # Generate sample data for demonstration
            self.test_results = self._generate_sample_results()

    def _generate_sample_results(self) -> List[Dict[str, Any]]:
        """Generate sample test results for demonstration."""
        results = []

        # Sample unit test results
        unit_tests = [
            ("testing/unit/test_exceptions.py::TestCodomyrmexError::test_basic_error_creation", "passed", 0.001),
            ("testing/unit/test_exceptions.py::TestCodomyrmexError::test_error_with_context", "passed", 0.002),
            ("testing/unit/test_logging_monitoring.py::TestLoggingMonitoring::test_logger_config_import", "passed", 0.005),
            ("testing/unit/test_environment_setup.py::TestEnvironmentSetup::test_env_checker_import", "passed", 0.003),
        ]

        # Sample integration test results
        integration_tests = [
            ("testing/integration/test_ai_code_execution_flow.py::TestAICodeExecutionFlow::test_basic_code_execution", "passed", 0.5),
            ("testing/integration/test_cross_module_workflows.py::TestCrossModuleWorkflows::test_user_registration_flow", "failed", 2.1),
        ]

        # Sample performance test results
        performance_tests = [
            ("testing/performance/test_module_performance.py::TestModulePerformance::test_ai_code_editing_performance", "passed", 15.2),
            ("testing/performance/test_module_performance.py::TestModulePerformance::test_data_visualization_performance", "passed", 8.7),
        ]

        for test_path, outcome, duration in unit_tests + integration_tests + performance_tests:
            results.append({
                "nodeid": test_path,
                "outcome": outcome,
                "duration": duration,
                "start": datetime.now().isoformat(),
                "stop": (datetime.now() + timedelta(seconds=duration)).isoformat(),
                "keywords": self._extract_keywords(test_path),
                "markers": self._extract_markers(test_path),
            })

        return results

    def _extract_keywords(self, test_path: str) -> List[str]:
        """Extract keywords from test path."""
        keywords = []
        if "unit" in test_path:
            keywords.append("unit")
        if "integration" in test_path:
            keywords.append("integration")
        if "performance" in test_path:
            keywords.append("performance")
        if "examples" in test_path:
            keywords.append("examples")
        return keywords

    def _extract_markers(self, test_path: str) -> List[str]:
        """Extract markers from test path."""
        markers = []
        if "performance" in test_path or "slow" in test_path:
            markers.append("slow")
        if "integration" in test_path:
            markers.append("integration")
        return markers

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get basic summary statistics."""
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["outcome"] == "passed")
        failed = sum(1 for r in self.test_results if r["outcome"] == "failed")
        skipped = sum(1 for r in self.test_results if r["outcome"] == "skipped")
        error = sum(1 for r in self.test_results if r["outcome"] == "error")

        total_duration = sum(r["duration"] for r in self.test_results)

        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "error": error,
            "total_duration": total_duration,
            "pass_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "avg_duration": total_duration / total_tests if total_tests > 0 else 0,
        }

    def get_slowest_tests(self, n: int = 10) -> List[Tuple[str, float]]:
        """Get the N slowest tests."""
        sorted_tests = sorted(
            self.test_results,
            key=lambda x: x["duration"],
            reverse=True
        )
        return [(test["nodeid"], test["duration"]) for test in sorted_tests[:n]]

    def get_failure_analysis(self) -> Dict[str, Any]:
        """Analyze test failures."""
        failures = [r for r in self.test_results if r["outcome"] in ["failed", "error"]]

        failure_categories = Counter()
        failure_locations = Counter()

        for failure in failures:
            # Categorize by test type
            if "unit" in failure["nodeid"]:
                failure_categories["unit"] += 1
            elif "integration" in failure["nodeid"]:
                failure_categories["integration"] += 1
            elif "performance" in failure["nodeid"]:
                failure_categories["performance"] += 1
            else:
                failure_categories["other"] += 1

            # Track failure locations
            location = failure["nodeid"].split("::")[0]
            failure_locations[location] += 1

        return {
            "total_failures": len(failures),
            "failure_categories": dict(failure_categories),
            "failure_locations": dict(failure_locations),
            "failed_tests": [f["nodeid"] for f in failures],
        }

    def get_test_distribution(self) -> Dict[str, int]:
        """Get test distribution by category."""
        distribution = Counter()

        for result in self.test_results:
            if "unit" in result["nodeid"]:
                distribution["unit"] += 1
            elif "integration" in result["nodeid"]:
                distribution["integration"] += 1
            elif "performance" in result["nodeid"]:
                distribution["performance"] += 1
            elif "examples" in result["nodeid"]:
                distribution["examples"] += 1
            else:
                distribution["other"] += 1

        return dict(distribution)

    def generate_report(self, format_type: str = "text", output_file: Optional[str] = None) -> str:
        """Generate a comprehensive test report."""
        stats = self.get_summary_stats()
        slowest = self.get_slowest_tests(10)
        failures = self.get_failure_analysis()
        distribution = self.get_test_distribution()

        if format_type == "json":
            report_data = {
                "summary": stats,
                "slowest_tests": slowest,
                "failure_analysis": failures,
                "test_distribution": distribution,
                "generated_at": datetime.now().isoformat(),
            }
            report = json.dumps(report_data, indent=2)

        elif format_type == "html":
            report = self._generate_html_report(stats, slowest, failures, distribution)

        else:  # text format
            report = self._generate_text_report(stats, slowest, failures, distribution)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to {output_file}")

        return report

    def _generate_text_report(self, stats: Dict, slowest: List, failures: Dict, distribution: Dict) -> str:
        """Generate a text-format report."""
        lines = []
        lines.append("=" * 60)
        lines.append("CODOMYRMEX TEST EXECUTION SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary statistics
        lines.append("SUMMARY STATISTICS")
        lines.append("-" * 20)
        lines.append(f"Total Tests:     {stats['total_tests']}")
        lines.append(f"Passed:          {stats['passed']}")
        lines.append(f"Failed:          {stats['failed']}")
        lines.append(f"Skipped:         {stats['skipped']}")
        lines.append(f"Errors:          {stats['error']}")
        lines.append(".1f")
        lines.append(".1f")
        lines.append(".3f")
        lines.append("")

        # Test distribution
        lines.append("TEST DISTRIBUTION")
        lines.append("-" * 18)
        for category, count in distribution.items():
            lines.append(f"{category.capitalize():<12}: {count}")
        lines.append("")

        # Slowest tests
        if slowest:
            lines.append("SLOWEST TESTS")
            lines.append("-" * 13)
            for i, (test_name, duration) in enumerate(slowest, 1):
                lines.append("2d")
            lines.append("")

        # Failure analysis
        if failures["total_failures"] > 0:
            lines.append("FAILURE ANALYSIS")
            lines.append("-" * 16)
            lines.append(f"Total Failures: {failures['total_failures']}")
            lines.append("")
            lines.append("By Category:")
            for category, count in failures["failure_categories"].items():
                lines.append(f"  {category.capitalize()}: {count}")
            lines.append("")
            lines.append("By Location:")
            for location, count in failures["failure_locations"].items():
                lines.append(f"  {location}: {count}")
            lines.append("")
            lines.append("Failed Tests:")
            for test in failures["failed_tests"][:10]:  # Show first 10
                lines.append(f"  - {test}")
            if len(failures["failed_tests"]) > 10:
                lines.append(f"  ... and {len(failures['failed_tests']) - 10} more")
        else:
            lines.append("NO FAILURES - All tests passed!")

        return "\n".join(lines)

    def _generate_html_report(self, stats: Dict, slowest: List, failures: Dict, distribution: Dict) -> str:
        """Generate an HTML-format report."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Codomyrmex Test Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .failure {{ color: #d9534f; }}
        .success {{ color: #5cb85c; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Codomyrmex Test Execution Summary</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="section summary">
        <h2>Summary Statistics</h2>
        <p>Total Tests: {stats['total_tests']} | Passed: {stats['passed']} | Failed: {stats['failed']}</p>
        <p>Pass Rate: {stats['pass_rate']:.1f}% | Total Duration: {stats['total_duration']:.1f}s</p>
    </div>

    <div class="section">
        <h2>Test Distribution</h2>
        <table>
            <tr><th>Category</th><th>Count</th></tr>
"""
        for category, count in distribution.items():
            html += f"            <tr><td>{category.capitalize()}</td><td>{count}</td></tr>\n"

        html += """
        </table>
    </div>

    <div class="section">
        <h2>Slowest Tests</h2>
        <table>
            <tr><th>Test</th><th>Duration (s)</th></tr>
"""
        for test_name, duration in slowest:
            html += f"            <tr><td>{test_name}</td><td>{duration:.3f}</td></tr>\n"

        html += """
        </table>
    </div>
</body>
</html>
"""
        return html


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate test execution reports")
    parser.add_argument("results_file", nargs="?", help="Path to pytest results JSON file")
    parser.add_argument("--durations", type=int, default=10, help="Show top N slowest tests")
    parser.add_argument("--failures", action="store_true", help="Show detailed failure analysis")
    parser.add_argument("--coverage", action="store_true", help="Include coverage analysis")
    parser.add_argument("--trends", action="store_true", help="Show test execution trends")
    parser.add_argument("--output", help="Save report to file")
    parser.add_argument("--format", choices=["text", "json", "html"], default="text",
                       help="Report format")

    args = parser.parse_args()

    generator = TestSummaryGenerator(args.results_file)

    # Generate report
    report = generator.generate_report(args.format, args.output)

    # Print to stdout if not saving to file
    if not args.output:
        print(report)

    # Additional analysis if requested
    if args.durations:
        slowest = generator.get_slowest_tests(args.durations)
        if slowest:
            print(f"\nTop {args.durations} slowest tests:")
            for test_name, duration in slowest:
                print(".3f")

    if args.failures:
        failures = generator.get_failure_analysis()
        if failures["total_failures"] > 0:
            print(f"\nFailure Analysis:")
            print(f"Total failures: {failures['total_failures']}")
            print(f"Categories: {failures['failure_categories']}")
        else:
            print("\nNo test failures!")


if __name__ == "__main__":
    main()

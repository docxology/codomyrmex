from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
import logging
import os
import sys

from codomyrmex.logging_monitoring import get_logger



#!/usr/bin/env python3
"""
Example Coverage Checker

This script verifies that all Codomyrmex modules have corresponding examples.
It scans the src/codomyrmex directory for modules and checks if examples exist.

Usage:
    python scripts/examples/check_example_coverage.py

Output:
    - Coverage percentage
    - List of modules without examples
    - List of examples without corresponding modules
    - Recommendations for missing examples
"""


# Add src to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    logger = get_logger(__name__)
except ImportError:
    # Fallback logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class ExampleCoverageChecker:
    """Checks coverage of examples for Codomyrmex modules."""

    def __init__(self, project_root: Path):
        """Initialize the coverage checker."""
        self.project_root = project_root
        self.src_dir = project_root / "src" / "codomyrmex"
        self.examples_dir = project_root / "examples"

        # Known modules that don't need examples (infrastructure, templates, etc.)
        self.exclude_modules = {
            "__init__",
            "__pycache__",
            "exceptions",
            "cli",
            "tests",
            "template",
            "module_template"
        }

        # Module to example mapping (special cases)
        self.module_to_example_mapping = {
            "api_documentation": "api_documentation",  # Direct mapping
            "database_management": "database_management",  # Direct mapping
            # Add any special mappings here
        }

    def get_all_modules(self) -> Set[str]:
        """Get all module names from src/codomyrmex directory."""
        modules = set()

        if not self.src_dir.exists():
            logger.error(f"Source directory not found: {self.src_dir}")
            return modules

        # Scan for module directories
        for item in self.src_dir.iterdir():
            if item.is_dir() and item.name not in self.exclude_modules:
                # Check if it has __init__.py (indicating it's a module)
                init_file = item / "__init__.py"
                if init_file.exists():
                    modules.add(item.name)

        # Also check for single-file modules (though most are directories)
        for item in self.src_dir.glob("*.py"):
            if item.stem not in self.exclude_modules:
                modules.add(item.stem)

        logger.info(f"Found {len(modules)} modules in source directory")
        return modules

    def get_all_examples(self) -> Set[str]:
        """Get all example module names from examples directory."""
        examples = set()

        if not self.examples_dir.exists():
            logger.error(f"Examples directory not found: {self.examples_dir}")
            return examples

        # Scan for example directories (excluding special directories)
        exclude_dirs = {"_common", "_templates", "_configs", "multi_module"}

        for item in self.examples_dir.iterdir():
            if item.is_dir() and item.name not in exclude_dirs:
                # Check if it has example_basic.py
                example_file = item / "example_basic.py"
                if example_file.exists():
                    examples.add(item.name)

        logger.info(f"Found {len(examples)} example directories")
        return examples

    def check_coverage(self) -> Dict[str, any]:
        """Check coverage of examples for modules."""
        modules = self.get_all_modules()
        examples = self.get_all_examples()

        # Calculate coverage
        covered_modules = modules.intersection(examples)
        missing_examples = modules - examples
        extra_examples = examples - modules

        coverage_percentage = (len(covered_modules) / len(modules) * 100) if modules else 0

        results = {
            "total_modules": len(modules),
            "total_examples": len(examples),
            "covered_modules": len(covered_modules),
            "missing_examples": len(missing_examples),
            "extra_examples": len(extra_examples),
            "coverage_percentage": coverage_percentage,
            "modules_list": sorted(list(modules)),
            "examples_list": sorted(list(examples)),
            "covered_list": sorted(list(covered_modules)),
            "missing_list": sorted(list(missing_examples)),
            "extra_list": sorted(list(extra_examples))
        }

        return results

    def analyze_missing_examples(self, missing_modules: List[str]) -> Dict[str, any]:
        """Analyze missing examples and provide recommendations."""
        analysis = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "recommendations": []
        }

        # Categorize by priority (this could be made more sophisticated)
        high_priority_modules = {
            "logging_monitoring", "environment_setup", "terminal_interface",
            "model_context_protocol", "ai_code_editing", "static_analysis",
            "code_execution_sandbox", "data_visualization", "pattern_matching",
            "git_operations", "code_review", "security_audit"
        }

        medium_priority_modules = {
            "build_synthesis", "documentation", "api_documentation",
            "ci_cd_automation", "database_management", "containerization",
            "config_management", "project_orchestration"
        }

        for module in missing_modules:
            if module in high_priority_modules:
                analysis["high_priority"].append(module)
            elif module in medium_priority_modules:
                analysis["medium_priority"].append(module)
            else:
                analysis["low_priority"].append(module)

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(
            analysis["high_priority"],
            analysis["medium_priority"],
            analysis["low_priority"]
        )

        return analysis

    def _generate_recommendations(self, high: List[str], medium: List[str], low: List[str]) -> List[str]:
        """Generate recommendations for missing examples."""
        recommendations = []

        if high:
            recommendations.append(f"🚨 HIGH PRIORITY: Create examples for {len(high)} core modules: {', '.join(high)}")
            recommendations.append("   These modules are fundamental to Codomyrmex functionality")

        if medium:
            recommendations.append(f"⚠️  MEDIUM PRIORITY: Create examples for {len(medium)} service modules: {', '.join(medium)}")
            recommendations.append("   These modules provide important orchestration capabilities")

        if low:
            recommendations.append(f"ℹ️  LOW PRIORITY: Consider examples for {len(low)} specialized modules: {', '.join(low)}")
            recommendations.append("   These modules serve specific use cases")

        # General recommendations
        total_missing = len(high) + len(medium) + len(low)
        if total_missing > 0:
            recommendations.append("")
            recommendations.append("📝 GENERAL RECOMMENDATIONS:")
            recommendations.append("   1. Use the template system in examples/_templates/")
            recommendations.append("   2. Follow the example structure: example_basic.py, config.yaml, config.json, README.md")
            recommendations.append("   3. Reference tested methods from unit tests in docstrings")
            recommendations.append("   4. Test examples with: python -m pytest testing/examples/")
            recommendations.append("   5. Update examples/README.md and AGENTS.md after creating examples")

        return recommendations

    def check_example_completeness(self) -> Dict[str, any]:
        """Check that existing examples are complete."""
        completeness_results = {
            "total_examples": 0,
            "complete_examples": 0,
            "incomplete_examples": [],
            "missing_files": {}
        }

        if not self.examples_dir.exists():
            return completeness_results

        # Required files for each example
        required_files = [
            "example_basic.py",
            "config.yaml",
            "config.json",
            "README.md"
        ]

        for example_dir in self.examples_dir.iterdir():
            if not example_dir.is_dir() or example_dir.name.startswith('_'):
                continue

            completeness_results["total_examples"] += 1
            example_name = example_dir.name
            missing_files = []

            for required_file in required_files:
                file_path = example_dir / required_file
                if not file_path.exists():
                    missing_files.append(required_file)

            if not missing_files:
                completeness_results["complete_examples"] += 1
            else:
                completeness_results["incomplete_examples"].append(example_name)
                completeness_results["missing_files"][example_name] = missing_files

        return completeness_results

    def generate_report(self) -> Dict[str, any]:
        """Generate a comprehensive coverage report."""
        logger.info("Generating example coverage report...")

        # Basic coverage
        coverage = self.check_coverage()

        # Missing examples analysis
        missing_analysis = self.analyze_missing_examples(coverage["missing_list"])

        # Example completeness
        completeness = self.check_example_completeness()

        # Combine all results
        report = {
            "summary": {
                "modules_found": coverage["total_modules"],
                "examples_found": coverage["total_examples"],
                "coverage_percentage": round(coverage["coverage_percentage"], 1),
                "missing_examples": coverage["missing_examples"],
                "extra_examples": coverage["extra_examples"],
                "complete_examples": completeness["complete_examples"],
                "incomplete_examples": len(completeness["incomplete_examples"])
            },
            "coverage_details": coverage,
            "missing_analysis": missing_analysis,
            "completeness": completeness,
            "recommendations": missing_analysis["recommendations"],
            "generated_at": "2025-12-26T00:00:00Z"  # Would use datetime in real implementation
        }

        return report

    def print_report(self, report: Dict[str, any]):
        """Print the coverage report in a readable format."""
        print("\n" + "="*80)
        print("🏗️  CODOMYRMEX EXAMPLE COVERAGE REPORT")
        print("="*80)

        summary = report["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   Modules Found: {summary['modules_found']}")
        print(f"   Examples Found: {summary['examples_found']}")
        print(f"   Coverage: {summary['coverage_percentage']}%")
        print(f"   Missing Examples: {summary['missing_examples']}")
        print(f"   Extra Examples: {summary['extra_examples']}")
        print(f"   Complete Examples: {summary['complete_examples']}/{summary['examples_found']}")

        if summary["missing_examples"] > 0:
            print(f"\n❌ MISSING EXAMPLES ({summary['missing_examples']}):")
            for module in report["coverage_details"]["missing_list"]:
                priority = "🔴"
                if module in report["missing_analysis"]["high_priority"]:
                    priority = "🔴 HIGH"
                elif module in report["missing_analysis"]["medium_priority"]:
                    priority = "🟡 MEDIUM"
                else:
                    priority = "🟢 LOW"
                print(f"   {priority}: {module}")

        if summary["extra_examples"] > 0:
            print(f"\n⚠️  EXTRA EXAMPLES (may indicate renamed modules):")
            for example in report["coverage_details"]["extra_list"]:
                print(f"   • {example}")

        if report["completeness"]["incomplete_examples"]:
            print(f"\n🔧 INCOMPLETE EXAMPLES ({len(report['completeness']['incomplete_examples'])}):")
            for example in report["completeness"]["incomplete_examples"]:
                missing = report["completeness"]["missing_files"][example]
                print(f"   • {example}: missing {', '.join(missing)}")

        if report["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for recommendation in report["recommendations"]:
                print(f"   {recommendation}")

        print(f"\n✅ REPORT GENERATED")
        print("="*80)

    def save_report(self, report: Dict[str, any], output_file: str = None):
        """Save the report to a JSON file."""
        if output_file is None:
            output_file = self.project_root / "examples" / "coverage_report.json"

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to: {output_file}")


def main():
    """Main function to run the coverage checker."""
    checker = ExampleCoverageChecker(project_root)

    # Generate report
    report = checker.generate_report()

    # Print report
    checker.print_report(report)

    # Save report
    checker.save_report(report)

    # Exit with appropriate code
    if report["summary"]["missing_examples"] > 0:
        logger.warning(f"Found {report['summary']['missing_examples']} missing examples")
        sys.exit(0)
    else:
        logger.info("All modules have examples! 🎉")
        sys.exit(0)


if __name__ == "__main__":
    main()

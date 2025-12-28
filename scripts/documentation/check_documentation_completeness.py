#!/usr/bin/env python3
"""
Documentation Completeness Checking Tool

This script checks the completeness of documentation across the Codomyrmex project,
ensuring all modules have appropriate documentation and required files are present.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class DocumentationRequirements:
    """Requirements for module documentation."""

    required_files: List[str] = field(default_factory=lambda: [
        "README.md",
        "API_SPECIFICATION.md",
        "SECURITY.md"
    ])

    required_sections: Dict[str, List[str]] = field(default_factory=lambda: {
        "README.md": [
            "Purpose", "Features", "Installation", "Usage",
            "API", "Contributing", "License"
        ],
        "API_SPECIFICATION.md": [
            "Overview", "Functions", "Classes", "Examples"
        ]
    })

    recommended_files: List[str] = field(default_factory=lambda: [
        "CHANGELOG.md",
        "USAGE_EXAMPLES.md",
        "DEVELOPER_GUIDE.md"
    ])


@dataclass
class CompletenessReport:
    """Report on documentation completeness."""

    module_path: str
    completeness_score: float
    missing_required_files: List[str]
    missing_recommended_files: List[str]
    missing_sections: Dict[str, List[str]]
    issues: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "module_path": self.module_path,
            "completeness_score": self.completeness_score,
            "missing_required_files": self.missing_required_files,
            "missing_recommended_files": self.missing_recommended_files,
            "missing_sections": self.missing_sections,
            "issues": self.issues,
            "recommendations": self.recommendations
        }


class DocumentationCompletenessChecker:
    """
    Comprehensive documentation completeness checker.

    Analyzes documentation coverage across modules and provides
    detailed reports on missing files, sections, and improvements.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the completeness checker.

        Args:
            project_root: Root path of the project
        """
        self.project_root = Path(project_root or SCRIPT_DIR)
        self.requirements = DocumentationRequirements()
        self.src_path = self.project_root / "src" / "codomyrmex"

    def check_documentation_coverage(self) -> Dict[str, CompletenessReport]:
        """
        Check documentation coverage across all modules.

        Returns:
            Dictionary mapping module paths to completeness reports
        """
        if not self.src_path.exists():
            raise ValueError(f"Source path {self.src_path} does not exist")

        reports = {}

        # Check main project documentation
        reports["project_root"] = self._check_module_completeness(self.project_root)

        # Check each module
        for module_path in self.src_path.iterdir():
            if module_path.is_dir() and not module_path.name.startswith('_'):
                reports[module_path.name] = self._check_module_completeness(module_path)

        return reports

    def find_missing_docs(self) -> List[str]:
        """
        Find modules that are completely missing documentation.

        Returns:
            List of module paths missing documentation
        """
        missing = []

        for module_path in self.src_path.iterdir():
            if module_path.is_dir() and not module_path.name.startswith('_'):
                has_docs = False

                for doc_file in self.requirements.required_files:
                    if (module_path / doc_file).exists():
                        has_docs = True
                        break

                if not has_docs:
                    missing.append(str(module_path))

        return missing

    def validate_doc_structure(self, module_path: str) -> Dict[str, Any]:
        """
        Validate the structure of documentation in a module.

        Args:
            module_path: Path to the module

        Returns:
            Validation results
        """
        module_path = Path(module_path)
        validation = {
            "valid": True,
            "issues": [],
            "structure_score": 100
        }

        # Check required files
        for required_file in self.requirements.required_files:
            file_path = module_path / required_file
            if not file_path.exists():
                validation["issues"].append(f"Missing required file: {required_file}")
                validation["structure_score"] -= 20
                validation["valid"] = False

        # Check file contents and sections
        for file_name, required_sections in self.requirements.required_sections.items():
            file_path = module_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check for required sections (case-insensitive)
                    missing_sections = []
                    for section in required_sections:
                        # Look for headers with the section name
                        pattern = rf'^#+\s*{re.escape(section)}'
                        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                            missing_sections.append(section)

                    if missing_sections:
                        validation["issues"].append(
                            f"{file_name}: Missing sections: {', '.join(missing_sections)}"
                        )
                        validation["structure_score"] -= 10
                        validation["valid"] = False

                except Exception as e:
                    validation["issues"].append(f"Error reading {file_name}: {e}")
                    validation["structure_score"] -= 15
                    validation["valid"] = False

        return validation

    def generate_completeness_report(self) -> str:
        """
        Generate a  completeness report.

        Returns:
            Formatted report string
        """
        reports = self.check_documentation_coverage()

        # Calculate overall statistics
        total_modules = len(reports)
        complete_modules = sum(1 for r in reports.values() if r.completeness_score >= 80)
        incomplete_modules = total_modules - complete_modules

        total_missing_required = sum(len(r.missing_required_files) for r in reports.values())
        total_missing_recommended = sum(len(r.missing_recommended_files) for r in reports.values())

        avg_score = sum(r.completeness_score for r in reports.values()) / total_modules if total_modules > 0 else 0

        # Generate report
        lines = []
        lines.append("=" * 70)
        lines.append("Codomyrmex Documentation Completeness Report")
        lines.append("=" * 70)
        lines.append("")

        lines.append("📊 OVERVIEW")
        lines.append("-" * 20)
        lines.append(f"Total modules checked: {total_modules}")
        lines.append(f"Complete modules (≥80%): {complete_modules}")
        lines.append(f"Incomplete modules: {incomplete_modules}")
        lines.append(".1f")
        lines.append(f"Missing required files: {total_missing_required}")
        lines.append(f"Missing recommended files: {total_missing_recommended}")
        lines.append("")

        # Module breakdown
        lines.append("📁 MODULE BREAKDOWN")
        lines.append("-" * 25)

        for module_name, report in sorted(reports.items()):
            status = "✅" if report.completeness_score >= 80 else "⚠️" if report.completeness_score >= 50 else "❌"
            lines.append(".1f")

            if report.missing_required_files:
                lines.append(f"    Missing required: {', '.join(report.missing_required_files)}")

            if report.missing_recommended_files:
                lines.append(f"    Missing recommended: {', '.join(report.missing_recommended_files)}")

            if report.issues:
                lines.append(f"    Issues: {len(report.issues)}")
            lines.append("")

        # Detailed recommendations
        all_recommendations = []
        for report in reports.values():
            all_recommendations.extend(report.recommendations)

        if all_recommendations:
            lines.append("💡 RECOMMENDATIONS")
            lines.append("-" * 20)
            for rec in all_recommendations[:10]:  # Show top 10
                lines.append(f"• {rec}")
            if len(all_recommendations) > 10:
                lines.append(f"... and {len(all_recommendations) - 10} more")
            lines.append("")

        return "\n".join(lines)

    def _check_module_completeness(self, module_path: Path) -> CompletenessReport:
        """Check completeness of documentation for a single module."""
        report = CompletenessReport(
            module_path=str(module_path),
            completeness_score=100.0,
            missing_required_files=[],
            missing_recommended_files=[],
            missing_sections={},
            issues=[],
            recommendations=[]
        )

        # Check required files
        for required_file in self.requirements.required_files:
            if not (module_path / required_file).exists():
                report.missing_required_files.append(required_file)
                report.completeness_score -= 15

        # Check recommended files
        for recommended_file in self.requirements.recommended_files:
            if not (module_path / recommended_file).exists():
                report.missing_recommended_files.append(recommended_file)
                report.completeness_score -= 5

        # Check file sections
        for file_name, required_sections in self.requirements.required_sections.items():
            file_path = module_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    missing_sections = []
                    for section in required_sections:
                        # Look for section headers (case-insensitive)
                        pattern = rf'^#+\s*{re.escape(section)}'
                        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                            missing_sections.append(section)

                    if missing_sections:
                        report.missing_sections[file_name] = missing_sections
                        report.completeness_score -= 5

                except Exception as e:
                    report.issues.append(f"Error reading {file_name}: {e}")
                    report.completeness_score -= 10

        # Generate recommendations
        if report.missing_required_files:
            report.recommendations.append(
                f"Create missing required files: {', '.join(report.missing_required_files)}"
            )

        if report.missing_recommended_files:
            report.recommendations.append(
                f"Consider adding recommended files: {', '.join(report.missing_recommended_files)}"
            )

        if report.missing_sections:
            for file_name, sections in report.missing_sections.items():
                report.recommendations.append(
                    f"Add missing sections to {file_name}: {', '.join(sections)}"
                )

        # Ensure score doesn't go below 0
        report.completeness_score = max(0.0, report.completeness_score)

        return report


def check_documentation_coverage() -> Dict[str, CompletenessReport]:
    """
    Convenience function to check documentation coverage.

    Returns:
        Dictionary mapping module paths to completeness reports
    """
    checker = DocumentationCompletenessChecker()
    return checker.check_documentation_coverage()


def find_missing_docs() -> List[str]:
    """
    Convenience function to find modules missing documentation.

    Returns:
        List of module paths missing documentation
    """
    checker = DocumentationCompletenessChecker()
    return checker.find_missing_docs()


def validate_doc_structure(module_path: str) -> Dict[str, Any]:
    """
    Convenience function to validate documentation structure.

    Args:
        module_path: Path to the module

    Returns:
        Validation results
    """
    checker = DocumentationCompletenessChecker()
    return checker.validate_doc_structure(module_path)


def generate_completeness_report() -> str:
    """
    Convenience function to generate completeness report.

    Returns:
        Formatted completeness report
    """
    checker = DocumentationCompletenessChecker()
    return checker.generate_completeness_report()


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check documentation completeness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --check-coverage
  %(prog)s --find-missing
  %(prog)s --validate-module src/codomyrmex/logging_monitoring/
  %(prog)s --generate-report
        """
    )

    parser.add_argument(
        '--check-coverage',
        action='store_true',
        help='Check documentation coverage across all modules'
    )

    parser.add_argument(
        '--find-missing',
        action='store_true',
        help='Find modules completely missing documentation'
    )

    parser.add_argument(
        '--validate-module',
        help='Validate documentation structure for a specific module'
    )

    parser.add_argument(
        '--generate-report',
        action='store_true',
        help='Generate a  completeness report'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file for results (JSON format)'
    )

    args = parser.parse_args()

    checker = DocumentationCompletenessChecker()

    try:
        if args.check_coverage:
            print("🔍 Checking documentation coverage...")
            reports = checker.check_documentation_coverage()

            if args.output:
                # Save as JSON
                output_data = {name: report.to_dict() for name, report in reports.items()}
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                print(f"✅ Coverage report saved to {args.output}")
            else:
                # Print summary
                total_modules = len(reports)
                complete = sum(1 for r in reports.values() if r.completeness_score >= 80)
                print(f"📊 Coverage Summary: {complete}/{total_modules} modules have ≥80% complete documentation")

        elif args.find_missing:
            print("🔍 Finding modules missing documentation...")
            missing = checker.find_missing_docs()

            if missing:
                print(f"❌ Found {len(missing)} modules missing documentation:")
                for module in missing:
                    print(f"  • {module}")
            else:
                print("✅ All modules have some documentation!")

        elif args.validate_module:
            print(f"🔍 Validating documentation structure for {args.validate_module}...")
            validation = checker.validate_doc_structure(args.validate_module)

            if validation["valid"]:
                print("✅ Documentation structure is valid")
            else:
                print("❌ Documentation structure issues found:")
                for issue in validation["issues"]:
                    print(f"  • {issue}")
                print(f"📊 Structure score: {validation['structure_score']}/100")

        elif args.generate_report:
            print("📋 Generating completeness report...")
            report = checker.generate_completeness_report()

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"✅ Report saved to {args.output}")
            else:
                print(report)

        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Error during documentation checking: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

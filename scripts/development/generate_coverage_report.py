#!/usr/bin/env python3
"""
Generate comprehensive coverage report for Codomyrmex.

This script analyzes coverage.json and generates:
- Human-readable coverage report
- Module-by-module breakdown
- Coverage dashboard in markdown format
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging

    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def load_coverage_data(coverage_file: Path) -> Optional[Dict[str, Any]]:
    """Load coverage data from JSON file."""
    if not coverage_file.exists():
        logger.error(f"Coverage file not found: {coverage_file}")
        return None

    try:
        with open(coverage_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in coverage file: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading coverage file: {e}")
        return None


def calculate_module_coverage(
    coverage_data: Dict[str, Any], module_name: str
) -> Dict[str, Any]:
    """Calculate coverage statistics for a specific module."""
    files = coverage_data.get("files", {})
    module_files = {
        path: data
        for path, data in files.items()
        if f"codomyrmex/{module_name}" in path
    }

    if not module_files:
        return {
            "module": module_name,
            "files": 0,
            "lines_total": 0,
            "lines_covered": 0,
            "lines_missing": 0,
            "coverage_percent": 0.0,
            "statements_total": 0,
            "statements_covered": 0,
            "statements_missing": 0,
        }

    total_lines = 0
    covered_lines = 0
    missing_lines = 0
    total_statements = 0
    covered_statements = 0
    missing_statements = 0

    for file_data in module_files.values():
        summary = file_data.get("summary", {})
        total_lines += summary.get("num_statements", 0)
        covered_lines += summary.get("covered_lines", 0)
        missing_lines += summary.get("missing_lines", 0)
        total_statements += summary.get("num_statements", 0)
        covered_statements += summary.get("covered_lines", 0)
        missing_statements += summary.get("missing_lines", 0)

    coverage_percent = (
        (covered_lines / total_lines * 100) if total_lines > 0 else 0.0
    )

    return {
        "module": module_name,
        "files": len(module_files),
        "lines_total": total_lines,
        "lines_covered": covered_lines,
        "lines_missing": missing_lines,
        "coverage_percent": coverage_percent,
        "statements_total": total_statements,
        "statements_covered": covered_statements,
        "statements_missing": missing_statements,
    }


def get_all_modules() -> List[str]:
    """Get list of all modules in codomyrmex."""
    src_path = Path(__file__).parent.parent.parent / "src" / "codomyrmex"
    if not src_path.exists():
        logger.warning(f"Source path not found: {src_path}")
        return []

    modules = []
    for item in src_path.iterdir():
        if item.is_dir() and not item.name.startswith("_") and item.name != "output":
            modules.append(item.name)

    return sorted(modules)


def generate_coverage_report(
    coverage_data: Dict[str, Any], output_file: Path
) -> str:
    """Generate markdown coverage report."""
    summary = coverage_data.get("totals", {})
    overall_coverage = summary.get("percent_covered", 0.0)
    total_lines = summary.get("num_statements", 0)
    covered_lines = summary.get("covered_lines", 0)
    missing_lines = summary.get("missing_lines", 0)

    report_lines = [
        "# 📊 Codomyrmex Test Coverage Report",
        "",
        f"*Generated: {Path(__file__).stat().st_mtime}*",
        "",
        "## Overall Coverage",
        "",
        f"- **Overall Coverage**: {overall_coverage:.2f}%",
        f"- **Total Statements**: {total_lines:,}",
        f"- **Covered Statements**: {covered_lines:,}",
        f"- **Missing Statements**: {missing_lines:,}",
        "",
        "## Coverage by Module",
        "",
        "| Module | Files | Coverage % | Lines Covered | Lines Missing | Status |",
        "|--------|-------|------------|---------------|---------------|--------|",
    ]

    modules = get_all_modules()
    module_stats = []

    for module in modules:
        stats = calculate_module_coverage(coverage_data, module)
        module_stats.append(stats)

        # Sort by coverage percentage (lowest first)
    module_stats.sort(key=lambda x: x["coverage_percent"])

    for stats in module_stats:
        coverage_pct = stats["coverage_percent"]
        if coverage_pct >= 80:
            status = "✅"
        elif coverage_pct >= 60:
            status = "⚠️"
        else:
            status = "❌"

        report_lines.append(
            f"| {stats['module']} | {stats['files']} | "
            f"{coverage_pct:.1f}% | {stats['lines_covered']:,} | "
            f"{stats['lines_missing']:,} | {status} |"
        )

    report_lines.extend(
        [
            "",
            "## Coverage Status Legend",
            "",
            "- ✅ **80%+**: Excellent coverage",
            "- ⚠️ **60-79%**: Needs improvement",
            "- ❌ **<60%**: Critical - requires immediate attention",
            "",
            "## Recommendations",
            "",
        ]
    )

    # Add recommendations
    low_coverage_modules = [
        s for s in module_stats if s["coverage_percent"] < 60
    ]
    if low_coverage_modules:
        report_lines.append(
            f"### Critical Modules ({len(low_coverage_modules)} modules need attention):"
        )
        for stats in low_coverage_modules[:5]:  # Top 5
            report_lines.append(
                f"- **{stats['module']}**: {stats['coverage_percent']:.1f}% coverage "
                f"({stats['lines_missing']:,} lines missing)"
            )
        report_lines.append("")

    medium_coverage_modules = [
        s for s in module_stats if 60 <= s["coverage_percent"] < 80
    ]
    if medium_coverage_modules:
        report_lines.append(
            f"### Modules Needing Improvement ({len(medium_coverage_modules)} modules):"
        )
        for stats in medium_coverage_modules[:5]:  # Top 5
            report_lines.append(
                f"- **{stats['module']}**: {stats['coverage_percent']:.1f}% coverage"
            )
        report_lines.append("")

    if overall_coverage < 80:
        report_lines.append(
            f"⚠️ **Overall coverage is below target (80%)**. "
            f"Current coverage: {overall_coverage:.2f}%"
        )
    else:
        report_lines.append(
            f"✅ **Overall coverage meets target (80%)**. "
            f"Current coverage: {overall_coverage:.2f}%"
        )

    report_lines.extend(
        [
            "",
            "## How to Improve Coverage",
            "",
            "1. Run tests: `make test-coverage`",
            "2. Review HTML report: `make test-coverage-html`",
            "3. Focus on modules with <60% coverage",
            "4. Add unit tests for uncovered code paths",
            "5. Review integration tests for edge cases",
            "",
            "---",
            "",
            "*This report is generated automatically. "
            "Run `python scripts/development/generate_coverage_report.py` to regenerate.*",
        ]
    )

    report_content = "\n".join(report_lines)

    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_content


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    coverage_file = repo_root / "coverage.json"
    output_file = repo_root / "docs" / "project" / "coverage-report.md"

    logger.info(f"Loading coverage data from: {coverage_file}")

    coverage_data = load_coverage_data(coverage_file)
    if not coverage_data:
        logger.error("Failed to load coverage data")
        return 1

    logger.info("Generating coverage report...")
    report_content = generate_coverage_report(coverage_data, output_file)

    logger.info(f"Coverage report generated: {output_file}")
    print(f"\n✅ Coverage report generated: {output_file}")
    print(f"📊 Overall coverage: {coverage_data.get('totals', {}).get('percent_covered', 0):.2f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())


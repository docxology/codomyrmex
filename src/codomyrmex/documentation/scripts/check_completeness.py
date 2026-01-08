from pathlib import Path
from typing import Dict, List, Set
import logging
import re
import sys

from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging



#!/usr/bin/env python3
"""
Documentation Completeness Checker.

This script checks for placeholder content and generates an implementation status tracker.
"""


try:

    setup_logging()
    logger = get_logger(__name__)
except ImportError:

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class DocumentationChecker:
    """Checks documentation for completeness and placeholder content."""

    def __init__(self, repo_root: Path):
        """Initialize checker."""
        self.repo_root = repo_root.resolve()
        self.src_path = self.repo_root / "src" / "codomyrmex"
        self.placeholders: Dict[str, List[Dict[str, str]]] = {}
        self.module_status: Dict[str, Dict[str, any]] = {}

        # Common placeholder patterns
        self.placeholder_patterns = [
            (r"placeholder", "placeholder text"),
            (r"TODO", "TODO comments"),
            (r"FIXME", "FIXME comments"),
            (r"XXX", "XXX markers"),
            (r"Placeholder content", "placeholder content"),
            (r"needs filling", "needs filling"),
            (r"needs specific content", "needs specific content"),
            (r"\[.*to be completed.*\]", "to be completed markers"),
            (r"\[.*TBD.*\]", "TBD markers"),
            (r"\[.*coming soon.*\]", "coming soon markers"),
            (r"example_function\(\)", "example function"),
            (r"# Placeholder", "placeholder headers"),
            (r"This is a placeholder", "placeholder text"),
        ]

    def check_file_for_placeholders(self, file_path: Path) -> List[Dict[str, str]]:
        """Check a file for placeholder content."""
        placeholders = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for pattern, description in self.placeholder_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        placeholders.append(
                            {
                                "line": line_num,
                                "content": line.strip()[:100],  # First 100 chars
                                "type": description,
                            }
                        )
                        break  # Only report once per line

        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")

        return placeholders

    def check_module_documentation(self, module_name: str) -> Dict[str, any]:
        """Check documentation completeness for a module."""
        module_path = self.src_path / module_name
        if not module_path.exists():
            return {"module": module_name, "status": "not_found", "files": []}

        # Required documentation files
        required_files = [
            "README.md",
            "API_SPECIFICATION.md",
            "MCP_TOOL_SPECIFICATION.md",
            "CHANGELOG.md",
            "SECURITY.md",
        ]

        file_status = {}
        total_placeholders = 0

        for file_name in required_files:
            file_path = module_path / file_name
            if file_path.exists():
                placeholders = self.check_file_for_placeholders(file_path)
                file_status[file_name] = {
                    "exists": True,
                    "placeholders": placeholders,
                    "placeholder_count": len(placeholders),
                }
                total_placeholders += len(placeholders)
            else:
                file_status[file_name] = {
                    "exists": False,
                    "placeholders": [],
                    "placeholder_count": 0,
                }

        # Check for docs/ directory
        docs_dir = module_path / "docs"
        if docs_dir.exists():
            docs_files = list(docs_dir.rglob("*.md"))
            file_status["docs/"] = {
                "exists": True,
                "file_count": len(docs_files),
                "placeholders": [],
            }
        else:
            file_status["docs/"] = {"exists": False, "file_count": 0}

        # Determine overall status
        missing_files = [f for f, status in file_status.items() if not status["exists"]]
        has_placeholders = total_placeholders > 0

        if missing_files and has_placeholders:
            status = "incomplete"
        elif missing_files:
            status = "missing_files"
        elif has_placeholders:
            status = "has_placeholders"
        else:
            status = "complete"

        return {
            "module": module_name,
            "status": status,
            "files": file_status,
            "missing_files": missing_files,
            "total_placeholders": total_placeholders,
        }

    def check_all_modules(self) -> Dict[str, any]:
        """Check all modules for documentation completeness."""
        results = {}

        if not self.src_path.exists():
            logger.error(f"Source path not found: {self.src_path}")
            return results

        for item in self.src_path.iterdir():
            if item.is_dir() and not item.name.startswith("_") and item.name != "output":
                result = self.check_module_documentation(item.name)
                results[item.name] = result

        return results

    def generate_implementation_status(self, module_results: Dict[str, any]) -> str:
        """Generate implementation status tracker markdown."""
        lines = [
            "# Codomyrmex Implementation Status Tracker",
            "",
            "*This document tracks the implementation and documentation status of all modules.*",
            "",
            "## Status Legend",
            "",
            "- ✅ **Complete**: All required files present, no placeholders",
            "- ⚠️ **Incomplete**: Missing files or has placeholder content",
            "- 📝 **Missing Files**: Required documentation files missing",
            "- 🔧 **Has Placeholders**: Contains placeholder content",
            "",
            "## Module Status",
            "",
            "| Module | Status | Missing Files | Placeholders |",
            "|--------|--------|--------------|--------------|",
        ]

        # Sort by status (complete first, then incomplete)
        sorted_modules = sorted(
            module_results.items(),
            key=lambda x: (
                0 if x[1]["status"] == "complete" else 1,
                x[1]["total_placeholders"],
                len(x[1]["missing_files"]),
            ),
        )

        for module_name, result in sorted_modules:
            status_emoji = {
                "complete": "✅",
                "incomplete": "⚠️",
                "missing_files": "📝",
                "has_placeholders": "🔧",
            }.get(result["status"], "❓")

            missing_str = ", ".join(result["missing_files"]) if result["missing_files"] else "none"
            placeholder_str = (
                str(result["total_placeholders"]) if result["total_placeholders"] > 0 else "0"
            )

            lines.append(
                f"| {module_name} | {status_emoji} {result['status']} | {missing_str} | {placeholder_str} |"
            )

        # Summary
        total_modules = len(module_results)
        complete_modules = sum(1 for r in module_results.values() if r["status"] == "complete")
        incomplete_modules = total_modules - complete_modules
        total_placeholders = sum(r["total_placeholders"] for r in module_results.values())

        lines.extend(
            [
                "",
                "## Summary",
                "",
                f"- **Total Modules**: {total_modules}",
                f"- **Complete**: {complete_modules} ({complete_modules/total_modules*100:.1f}%)",
                f"- **Incomplete**: {incomplete_modules} ({incomplete_modules/total_modules*100:.1f}%)",
                f"- **Total Placeholders**: {total_placeholders}",
                "",
                "## Next Steps",
                "",
            ]
        )

        if incomplete_modules > 0:
            lines.append("### Priority Actions:")
            lines.append("")

            # Find modules with most issues
            priority_modules = sorted(
                [
                    (name, result)
                    for name, result in module_results.items()
                    if result["status"] != "complete"
                ],
                key=lambda x: (x[1]["total_placeholders"], len(x[1]["missing_files"])),
                reverse=True,
            )[:5]

            for module_name, result in priority_modules:
                lines.append(f"1. **{module_name}**:")
                if result["missing_files"]:
                    lines.append(f"   - Add missing files: {', '.join(result['missing_files'])}")
                if result["total_placeholders"] > 0:
                    lines.append(f"   - Replace {result['total_placeholders']} placeholder(s)")
                lines.append("")

        lines.extend(
            [
                "---",
                "",
                "*This report is generated automatically. "
                "Run `python scripts/documentation/check_completeness.py` to regenerate.*",
            ]
        )

        return "\n".join(lines)

    def generate_detailed_report(self, module_results: Dict[str, any]) -> str:
        """Generate detailed report with placeholder locations."""
        lines = [
            "# Documentation Completeness Detailed Report",
            "",
            "*This report shows specific placeholder content found in documentation.*",
            "",
        ]

        for module_name, result in sorted(module_results.items()):
            if result["total_placeholders"] == 0:
                continue

            lines.extend(
                [
                    f"## {module_name}",
                    "",
                ]
            )

            for file_name, file_status in result["files"].items():
                if file_status.get("placeholders"):
                    lines.append(f"### {file_name}")
                    lines.append("")
                    lines.append("| Line | Type | Content |")
                    lines.append("|------|------|---------|")

                    for placeholder in file_status["placeholders"][:10]:  # First 10
                        lines.append(
                            f"| {placeholder['line']} | {placeholder['type']} | "
                            f"`{placeholder['content']}` |"
                        )

                    if len(file_status["placeholders"]) > 10:
                        lines.append(
                            f"| ... | ... | *and {len(file_status['placeholders']) - 10} more* |"
                        )

                    lines.append("")

        return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    checker = DocumentationChecker(repo_root)

    logger.info("Checking documentation completeness...")
    results = checker.check_all_modules()

    # Generate status tracker
    status_file = repo_root / "docs" / "project" / "implementation-status.md"
    status_content = checker.generate_implementation_status(results)

    status_file.parent.mkdir(parents=True, exist_ok=True)
    with open(status_file, "w", encoding="utf-8") as f:
        f.write(status_content)

    logger.info(f"Implementation status tracker written to: {status_file}")

    # Generate detailed report
    detailed_file = repo_root / "docs" / "project" / "documentation-completeness.md"
    detailed_content = checker.generate_detailed_report(results)

    detailed_file.parent.mkdir(parents=True, exist_ok=True)
    with open(detailed_file, "w", encoding="utf-8") as f:
        f.write(detailed_content)

    logger.info(f"Detailed completeness report written to: {detailed_file}")

    # Print summary
    total_modules = len(results)
    complete_modules = sum(1 for r in results.values() if r["status"] == "complete")
    total_placeholders = sum(r["total_placeholders"] for r in results.values())

    print("\n" + "=" * 60)
    print("Documentation Completeness Results")
    print("=" * 60)
    print(f"\nModules checked: {total_modules}")
    print(f"Complete modules: {complete_modules} ({complete_modules/total_modules*100:.1f}%)")
    print(f"Total placeholders found: {total_placeholders}")

    if total_placeholders > 0:
        print("\n⚠️  Placeholder content found in documentation")
        print("   Review the detailed report for specific locations")

    if complete_modules < total_modules:
        print(f"\n⚠️  {total_modules - complete_modules} modules need attention")

    print(f"\n✅ Reports generated:")
    print(f"   - {status_file}")
    print(f"   - {detailed_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


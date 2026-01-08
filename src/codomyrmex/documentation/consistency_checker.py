from pathlib import Path

from codomyrmex.logging_monitoring.logger_config import get_logger














"""Documentation Consistency Checker Module.

This module ensures documentation consistency across the Codomyrmex platform,
checking for naming conventions, formatting standards, and content alignment.
"""



logger = get_logger(__name__)



class DocumentationConsistencyChecker:
    """Checks documentation consistency across files."""

    def __init__(self):
        self.naming_conventions = {
            "files": ["README.md", "CHANGELOG.md", "CONTRIBUTING.md"],
            "headers": ["# ", "## ", "### "],
            "code_blocks": ["```python", "```bash", "```javascript"]
        }

        self.required_sections = [
            "Installation", "Usage", "API Reference", "Examples"
        ]

    def check_project_consistency(self, project_path: Path) -> dict[str, list[str]]:
        """Check consistency across the entire project."""
        issues = {
            "naming": [],
            "formatting": [],
            "content": [],
            "structure": []
        }

        # Get all markdown files
        md_files = list(project_path.rglob("*.md"))

        # Check naming conventions
        issues["naming"] = self._check_naming_conventions(md_files)

        # Check formatting consistency
        issues["formatting"] = self._check_formatting_consistency(md_files)

        # Check content consistency
        issues["content"] = self._check_content_consistency(md_files)

        # Check structural consistency
        issues["structure"] = self._check_structural_consistency(md_files)

        return issues

    def _check_naming_conventions(self, md_files: list[Path]) -> list[str]:
        """Check file and header naming conventions."""
        issues = []

        for file_path in md_files:
            filename = file_path.name

            # Check filename conventions
            if filename in ["readme.md", "Readme.md", "README.MD"]:
                issues.append(f"❌ {file_path}: Use 'README.md' (not '{filename}')")

            # Check header formatting in file
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.split("\n")

                for i, line in enumerate(lines[:10]):  # Check first 10 lines
                    if line.strip().startswith("#") and not line.startswith("# "):
                        issues.append(f"❌ {file_path}:{i+1}: Header should start with '# '")

            except Exception as e:
                issues.append(f"⚠️ {file_path}: Could not read file ({e})")

        return issues

    def _check_formatting_consistency(self, md_files: list[Path]) -> list[str]:
        """Check formatting consistency."""
        issues = []

        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Check for mixed tabs and spaces
                if "\t" in content and "    " in content:
                    issues.append(f"❌ {file_path}: Mixed tabs and spaces")

                # Check for trailing whitespace
                lines_with_trailing = []
                for i, line in enumerate(content.split("\n")):
                    if line.rstrip() != line:
                        lines_with_trailing.append(i + 1)

                if lines_with_trailing:
                    issues.append(f"❌ {file_path}: Trailing whitespace on lines {lines_with_trailing[:3]}")

                # Check for inconsistent line endings
                if "\\r\\n" in content and "\\n" in content:
                    issues.append(f"❌ {file_path}: Mixed line endings")

            except Exception as e:
                issues.append(f"⚠️ {file_path}: Could not check formatting ({e})")

        return issues

    def _check_content_consistency(self, md_files: list[Path]) -> list[str]:
        """Check content consistency."""
        issues = []

        # Check for consistent terminology
        term_usage = {}

        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8").lower()

                # Track usage of key terms
                key_terms = ["codomyrmex", "module", "agent", "documentation"]
                for term in key_terms:
                    if term not in term_usage:
                        term_usage[term] = []
                    if term in content:
                        term_usage[term].append(str(file_path))

            except Exception as e:
                issues.append(f"⚠️ {file_path}: Could not check content ({e})")

        # Report inconsistent term usage
        for term, files in term_usage.items():
            if len(files) > 0:
                usage_rate = len(files) / len(md_files)
                if usage_rate < 0.3:  # Less than 30% usage
                    issues.append(f"⚠️ Term '{term}' used in only {len(files)}/{len(md_files)} files")

        return issues

    def _check_structural_consistency(self, md_files: list[Path]) -> list[str]:
        """Check structural consistency."""
        issues = []

        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Check for required sections
                missing_sections = []
                for section in self.required_sections:
                    if f"## {section}" not in content:
                        missing_sections.append(section)

                if missing_sections:
                    issues.append(f"❌ {file_path}: Missing sections: {', '.join(missing_sections)}")

                # Check for consistent section ordering
                section_order = []
                for line in content.split("\n"):
                    if line.strip().startswith("## "):
                        section_order.append(line.strip()[3:])

                # Check if sections follow logical order
                expected_order = ["Overview", "Installation", "Usage", "API", "Examples", "Contributing"]
                current_order = [s for s in expected_order if s in section_order]

                if current_order != [s for s in expected_order if s in section_order]:
                    issues.append(f"⚠️ {file_path}: Section order could be improved")

            except Exception as e:
                issues.append(f"⚠️ {file_path}: Could not check structure ({e})")

        return issues

    def generate_consistency_report(self, project_path: Path) -> str:
        """Generate a comprehensive consistency report."""
        issues = self.check_project_consistency(project_path)

        report_lines = []
        report_lines.append("# Documentation Consistency Report")
        report_lines.append(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        total_issues = sum(len(issue_list) for issue_list in issues.values())

        for category, issue_list in issues.items():
            if issue_list:
                report_lines.append(f"## {category.title()} Issues ({len(issue_list)})")
                for issue in issue_list[:10]:  # Show first 10 issues
                    report_lines.append(f"- {issue}")
                if len(issue_list) > 10:
                    report_lines.append(f"- ... and {len(issue_list) - 10} more issues")
                report_lines.append("")

        report_lines.append(f"## Summary: {total_issues} total issues found")

        if total_issues == 0:
            report_lines.append("🎉 Excellent! No consistency issues found.")
        elif total_issues < 5:
            report_lines.append("👍 Good consistency with minor issues.")
        else:
            report_lines.append("⚠️ Multiple consistency issues need attention.")

        return "\n".join(report_lines)




def generate_quality_tests() -> str:
    """Generate tests for the quality assessment modules."""
    return "Tests for documentation quality assessment modules."

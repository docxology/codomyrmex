"""Documentation quality generators for droid tasks."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


def assess_documentation_coverage(*, prompt: str, description: str) -> str:
    """Assess documentation coverage for README, AGENTS.md, and technical accuracy."""
    import sys
    from pathlib import Path

    # Add the current directory to Python path for direct imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        pass
#         sys.path.insert(0, current_dir)  # Removed sys.path manipulation

    # Define paths to check
    project_root = Path(__file__).parent.parent.parent.parent.parent
    docs_path = project_root / "src" / "codomyrmex" / "documentation"

    coverage_report = []
    coverage_report.append("📊 Documentation Coverage Assessment Report")
    coverage_report.append("=" * 50)

    # Check README files
    readme_checks = []
    readme_locations = [
        project_root / "README.md",
        docs_path / "README.md"
    ]

    for readme_path in readme_locations:
        if readme_path.exists():
            content = readme_path.read_text()
            score = assess_readme_quality(content, readme_path)
            readme_checks.append(f"✅ {readme_path.relative_to(project_root)}: Score {score}/100")
        else:
            readme_checks.append(f"❌ {readme_path.relative_to(project_root)}: Missing")

    coverage_report.append("\n📖 README Coverage:")
    coverage_report.extend(readme_checks)

    # Check AGENTS.md files
    agents_checks = []
    agents_locations = [
        project_root / "AGENTS.md",
        project_root / "src" / "AGENTS.md",
        project_root / "docs" / "AGENTS.md"
    ]

    for agents_path in agents_locations:
        if agents_path.exists():
            content = agents_path.read_text()
            score = assess_agents_quality(content, agents_path)
            agents_checks.append(f"✅ {agents_path.relative_to(project_root)}: Score {score}/100")
        else:
            agents_checks.append(f"❌ {agents_path.relative_to(project_root)}: Missing")

    coverage_report.append("\n🤖 AGENTS.md Coverage:")
    coverage_report.extend(agents_checks)

    # Check technical documentation
    tech_docs_checks = []
    tech_docs_path = docs_path / "docs"
    if tech_docs_path.exists():
        md_files = list(tech_docs_path.glob("*.md"))
        for doc_path in md_files[:5]:  # Check first 5 files
            content = doc_path.read_text()
            score = assess_technical_accuracy(content, doc_path)
            tech_docs_checks.append(f"✅ {doc_path.relative_to(project_root)}: Score {score}/100")

        if len(md_files) > 5:
            tech_docs_checks.append(f"📁 ... and {len(md_files) - 5} more files")
    else:
        tech_docs_checks.append("❌ Technical documentation directory missing")

    coverage_report.append("\n📚 Technical Documentation Coverage:")
    coverage_report.extend(tech_docs_checks)

    # Overall assessment
    total_score = sum(int(check.split("Score ")[1].split("/")[0]) for check in coverage_report if "Score" in check)
    max_possible = len([check for check in coverage_report if "Score" in check]) * 100
    overall_score = (total_score / max_possible * 100) if max_possible > 0 else 0

    coverage_report.append(f"🏆 Overall Coverage Score: {overall_score:.1f}/100")

    # Write report
    report_path = docs_path / "coverage_assessment.md"
    report_path.write_text("\n".join(coverage_report))

    logger.info(f"Documentation coverage assessed: {overall_score:.1f}/100", extra={"description": description})
    return f"Documentation coverage assessed: {overall_score:.1f}/100"


def generate_quality_tests() -> str:
    """Generate tests for the quality assessment modules."""
    return '''"""Tests for documentation quality assessment modules."""

import pytest
from pathlib import Path
import tempfile
import os


class TestDocumentationQualityAnalyzer:
    """Test cases for DocumentationQualityAnalyzer."""

    def test_analyzer_creation(self):
        """Test creating a quality analyzer."""
        from codomyrmex.documentation.quality.quality_assessment import DocumentationQualityAnalyzer

        analyzer = DocumentationQualityAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_file')

    def test_file_analysis(self):
        """Test analyzing a documentation file."""
        from codomyrmex.documentation.quality.quality_assessment import DocumentationQualityAnalyzer

        analyzer = DocumentationQualityAnalyzer()

        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Documentation\\n\\n## Installation\\n```bash\\npip install test\\n```\\n## Usage\\nExample usage here.")
            temp_path = Path(f.name)

        try:
            result = analyzer.analyze_file(temp_path)
            assert "overall_score" in result
            assert isinstance(result["overall_score"], float)
            assert 0 <= result["overall_score"] <= 100
        finally:
            temp_path.unlink()


class TestDocumentationConsistencyChecker:
    """Test cases for DocumentationConsistencyChecker."""

    def test_checker_creation(self):
        """Test creating a consistency checker."""
        from codomyrmex.documentation.quality.consistency_checker import DocumentationConsistencyChecker

        checker = DocumentationConsistencyChecker()
        assert checker is not None
        assert hasattr(checker, 'check_project_consistency')

    def test_consistency_check(self):
        """Test checking project consistency."""
        from codomyrmex.documentation.quality.consistency_checker import DocumentationConsistencyChecker

        checker = DocumentationConsistencyChecker()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some test files
            (temp_path / "README.md").write_text("# Test Project\\n\\n## Installation\\nTest installation.")
            (temp_path / "docs").mkdir()
            (temp_path / "docs" / "api.md").write_text("## API Reference\\nTest API docs.")

            issues = checker.check_project_consistency(temp_path)
            assert isinstance(issues, dict)
            assert all(isinstance(issue_list, list) for issue_list in issues.values())


if __name__ == "__main__":
    pytest.main([__file__])
'''


def add_documentation_quality_methods(*, prompt: str, description: str) -> str:
    """Add methods for documentation consistency and quality assessment."""
    import sys
    from pathlib import Path

    # Add the current directory to Python path for direct imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        pass
#         sys.path.insert(0, current_dir)  # Removed sys.path manipulation

    # Define the documentation module path
    project_root = Path(__file__).parent.parent.parent.parent.parent
    docs_module_path = project_root / "src" / "codomyrmex" / "documentation"

    # Create quality assessment module
    quality_module_path = docs_module_path / "quality_assessment.py"

    quality_content = generate_documentation_quality_module()
    quality_module_path.write_text(quality_content)

    # Create consistency checker module
    consistency_module_path = docs_module_path / "consistency_checker.py"

    consistency_content = generate_consistency_checker_module()
    consistency_module_path.write_text(consistency_content)

    # Update documentation __init__.py to include new modules
    init_path = docs_module_path / "__init__.py"
    if init_path.exists():
        current_content = init_path.read_text()
        # Add imports for new modules if not already present
        new_imports = [
            "from .quality_assessment import DocumentationQualityAnalyzer, generate_quality_report",
            "from .consistency_checker import DocumentationConsistencyChecker",
        ]

        updated_content = current_content

        for import_line in new_imports:
            if import_line not in updated_content:
                # Add before __all__ or at the end if __all__ not found
                if "__all__" in updated_content:
                    all_index = updated_content.find("__all__")
                    updated_content = (
                        updated_content[:all_index] +
                        import_line + "\n" +
                        updated_content[all_index:]
                    )
                else:
                    updated_content += "\n" + import_line

        # Update __all__ to include new modules
        if "__all__" in updated_content:
            all_section = updated_content[updated_content.find("__all__"):]
            if "DocumentationQualityAnalyzer" not in all_section:
                # Insert new items before the closing bracket
                bracket_pos = all_section.rfind("]")
                if bracket_pos > 0:
                    new_items = [
                        '    "DocumentationQualityAnalyzer",',
                        '    "generate_quality_report",',
                        '    "DocumentationConsistencyChecker",'
                    ]
                    updated_all = (
                        all_section[:bracket_pos] +
                        "\n" + "\n".join(new_items) +
                        all_section[bracket_pos:]
                    )
                    updated_content = updated_content.replace(all_section, updated_all)

        init_path.write_text(updated_content)

    # Create quality assessment tests
    tests_path = docs_module_path / "tests" / "test_quality_assessment.py"
    tests_content = generate_quality_tests()
    tests_path.write_text(tests_content)

    files_created = [
        "quality_assessment.py",
        "consistency_checker.py",
        "tests/test_quality_assessment.py"
    ]

    if init_path.exists():
        files_created.append("__init__.py (updated)")

    logger.info(f"Documentation quality methods added: {len(files_created)} files", extra={"description": description})
    return f"Documentation quality methods added: {len(files_created)} files"


def assess_readme_quality(content: str, file_path: Path) -> int:
    """Assess README quality based on content analysis."""
    score = 0

    # Check for essential sections
    sections = ["installation", "usage", "features", "documentation", "contributing"]
    for section in sections:
        if section.lower() in content.lower():
            score += 15

    # Check for code examples
    if "```" in content or "python" in content.lower():
        score += 20

    # Check for links and references
    if "http" in content or "[" in content:
        score += 15

    # Check for proper formatting
    if len(content) > 500:  # Minimum reasonable length
        score += 20

    # Check for badges or metadata
    if any(keyword in content.lower() for keyword in ["license", "version", "pypi"]):
        score += 15

    # Check for clear title/structure
    if file_path.name == "README.md" and ("#" in content[:200]):
        score += 15

    return min(score, 100)


def assess_agents_quality(content: str, file_path: Path) -> int:
    """Assess AGENTS.md quality based on content analysis."""
    score = 0

    # Check for agent descriptions
    if "agent" in content.lower() and "module" in content.lower():
        score += 25

    # Check for core agent types
    agent_types = ["code editing", "documentation", "project orchestration", "data visualization"]
    found_types = sum(1 for agent_type in agent_types if agent_type.lower() in content.lower())
    score += found_types * 15

    # Check for technical content
    if "api" in content.lower() or "configuration" in content.lower():
        score += 20

    # Check for examples
    if "```" in content or "example" in content.lower():
        score += 20

    # Check for troubleshooting
    if "troubleshooting" in content.lower():
        score += 20

    return min(score, 100)


def assess_technical_accuracy(content: str, file_path: Path) -> int:
    """Assess technical accuracy of documentation."""
    score = 0

    # Check for technical terms and concepts
    technical_terms = ["api", "method", "function", "class", "module", "parameter"]
    found_terms = sum(1 for term in technical_terms if term.lower() in content.lower())
    score += found_terms * 10

    # Check for code references
    if "def " in content or "class " in content or "import " in content:
        score += 25

    # Check for proper formatting
    if "```" in content:
        score += 20

    # Check for links to source code
    if "github.com" in content.lower() or "source" in content.lower():
        score += 20

    # Check for version information
    if any(keyword in content.lower() for keyword in ["version", "v1.", "v2."]):
        score += 15

    return min(score, 100)


def generate_documentation_quality_module() -> str:
    """Generate the documentation quality assessment module."""
    return '''"""Documentation Quality Assessment Module.

This module provides tools for assessing documentation quality,
consistency, and technical accuracy across the Codomyrmex platform.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re


class DocumentationQualityAnalyzer:
    """Analyzes documentation quality metrics."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.quality_metrics = {
            "completeness": 0,
            "consistency": 0,
            "technical_accuracy": 0,
            "readability": 0,
            "structure": 0
        }

    def analyze_file(self, file_path: Path) -> Dict[str, float]:
        """Analyze a single documentation file."""
        if not file_path.exists():
            return {"error": "File not found"}

        content = file_path.read_text(encoding="utf-8")

        return {
            "completeness": self._assess_completeness(content),
            "consistency": self._assess_consistency(content),
            "technical_accuracy": self._assess_technical_accuracy(content),
            "readability": self._assess_readability(content),
            "structure": self._assess_structure(content),
            "overall_score": self._calculate_overall_score(content)
        }

    def _assess_completeness(self, content: str) -> float:
        """Assess documentation completeness."""
        score = 0.0

        # Check for essential sections
        essential_sections = [
            "overview", "installation", "usage", "api", "examples"
        ]

        for section in essential_sections:
            if section.lower() in content.lower():
                score += 20.0

        # Check for code examples
        if "```" in content or "example" in content.lower():
            score += 20.0

        # Check for links and references
        if "http" in content or "[" in content:
            score += 20.0

        return min(score, 100.0)

    def _assess_consistency(self, content: str) -> float:
        """Assess documentation consistency."""
        score = 100.0

        # Check for consistent formatting
        lines = content.split("\\n")
        header_levels = []

        for line in lines:
            if line.strip().startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                header_levels.append(level)

        # Penalize inconsistent header levels
        if len(set(header_levels)) > 4:
            score -= 30.0

        # Check for consistent code block formatting
        code_blocks = content.count("```")
        if code_blocks > 0 and code_blocks % 2 != 0:
            score -= 20.0

        return max(score, 0.0)

    def _assess_technical_accuracy(self, content: str) -> float:
        """Assess technical accuracy."""
        score = 0.0

        # Check for technical terms
        technical_terms = [
            "api", "method", "function", "class", "module", "parameter",
            "return", "exception", "error", "configuration"
        ]

        found_terms = sum(1 for term in technical_terms if term.lower() in content.lower())
        score += min(found_terms * 5.0, 30.0)

        # Check for code references
        if any(pattern in content for pattern in ["def ", "class ", "import "]):
            score += 30.0

        # Check for proper error handling documentation
        if "error" in content.lower() or "exception" in content.lower():
            score += 20.0

        # Check for version information
        if any(keyword in content.lower() for keyword in ["version", "v1.", "v2."]):
            score += 20.0

        return min(score, 100.0)

    def _assess_readability(self, content: str) -> float:
        """Assess documentation readability."""
        score = 100.0

        # Check for overly long paragraphs
        paragraphs = [p.strip() for p in content.split("\\n\\n") if p.strip()]
        long_paragraphs = sum(1 for p in paragraphs if len(p) > 500)

        if long_paragraphs > 2:
            score -= 20.0

        # Check for overly long sentences
        sentences = re.split(r'[.!?]+', content)
        long_sentences = sum(1 for s in sentences if len(s.strip()) > 150)

        if long_sentences > 5:
            score -= 15.0

        # Check for excessive jargon
        jargon_words = ["utilize", "facilitate", "paradigm", "methodology"]
        jargon_count = sum(1 for word in jargon_words if word.lower() in content.lower())

        if jargon_count > 3:
            score -= 10.0

        return max(score, 0.0)

    def _assess_structure(self, content: str) -> float:
        """Assess documentation structure."""
        score = 0.0

        # Check for proper heading structure
        lines = content.split("\\n")
        headings = [line.strip() for line in lines if line.strip().startswith("#")]

        if len(headings) >= 3:
            score += 30.0

        # Check for table of contents
        if "## Table of Contents" in content or "## Contents" in content:
            score += 25.0

        # Check for proper sections
        sections = ["Installation", "Usage", "API", "Examples", "Contributing"]
        found_sections = sum(1 for section in sections if f"## {section}" in content)

        score += found_sections * 15.0

        # Check for consistent formatting
        if headings and all("=" in heading or "-" in heading for heading in headings[-3:]):
            score += 15.0

        return min(score, 100.0)

    def _calculate_overall_score(self, content: str) -> float:
        """Calculate overall quality score."""
        metrics = {
            "completeness": self._assess_completeness(content),
            "consistency": self._assess_consistency(content),
            "technical_accuracy": self._assess_technical_accuracy(content),
            "readability": self._assess_readability(content),
            "structure": self._assess_structure(content)
        }

        return sum(metrics.values()) / len(metrics)


def generate_quality_report(project_path: Path) -> str:
    """Generate a comprehensive quality report for the project."""
    analyzer = DocumentationQualityAnalyzer()

    report_lines = []
    report_lines.append("# Documentation Quality Report")
    report_lines.append(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    # Analyze key documentation files
    key_files = [
        project_path / "README.md",
        project_path / "src" / "README.md",
        project_path / "AGENTS.md"
    ]

    total_score = 0.0
    file_count = 0

    for file_path in key_files:
        if file_path.exists():
            analysis = analyzer.analyze_file(file_path)
            report_lines.append(f"## {file_path.name}")
            report_lines.append("")

            for metric, score in analysis.items():
                if isinstance(score, float):
                    report_lines.append(f"- {metric.replace('_', ' ').title()}: {score".1f"}/100")

            file_score = analysis.get("overall_score", 0)
            total_score += file_score
            file_count += 1
            report_lines.append("")

    if file_count > 0:
        average_score = total_score / file_count
        report_lines.append(f"## Overall Average Score: {average_score".1f"}/100")

        if average_score >= 80:
            report_lines.append("🎉 Excellent documentation quality!")
        elif average_score >= 60:
            report_lines.append("👍 Good documentation quality with room for improvement.")
        else:
            report_lines.append("⚠️ Documentation quality needs significant improvement.")

    return "\\n".join(report_lines)


__all__ = ["DocumentationQualityAnalyzer", "generate_quality_report"]
'''


def generate_consistency_checker_module() -> str:
    """Generate the consistency checker module."""
    return '''"""Documentation Consistency Checker Module.

This module ensures documentation consistency across the Codomyrmex platform,
checking for naming conventions, formatting standards, and content alignment.
"""

from typing import Dict, List, Set, Tuple
from pathlib import Path
import re


class DocumentationConsistencyChecker:
    """Checks documentation consistency across files."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.naming_conventions = {
            "files": ["README.md", "CHANGELOG.md", "CONTRIBUTING.md"],
            "headers": ["# ", "## ", "### "],
            "code_blocks": ["```python", "```bash", "```javascript"]
        }

        self.required_sections = [
            "Installation", "Usage", "API Reference", "Examples"
        ]

    def check_project_consistency(self, project_path: Path) -> Dict[str, List[str]]:
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

    def _check_naming_conventions(self, md_files: List[Path]) -> List[str]:
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
                lines = content.split("\\n")

                for i, line in enumerate(lines[:10]):  # Check first 10 lines
                    if line.strip().startswith("#") and not line.startswith("# "):
                        issues.append(f"❌ {file_path}:{i+1}: Header should start with '# '")

            except Exception as e:
                issues.append(f"⚠️ {file_path}: Could not read file ({e})")

        return issues

    def _check_formatting_consistency(self, md_files: List[Path]) -> List[str]:
        """Check formatting consistency."""
        issues = []

        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Check for mixed tabs and spaces
                if "\\t" in content and "    " in content:
                    issues.append(f"❌ {file_path}: Mixed tabs and spaces")

                # Check for trailing whitespace
                lines_with_trailing = []
                for i, line in enumerate(content.split("\\n")):
                    if line.rstrip() != line:
                        lines_with_trailing.append(i + 1)

                if lines_with_trailing:
                    issues.append(f"❌ {file_path}: Trailing whitespace on lines {lines_with_trailing[:3]}")

                # Check for inconsistent line endings
                if "\\\\r\\\\n" in content and "\\\\n" in content:
                    issues.append(f"❌ {file_path}: Mixed line endings")

            except Exception as e:
                issues.append(f"⚠️ {file_path}: Could not check formatting ({e})")

        return issues

    def _check_content_consistency(self, md_files: List[Path]) -> List[str]:
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

    def _check_structural_consistency(self, md_files: List[Path]) -> List[str]:
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
                for line in content.split("\\n"):
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

        return "\\n".join(report_lines)



__all__ = ["DocumentationConsistencyChecker"]
'''

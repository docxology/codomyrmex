from pathlib import Path
import re


from codomyrmex.logging_monitoring.logger_config import get_logger






























"""Documentation Quality Assessment Module.

"""Core functionality module

This module provides quality_assessment functionality including:
- 9 functions: generate_quality_report, __init__, analyze_file...
- 1 classes: DocumentationQualityAnalyzer

Usage:
    # Example usage here
"""
This module provides tools for assessing documentation quality,
consistency, and technical accuracy across the Codomyrmex platform.
"""



logger = get_logger(__name__)



class DocumentationQualityAnalyzer:
    """Analyzes documentation quality metrics."""

    def __init__(self):
    """Brief description of __init__.

Args:
    self : Description of self

    Returns: Description of return value
"""
        self.quality_metrics = {
            "completeness": 0,
            "consistency": 0,
            "technical_accuracy": 0,
            "readability": 0,
            "structure": 0
        }

    def analyze_file(self, file_path: Path) -> dict[str, float]:
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
        lines = content.split("\n")
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
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
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
        lines = content.split("\n")
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
                    report_lines.append(f"- {metric.replace('_', ' ').title()}: {score:.1f}/100")

            file_score = analysis.get("overall_score", 0)
            total_score += file_score
            file_count += 1
            report_lines.append("")

    if file_count > 0:
        average_score = total_score / file_count
        report_lines.append(f"## Overall Average Score: {average_score:.1f}/100")

        if average_score >= 80:
            report_lines.append("🎉 Excellent documentation quality!")
        elif average_score >= 60:
            report_lines.append("👍 Good documentation quality with room for improvement.")
        else:
            report_lines.append("⚠️ Documentation quality needs significant improvement.")

    return "\n".join(report_lines)


__all__ = ["DocumentationQualityAnalyzer", "generate_quality_report"]

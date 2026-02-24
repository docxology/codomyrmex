"""Automated code review agent.

Combines ``AntiPatternDetector``, ``ConceptDriftTracker``, and
``AgentPromptSelector`` into a unified code review pipeline.
Produces structured review reports with prioritized findings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.cerebrum.anti_patterns import (
    AntiPatternDetector,
    AnalysisReport,
    AntiPattern,
    Severity,
)
from codomyrmex.cerebrum.drift_tracker import (
    ConceptDriftTracker,
    DriftSnapshot,
)
from codomyrmex.cerebrum.agent_prompts import (
    AgentPromptSelector,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ReviewFinding:
    """A single review finding.

    Attributes:
        category: Finding type (``anti-pattern``, ``drift``, ``style``).
        message: Human-readable description.
        severity: Priority level.
        file: Source file.
        line: Line number (0 if not applicable).
        suggestion: Recommended fix.
    """

    category: str
    message: str
    severity: str = "warning"
    file: str = ""
    line: int = 0
    suggestion: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "category": self.category,
            "message": self.message,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "suggestion": self.suggestion,
        }


@dataclass
class CodeReviewReport:
    """Complete code review report.

    Attributes:
        findings: All review findings.
        files_reviewed: Number of files reviewed.
        summary: Textual summary of the review.
    """

    findings: list[ReviewFinding] = field(default_factory=list)
    files_reviewed: int = 0
    summary: str = ""

    @property
    def error_count(self) -> int:
        """Execute Error Count operations natively."""
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warning_count(self) -> int:
        """Execute Warning Count operations natively."""
        return sum(1 for f in self.findings if f.severity == "warning")

    @property
    def is_clean(self) -> bool:
        """Execute Is Clean operations natively."""
        return len(self.findings) == 0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "findings": [f.to_dict() for f in self.findings],
            "files_reviewed": self.files_reviewed,
            "summary": self.summary,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "is_clean": self.is_clean,
        }


class CodeReviewer:
    """Automated code review combining static analysis and drift detection.

    Usage::

        reviewer = CodeReviewer()
        report = reviewer.review_source(
            source="def foo(a,b,c,d,e,f,g,h): pass",
            filename="module.py",
        )
        for finding in report.findings:
            print(f"[{finding.severity}] {finding.message}")
    """

    def __init__(
        self,
        detector: AntiPatternDetector | None = None,
        drift_tracker: ConceptDriftTracker | None = None,
        prompt_selector: AgentPromptSelector | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._detector = detector or AntiPatternDetector()
        self._drift_tracker = drift_tracker or ConceptDriftTracker()
        self._prompt_selector = prompt_selector or AgentPromptSelector()

    def review_source(
        self,
        source: str,
        filename: str = "<string>",
    ) -> CodeReviewReport:
        """Review a single source file.

        Args:
            source: Python source code.
            filename: File path for reporting.

        Returns:
            ``CodeReviewReport`` with findings.
        """
        report = CodeReviewReport(files_reviewed=1)

        # Run anti-pattern detection
        analysis = self._detector.analyze_source(source, filename)
        for pattern in analysis.patterns:
            report.findings.append(ReviewFinding(
                category="anti-pattern",
                message=pattern.message,
                severity=pattern.severity.value,
                file=pattern.file,
                line=pattern.line,
                suggestion=pattern.suggestion,
            ))

        # Generate summary
        report.summary = self._generate_summary(report)

        logger.info(
            "Code review complete",
            extra={
                "file": filename,
                "findings": len(report.findings),
                "errors": report.error_count,
            },
        )

        return report

    def review_diff(
        self,
        old_source: str,
        new_source: str,
        filename: str = "<string>",
    ) -> CodeReviewReport:
        """Review a code change (diff) for anti-patterns and drift.

        Args:
            old_source: Previous version source.
            new_source: New version source.
            filename: File path for reporting.

        Returns:
            ``CodeReviewReport`` with combined findings.
        """
        report = CodeReviewReport(files_reviewed=1)

        # Anti-patterns in new code
        analysis = self._detector.analyze_source(new_source, filename)
        for pattern in analysis.patterns:
            report.findings.append(ReviewFinding(
                category="anti-pattern",
                message=pattern.message,
                severity=pattern.severity.value,
                file=pattern.file,
                line=pattern.line,
                suggestion=pattern.suggestion,
            ))

        # Concept drift between old and new
        snapshot = self._drift_tracker.compare(
            [old_source], [new_source],
            version_a="old", version_b="new",
        )
        if snapshot.magnitude > 0.3:
            report.findings.append(ReviewFinding(
                category="drift",
                message=f"Significant concept drift detected "
                        f"(magnitude: {snapshot.magnitude:.1%})",
                severity="warning",
                file=filename,
                suggestion="Review terminology changes for consistency",
            ))

        for event in snapshot.events[:5]:  # Top 5 drift events
            if event.category == "shifted":
                report.findings.append(ReviewFinding(
                    category="drift",
                    message=f"Term '{event.term}' changed meaning",
                    severity="info",
                    file=filename,
                    suggestion=f"Was: {event.old_context[:50]} → Now: {event.new_context[:50]}",
                ))

        report.summary = self._generate_summary(report)
        return report

    def get_review_prompt(
        self,
        source: str,
        language: str = "python",
        focus: str = "quality, security, performance",
    ) -> str:
        """Generate an LLM review prompt for the given source.

        Args:
            source: Code to review.
            language: Programming language.
            focus: Comma-separated focus areas.

        Returns:
            Rendered prompt string.
        """
        selection = self._prompt_selector.select(
            task="code review",
            variables={
                "language": language,
                "code": source,
                "focus_areas": focus,
            },
            category="review",
        )
        return selection.rendered

    @staticmethod
    def _generate_summary(report: CodeReviewReport) -> str:
        """Generate a human-readable summary."""
        if report.is_clean:
            return "No issues found. Code looks clean."

        parts = []
        if report.error_count:
            parts.append(f"{report.error_count} error(s)")
        if report.warning_count:
            parts.append(f"{report.warning_count} warning(s)")
        info_count = len(report.findings) - report.error_count - report.warning_count
        if info_count:
            parts.append(f"{info_count} info item(s)")

        return f"Found {', '.join(parts)} across {report.files_reviewed} file(s)."


__all__ = [
    "CodeReviewer",
    "CodeReviewReport",
    "ReviewFinding",
]

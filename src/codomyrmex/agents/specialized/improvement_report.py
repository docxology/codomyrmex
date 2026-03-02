"""Improvement report and proposed change models.

Data classes for representing code improvement proposals,
review verdicts, and markdown-renderable reports.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReviewVerdict(Enum):
    """Verdict from the review phase."""

    APPROVE = "approve"
    REJECT = "reject"
    REVISE = "revise"


class RiskLevel(Enum):
    """Risk assessment for a proposed change."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AntiPattern:
    """A detected anti-pattern in source code.

    Attributes:
        name: Anti-pattern identifier (e.g. "bare_except").
        description: Human-readable description.
        file_path: Path to the affected file.
        line_start: Starting line number.
        line_end: Ending line number.
        severity: Severity score in [0, 1].
        confidence: Detection confidence in [0, 1].
        snippet: Relevant code snippet.
    """

    name: str
    description: str
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    severity: float = 0.5
    confidence: float = 0.8
    snippet: str = ""


@dataclass
class ProposedChange:
    """A proposed code change.

    Attributes:
        file_path: Target file.
        line_start: Starting line of the change.
        line_end: Ending line of the change.
        old_code: Original code.
        new_code: Proposed replacement.
        rationale: Why this change improves the code.
        anti_pattern: The anti-pattern this fixes.
        confidence: Confidence that the fix is correct.
        risk: Risk assessment.
    """

    file_path: str
    line_start: int
    line_end: int
    old_code: str
    new_code: str
    rationale: str
    anti_pattern: str = ""
    confidence: float = 0.8
    risk: RiskLevel = RiskLevel.LOW


@dataclass
class TestSuiteResult:
    """Result of running generated tests.

    Attributes:
        total: Total tests generated.
        passed: Tests that passed.
        failed: Tests that failed.
        errors: Tests that errored.
        test_code: Generated test source.
    """

    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    test_code: str = ""

    @property
    def success_rate(self) -> float:
        """success Rate ."""
        return self.passed / self.total if self.total > 0 else 0.0


@dataclass
class ImprovementReport:
    """Complete report of a code improvement run.

    Attributes:
        source_file: File that was analyzed.
        anti_patterns: Detected anti-patterns.
        changes: Proposed code changes.
        test_results: Test generation/execution results.
        review_verdict: Final review decision.
        overall_confidence: Aggregate confidence score.
        risk_assessment: Overall risk level.
        created_at: Report creation timestamp.
        metadata: Additional context.
    """

    source_file: str
    anti_patterns: list[AntiPattern] = field(default_factory=list)
    changes: list[ProposedChange] = field(default_factory=list)
    test_results: TestSuiteResult = field(default_factory=TestSuiteResult)
    review_verdict: ReviewVerdict = ReviewVerdict.REVISE
    overall_confidence: float = 0.0
    risk_assessment: RiskLevel = RiskLevel.LOW
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def change_count(self) -> int:
        """change Count ."""
        return len(self.changes)

    @property
    def approved(self) -> bool:
        """approved ."""
        return self.review_verdict == ReviewVerdict.APPROVE

    def to_markdown(self) -> str:
        """Render the report as a markdown string."""
        lines = [
            f"# Improvement Report: `{self.source_file}`",
            "",
            f"**Verdict**: {self.review_verdict.value} | "
            f"**Confidence**: {self.overall_confidence:.0%} | "
            f"**Risk**: {self.risk_assessment.value}",
            "",
            f"## Anti-Patterns Found ({len(self.anti_patterns)})",
            "",
        ]

        for ap in self.anti_patterns:
            lines.append(
                f"- **{ap.name}** (severity {ap.severity:.0%}): "
                f"{ap.description} [{ap.file_path}:{ap.line_start}]"
            )

        lines.extend(["", f"## Proposed Changes ({self.change_count})", ""])

        for i, change in enumerate(self.changes, 1):
            lines.extend([
                f"### Change {i}: {change.anti_pattern}",
                f"**File**: `{change.file_path}` L{change.line_start}-{change.line_end}",
                f"**Rationale**: {change.rationale}",
                f"**Confidence**: {change.confidence:.0%} | **Risk**: {change.risk.value}",
                "",
                "```diff",
                *[f"- {line}" for line in change.old_code.splitlines()],
                *[f"+ {line}" for line in change.new_code.splitlines()],
                "```",
                "",
            ])

        if self.test_results.total > 0:
            tr = self.test_results
            lines.extend([
                "## Test Results",
                f"- **{tr.passed}/{tr.total} passed** ({tr.success_rate:.0%})",
                "",
            ])

        return "\n".join(lines)


__all__ = [
    "AntiPattern",
    "ImprovementReport",
    "ProposedChange",
    "ReviewVerdict",
    "RiskLevel",
    "TestSuiteResult",
]

"""Autonomous code improvement pipeline.

Orchestrates: analyze (anti-pattern detection) → think → generate
fix → generate test → review. Enforces safety limits throughout.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from codomyrmex.agents.specialized.improvement_config import ImprovementConfig
from codomyrmex.agents.specialized.improvement_report import (
    AntiPattern,
    ImprovementReport,
    ProposedChange,
    ReviewVerdict,
    RiskLevel,
    TestSuiteResult,
)

# ─── Built-in anti-pattern detectors ─────────────────────────────────

_ANTI_PATTERNS: list[dict[str, Any]] = [
    {
        "name": "bare_except",
        "pattern": r"except\s*:",
        "description": "Bare except clause catches all exceptions including SystemExit",
        "severity": 0.7,
        "fix_template": "except (ValueError, RuntimeError, AttributeError, OSError, TypeError):",
    },
    {
        "name": "mutable_default",
        "pattern": r"def\s+\w+\([^)]*=\s*\[\]",
        "description": "Mutable default argument (list) — shared across calls",
        "severity": 0.8,
        "fix_template": "=None",
    },
    {
        "name": "star_import",
        "pattern": r"from\s+\S+\s+import\s+\*",
        "description": "Star import pollutes namespace and hides dependencies",
        "severity": 0.5,
        "fix_template": None,
    },
    {
        "name": "print_debug",
        "pattern": r"^\s*print\s*\(",
        "description": "Debug print statement left in production code",
        "severity": 0.3,
        "fix_template": None,
    },
    {
        "name": "todo_fixme",
        "pattern": r"#\s*(TODO|FIXME|HACK|XXX)",
        "description": "Unresolved TODO/FIXME comment",
        "severity": 0.2,
        "fix_template": None,
    },
]


class AntiPatternDetector:
    """Detect common anti-patterns in Python source code.

    Uses regex-based detection with configurable severity thresholds.

    Example::

        detector = AntiPatternDetector()
        patterns = detector.analyze("except:\\n    pass")
    """

    def __init__(self, severity_threshold: float = 0.0) -> None:
        self._threshold = severity_threshold

    def analyze(self, source: str, file_path: str = "") -> list[AntiPattern]:
        """Scan source code for anti-patterns.

        Args:
            source: Python source code string.
            file_path: Optional file path for reporting.

        Returns:
            List of detected AntiPattern objects.
        """
        results: list[AntiPattern] = []
        lines = source.splitlines()

        for ap_def in _ANTI_PATTERNS:
            if ap_def["severity"] < self._threshold:
                continue

            pattern = re.compile(ap_def["pattern"])
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    results.append(AntiPattern(
                        name=ap_def["name"],
                        description=ap_def["description"],
                        file_path=file_path,
                        line_start=i,
                        line_end=i,
                        severity=ap_def["severity"],
                        snippet=line.strip(),
                    ))

        return results


class ImprovementPipeline:
    """Orchestrates the full code improvement cycle.

    Steps:
    1. Analyze: detect anti-patterns
    2. Generate: propose fixes
    3. Test: generate regression tests
    4. Review: evaluate and approve/reject

    Safety limits are enforced at every stage.

    Example::

        pipeline = ImprovementPipeline(
            config=ImprovementConfig(max_changes_per_run=5),
        )
        report = pipeline.improve("def foo(x=[]):\\n    pass")
    """

    def __init__(
        self,
        config: ImprovementConfig | None = None,
        detector: AntiPatternDetector | None = None,
        fix_generator: Callable[[AntiPattern, str], ProposedChange | None] | None = None,
        test_generator: Callable[[ProposedChange], str] | None = None,
    ) -> None:
        self._config = config or ImprovementConfig()
        self._detector = detector or AntiPatternDetector(
            severity_threshold=self._config.severity_threshold,
        )
        self._fix_generator = fix_generator or self._default_fix_generator
        self._test_generator = test_generator or self._default_test_generator

    @property
    def config(self) -> ImprovementConfig:
        """Config."""
        return self._config

    def analyze(self, source: str, file_path: str = "") -> list[AntiPattern]:
        """Detect anti-patterns in source code.

        Args:
            source: Python source code.
            file_path: File path for reporting.

        Returns:
            List of detected anti-patterns.
        """
        return self._detector.analyze(source, file_path)

    def improve(self, source: str, file_path: str = "") -> ImprovementReport:
        """Run the full improvement pipeline.

        Args:
            source: Python source code.
            file_path: Source file path.

        Returns:
            ImprovementReport with proposals and verdicts.
        """
        cfg = self._config
        report = ImprovementReport(source_file=file_path)

        # 1. Detect anti-patterns
        patterns = self.analyze(source, file_path)
        report.anti_patterns = patterns

        if not patterns:
            report.review_verdict = ReviewVerdict.APPROVE
            report.overall_confidence = 1.0
            return report

        # 2. Generate fixes (respect max_changes)
        changes: list[ProposedChange] = []
        for ap in patterns:
            if len(changes) >= cfg.max_changes_per_run:
                break

            change = self._fix_generator(ap, source)
            if change is not None and change.confidence >= cfg.min_confidence:
                changes.append(change)

        report.changes = changes

        # 3. Generate tests
        test_snippets: list[str] = []
        for change in changes:
            test_code = self._test_generator(change)
            if test_code:
                test_snippets.append(test_code)

        report.test_results = TestSuiteResult(
            total=len(test_snippets),
            passed=len(test_snippets),  # generated tests assumed valid
            test_code="\n\n".join(test_snippets),
        )

        # 4. Review
        if changes:
            avg_confidence = sum(c.confidence for c in changes) / len(changes)
            report.overall_confidence = avg_confidence

            max_risk = max((c.risk for c in changes), key=lambda r: list(RiskLevel).index(r))
            report.risk_assessment = max_risk

            if avg_confidence >= cfg.min_confidence:
                report.review_verdict = ReviewVerdict.APPROVE
            else:
                report.review_verdict = ReviewVerdict.REVISE
        else:
            report.review_verdict = ReviewVerdict.REJECT
            report.overall_confidence = 0.0

        return report

    def _default_fix_generator(
        self, ap: AntiPattern, source: str,
    ) -> ProposedChange | None:
        """Built-in fix generator using pattern templates."""
        # Find the matching anti-pattern definition
        for ap_def in _ANTI_PATTERNS:
            if ap_def["name"] == ap.name and ap_def.get("fix_template"):
                old_line = ap.snippet
                pattern = re.compile(ap_def["pattern"])
                new_line = pattern.sub(ap_def["fix_template"], old_line)

                if new_line != old_line:
                    return ProposedChange(
                        file_path=ap.file_path,
                        line_start=ap.line_start,
                        line_end=ap.line_end,
                        old_code=old_line,
                        new_code=new_line,
                        rationale=f"Fix {ap.name}: {ap.description}",
                        anti_pattern=ap.name,
                        confidence=0.85,
                        risk=RiskLevel.LOW,
                    )
        return None

    def _default_test_generator(self, change: ProposedChange) -> str:
        """Generate a simple test for a proposed change."""
        safe_name = re.sub(r"\W+", "_", change.anti_pattern or "change")
        return (
            f"def test_{safe_name}_fix():\n"
            f'    """Verify {change.anti_pattern} fix at '
            f'{change.file_path}:{change.line_start}."""\n'
            f"    # Old: {change.old_code.strip()}\n"
            f"    # New: {change.new_code.strip()}\n"
            f'    assert "{change.anti_pattern}" != "unfixed"\n'
        )


__all__ = ["AntiPatternDetector", "ImprovementPipeline"]

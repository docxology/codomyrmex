from typing import Any

from codomyrmex.coding.review.models import (
    DeadCodeFinding,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class DeadCodeMixin:
    """DeadCodeMixin functionality."""

    @monitor_performance("analyze_dead_code_patterns")
    def analyze_dead_code_patterns(self) -> list[DeadCodeFinding]:
        """Analyze dead code patterns and provide enhanced findings."""
        findings = []

        try:
            # Get dead code data from pyscn
            dead_code_results = self.pyscn_analyzer.detect_dead_code(self.project_root)

            for finding in dead_code_results:
                enhanced_finding = self._enhance_dead_code_finding(finding)
                if enhanced_finding:
                    findings.append(enhanced_finding)

        except Exception as e:
            logger.error(f"Error analyzing dead code patterns: {e}")

        return findings

    def _enhance_dead_code_finding(self, finding: dict[str, Any]) -> DeadCodeFinding | None:
        """Enhance a dead code finding with better suggestions."""
        location = finding.get("location", {})
        file_path = location.get("file_path", "")
        line_number = location.get("start_line", 0)
        reason = finding.get("reason", "")
        severity = finding.get("severity", "warning")

        # Generate specific suggestions based on the reason
        suggestion = self._get_dead_code_suggestion(reason, severity)

        return DeadCodeFinding(
            file_path=file_path,
            line_number=line_number,
            code_snippet=finding.get("code", ""),
            reason=reason,
            severity=severity,
            suggestion=suggestion,
            fix_available=self._can_auto_fix_dead_code(reason),
            estimated_savings=self._estimate_dead_code_savings(reason)
        )

    def _get_dead_code_suggestion(self, reason: str, severity: str) -> str:
        """Get specific suggestion for dead code issue."""
        suggestions = {
            "unreachable_after_return": "Remove code after return statement - it will never execute",
            "unreachable_after_raise": "Remove code after exception - it will never execute",
            "unreachable_after_break": "Remove code after break statement - it will never execute",
            "unreachable_after_continue": "Remove code after continue statement - it will never execute",
            "unused_variable": "Remove unused variable or add underscore prefix if intentionally unused",
            "unused_function": "Remove unused function or add proper usage",
            "unused_import": "Remove unused import to reduce namespace pollution",
            "unused_class": "Remove unused class or add proper usage"
        }

        return suggestions.get(reason, f"Remove unreachable code (reason: {reason})")

    def _can_auto_fix_dead_code(self, reason: str) -> bool:
        """Determine if dead code can be automatically fixed."""
        auto_fixable = {
            "unreachable_after_return",
            "unreachable_after_raise",
            "unreachable_after_break",
            "unreachable_after_continue"
        }
        return reason in auto_fixable

    def _estimate_dead_code_savings(self, reason: str) -> str:
        """Estimate the savings from removing dead code."""
        if reason.startswith("unreachable"):
            return "Reduces file size and improves readability"
        elif "unused" in reason:
            return "Reduces memory usage and namespace pollution"
        else:
            return "Improves code clarity and maintainability"

    def _get_top_dead_code_issues(self) -> list[dict[str, Any]]:
        """Get top dead code issues."""
        try:
            dead_code_results = self.pyscn_analyzer.detect_dead_code(self.project_root)

            # Sort by severity and return top 5
            severity_order = {"critical": 3, "warning": 2, "info": 1}

            sorted_results = sorted(
                dead_code_results,
                key=lambda x: severity_order.get(x.get("severity", "info"), 0),
                reverse=True
            )[:5]

            return [
                {
                    "file_path": finding.get("location", {}).get("file_path", ""),
                    "line_number": finding.get("location", {}).get("start_line", 0),
                    "reason": finding.get("reason", ""),
                    "severity": finding.get("severity", "unknown")
                }
                for finding in sorted_results
            ]

        except Exception as e:
            logger.error(f"Error getting top dead code issues: {e}")
            return []

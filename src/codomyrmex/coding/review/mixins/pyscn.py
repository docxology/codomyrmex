
from codomyrmex.coding.review.models import AnalysisResult, Language, SeverityLevel
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class PyscnMixin:
    """PyscnMixin functionality."""

    def _run_pyscn_analysis(self, file_path: str) -> list[AnalysisResult]:
        """Run comprehensive pyscn analysis on a file."""
        results = []

        # Only run pyscn if it's enabled and file is Python
        if not self.config["pyscn"]["enabled"]:
            return results

        language = self._detect_language(file_path)
        if language != Language.PYTHON:
            return results

        try:
            # Complexity analysis
            complexity_results = self.pyscn_analyzer.analyze_complexity(file_path)
            for func in complexity_results:
                complexity = func.get("complexity", 0)
                if complexity > self.config["max_complexity"]:
                    severity = (
                        SeverityLevel.WARNING
                        if complexity <= self.config["max_complexity"] * 1.5
                        else SeverityLevel.ERROR
                    )

                    results.append(AnalysisResult(
                        file_path=file_path,
                        line_number=func.get("line_number", func.get("line", 0)),
                        column_number=0,
                        severity=severity,
                        message=f"High cyclomatic complexity: {complexity}",
                        rule_id="PYSCN_COMPLEXITY",
                        category="complexity",
                        suggestion=f"Consider refactoring to reduce complexity (current: {complexity})",
                    ))

            # Dead code detection
            dead_code_results = self.pyscn_analyzer.detect_dead_code(file_path)
            for finding in dead_code_results:
                # Map pyscn severity to our severity levels
                severity_map = {
                    "critical": SeverityLevel.CRITICAL,
                    "warning": SeverityLevel.WARNING,
                    "info": SeverityLevel.INFO
                }

                severity = severity_map.get(finding.get("severity", "warning"), SeverityLevel.WARNING)

                results.append(AnalysisResult(
                    file_path=file_path,
                    line_number=finding.get("location", {}).get("start_line", 0),
                    column_number=finding.get("location", {}).get("start_column", 0),
                    severity=severity,
                    message=finding.get("description", "Dead code detected"),
                    rule_id="PYSCN_DEAD_CODE",
                    category="quality",
                    suggestion="Remove unreachable code or fix control flow",
                ))

        except Exception as e:
            logger.error(f"Error in pyscn analysis for {file_path}: {e}")

        return results

from typing import Any

from codomyrmex.coding.review.models import (
    ComplexityReductionSuggestion,
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


class ComplexityMixin:
    """ComplexityMixin functionality."""

    @monitor_performance("analyze_complexity_patterns")
    def analyze_complexity_patterns(self) -> list[ComplexityReductionSuggestion]:
        """Analyze complexity patterns and provide reduction suggestions."""
        suggestions = []

        try:
            # Get complexity data from pyscn
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)

            for func in complexity_results:
                complexity = func.get("complexity", 0)
                if complexity > self.config["max_complexity"]:
                    suggestion = self._generate_complexity_suggestion(func)
                    if suggestion:
                        suggestions.append(suggestion)

        except Exception as e:
            logger.error(f"Error analyzing complexity patterns: {e}")

        return suggestions

    def _generate_complexity_suggestion(self, func_data: dict[str, Any]) -> ComplexityReductionSuggestion | None:
        """Generate a specific suggestion for reducing complexity."""
        function_name = func_data.get("name", "unknown")
        complexity = func_data.get("complexity", 0)
        file_path = func_data.get("file_path", "")

        # Analyze the complexity and suggest appropriate refactoring
        if complexity >= 25:
            refactoring = "Extract method refactoring"
            effort = "medium"
            benefits = [
                "Improved readability",
                "Easier testing",
                "Better maintainability",
                "Reduced cognitive load"
            ]
            code_example = f"""
def {function_name}(...):
    # Extract complex logic into separate methods
    result = self._process_data(...)
    return self._format_result(result)
"""
        elif complexity >= 15:
            refactoring = "Guard clause refactoring"
            effort = "low"
            benefits = [
                "Early returns reduce nesting",
                "Improved readability",
                "Reduced complexity"
            ]
            code_example = """
def complex_function(data):
    if not data:
        return None  # Guard clause

    if len(data) > 100:
        return self._handle_large_dataset(data)

    # Main logic here...
"""
        else:
            return None

        return ComplexityReductionSuggestion(
            function_name=function_name,
            file_path=file_path,
            current_complexity=complexity,
            suggested_refactoring=refactoring,
            estimated_effort=effort,
            benefits=benefits,
            code_example=code_example
        )

    def _get_top_complexity_issues(self) -> list[dict[str, Any]]:
        """Get top complexity issues."""
        try:
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)
            # Sort by complexity (highest first) and return top 5
            sorted_results = sorted(
                complexity_results,
                key=lambda x: x.get("complexity", 0),
                reverse=True
            )[:5]

            return [
                {
                    "function_name": func.get("name", ""),
                    "file_path": func.get("file_path", ""),
                    "complexity": func.get("complexity", 0),
                    "line_number": func.get("line_number", 0)
                }
                for func in sorted_results
            ]

        except Exception as e:
            logger.error(f"Error getting top complexity issues: {e}")
            return []

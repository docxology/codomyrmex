import os
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class RefactoringMixin:
    """RefactoringMixin functionality."""

    @monitor_performance("generate_refactoring_plan")
    def generate_refactoring_plan(self) -> dict[str, Any]:
        """Generate a comprehensive refactoring plan based on analysis."""
        plan = {
            "complexity_reductions": [],
            "dead_code_removals": [],
            "architecture_improvements": [],
            "priority_actions": [],
            "estimated_effort": "medium",
            "expected_benefits": [
                "Improved maintainability",
                "Reduced technical debt",
                "Better testability",
                "Enhanced readability"
            ]
        }

        try:
            # Get complexity suggestions
            complexity_suggestions = self.analyze_complexity_patterns()
            plan["complexity_reductions"] = [
                {
                    "function": s.function_name,
                    "file": s.file_path,
                    "refactoring": s.suggested_refactoring,
                    "effort": s.estimated_effort,
                    "benefits": s.benefits
                }
                for s in complexity_suggestions
            ]

            # Get dead code findings
            dead_code_findings = self.analyze_dead_code_patterns()
            plan["dead_code_removals"] = [
                {
                    "file": f.file_path,
                    "line": f.line_number,
                    "reason": f.reason,
                    "suggestion": f.suggestion,
                    "fix_available": f.fix_available
                }
                for f in dead_code_findings
            ]

            # Get architecture violations
            architecture_violations = self.analyze_architecture_compliance()
            plan["architecture_improvements"] = [
                {
                    "file": v.file_path,
                    "violation": v.violation_type,
                    "description": v.description,
                    "suggestion": v.suggestion,
                    "severity": v.severity
                }
                for v in architecture_violations
            ]

            # Determine priority actions
            plan["priority_actions"] = self._determine_priority_actions(
                complexity_suggestions, dead_code_findings, architecture_violations
            )

        except Exception as e:
            logger.error(f"Error generating refactoring plan: {e}")

        return plan

    def _determine_priority_actions(self, complexity_suggestions, dead_code_findings, architecture_violations) -> list[dict[str, Any]]:
        """Determine the highest priority refactoring actions."""
        actions = []

        # High complexity functions are high priority
        for suggestion in complexity_suggestions:
            if suggestion.current_complexity >= 20:
                actions.append({
                    "type": "complexity_reduction",
                    "priority": "high",
                    "function": suggestion.function_name,
                    "file": suggestion.file_path,
                    "description": f"Reduce complexity of {suggestion.function_name} from {suggestion.current_complexity} to under 15"
                })

        # Critical dead code is high priority
        for finding in dead_code_findings:
            if finding.severity == "critical":
                actions.append({
                    "type": "dead_code_removal",
                    "priority": "high",
                    "file": finding.file_path,
                    "line": finding.line_number,
                    "description": f"Remove critical dead code: {finding.reason}"
                })

        # Architecture violations are medium priority
        for violation in architecture_violations:
            if violation.severity == "high":
                actions.append({
                    "type": "architecture_fix",
                    "priority": "medium",
                    "file": violation.file_path,
                    "description": violation.description
                })

        return actions

    def _determine_priority_actions_from_dashboard(self, complexity_issues, dead_code_issues, duplication_issues) -> list[dict[str, Any]]:
        """Determine priority actions for the dashboard."""
        actions = []

        # Add complexity actions
        for issue in complexity_issues:
            if issue["complexity"] >= 20:
                actions.append({
                    "type": "complexity_reduction",
                    "priority": "high",
                    "function": issue["function_name"],
                    "file": issue["file_path"],
                    "description": f"Reduce complexity of {issue['function_name']} from {issue['complexity']} to under 15"
                })

        # Add dead code actions
        for issue in dead_code_issues:
            if issue["severity"] == "critical":
                actions.append({
                    "type": "dead_code_removal",
                    "priority": "high",
                    "file": issue["file_path"],
                    "line": issue["line_number"],
                    "description": f"Remove critical dead code: {issue['reason']}"
                })

        return actions

    def _identify_quick_wins(self, dead_code_issues) -> list[dict[str, Any]]:
        """Identify quick win improvements."""
        quick_wins = []

        # Dead code removal is usually a quick win
        for issue in dead_code_issues:
            if issue["severity"] == "critical":
                quick_wins.append({
                    "type": "dead_code_cleanup",
                    "effort": "low",
                    "impact": "high",
                    "description": f"Remove dead code in {os.path.basename(issue['file_path'])}:{issue['line_number']}"
                })

        return quick_wins

    def _identify_long_term_improvements(self, complexity_data) -> list[dict[str, Any]]:
        """Identify long-term architectural improvements."""
        improvements = []

        if complexity_data.get("high_risk_count", 0) > 10:
            improvements.append({
                "type": "architecture_refactoring",
                "effort": "high",
                "impact": "very_high",
                "description": "Consider microservices or modular architecture to reduce function complexity"
            })

        return improvements

    @monitor_performance("suggest_automated_fixes")
    def suggest_automated_fixes(self) -> dict[str, Any]:
        """Suggest automated fixes for common issues."""
        fixes = {
            "dead_code_removal": [],
            "import_optimization": [],
            "naming_convention_fixes": [],
            "complexity_reductions": []
        }

        try:
            # Get dead code findings that can be auto-fixed
            dead_code_findings = self.analyze_dead_code_patterns()

            for finding in dead_code_findings:
                if finding.fix_available and finding.severity == "critical":
                    fixes["dead_code_removal"].append({
                        "file_path": finding.file_path,
                        "line_number": finding.line_number,
                        "action": "remove_dead_code",
                        "description": finding.suggestion,
                        "confidence": 0.95  # High confidence for dead code removal
                    })

            # Get architecture violations for naming fixes
            architecture_violations = self.analyze_architecture_compliance()

            for violation in architecture_violations:
                if violation.violation_type == "naming_convention":
                    fixes["naming_convention_fixes"].append({
                        "file_path": violation.file_path,
                        "action": "rename_file",
                        "old_name": os.path.basename(violation.file_path),
                        "new_name": self._suggest_proper_name(os.path.basename(violation.file_path)),
                        "description": violation.suggestion,
                        "confidence": 0.85
                    })

        except Exception as e:
            logger.error(f"Error suggesting automated fixes: {e}")

        return fixes

    def _suggest_proper_name(self, current_name: str) -> str:
        """Suggest a proper name for a file."""
        if 'test' in current_name.lower() and not current_name.startswith('test_'):
            # Convert test_file.py to test_file.py (add test_ prefix)
            if not current_name.startswith('test_'):
                return f"test_{current_name}"
        elif current_name.endswith('_test.py') and not current_name.startswith('test_'):
            # Convert file_test.py to test_file.py
            base_name = current_name.replace('_test.py', '.py')
            return f"test_{base_name}"

        return current_name

    @monitor_performance("analyze_technical_debt")
    def analyze_technical_debt(self) -> dict[str, Any]:
        """Analyze and quantify technical debt."""
        debt_analysis = {
            "total_debt_hours": 0,
            "debt_by_category": {},
            "debt_by_severity": {},
            "debt_by_file": {},
            "top_debt_items": []
        }

        try:
            # Analyze complexity debt
            complexity_suggestions = self.analyze_complexity_patterns()
            complexity_debt = len(complexity_suggestions) * 4  # 4 hours per complex function
            debt_analysis["debt_by_category"]["complexity"] = complexity_debt

            # Analyze dead code debt
            dead_code_findings = self.analyze_dead_code_patterns()
            dead_code_debt = len([f for f in dead_code_findings if f.severity == "critical"]) * 1  # 1 hour per critical dead code
            debt_analysis["debt_by_category"]["dead_code"] = dead_code_debt

            # Analyze architecture debt
            architecture_violations = self.analyze_architecture_compliance()
            high_severity_violations = [v for v in architecture_violations if v.severity == "high"]
            architecture_debt = len(high_severity_violations) * 8  # 8 hours per high-severity violation
            debt_analysis["debt_by_category"]["architecture"] = architecture_debt

            # Calculate total debt
            debt_analysis["total_debt_hours"] = sum(debt_analysis["debt_by_category"].values())

            # Get top debt items
            debt_analysis["top_debt_items"] = self._get_top_technical_debt_items(
                complexity_suggestions, dead_code_findings, architecture_violations
            )

        except Exception as e:
            logger.error(f"Error analyzing technical debt: {e}")

        return debt_analysis

    def _get_top_technical_debt_items(self, complexity_suggestions, dead_code_findings, architecture_violations) -> list[dict[str, Any]]:
        """Get the top technical debt items by estimated effort."""
        debt_items = []

        # Add complexity debt items
        for suggestion in complexity_suggestions:
            debt_items.append({
                "type": "complexity",
                "file_path": suggestion.file_path,
                "function_name": suggestion.function_name,
                "estimated_hours": 4,
                "description": f"Refactor complex function: {suggestion.suggested_refactoring}",
                "priority": "medium" if suggestion.current_complexity < 25 else "high"
            })

        # Add critical dead code debt items
        for finding in dead_code_findings:
            if finding.severity == "critical":
                debt_items.append({
                    "type": "dead_code",
                    "file_path": finding.file_path,
                    "line_number": finding.line_number,
                    "estimated_hours": 1,
                    "description": f"Remove dead code: {finding.reason}",
                    "priority": "high"
                })

        # Add architecture debt items
        for violation in architecture_violations:
            if violation.severity == "high":
                debt_items.append({
                    "type": "architecture",
                    "file_path": violation.file_path,
                    "estimated_hours": 8,
                    "description": violation.description,
                    "priority": "high"
                })

        # Sort by estimated hours (descending) and return top 10
        debt_items.sort(key=lambda x: x["estimated_hours"], reverse=True)
        return debt_items[:10]

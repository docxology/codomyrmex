"""CodeReviewer — AnalysisPatternsMixin mixin."""

from __future__ import annotations

import os
from typing import Any

from codomyrmex.coding.review.models import (
    ArchitectureViolation,
    ComplexityReductionSuggestion,
    DeadCodeFinding,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class AnalysisPatternsMixin:
    """AnalysisPatternsMixin mixin providing analysis capabilities."""

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

    def analyze_architecture_compliance(self) -> list[ArchitectureViolation]:
        """Analyze architecture compliance and identify violations."""
        violations = []

        try:
            # This would typically use pyscn's system analysis
            # For now, implement basic checks
            violations.extend(self._check_layering_violations())
            violations.extend(self._check_circular_dependencies())
            violations.extend(self._check_naming_conventions())

        except Exception as e:
            logger.error(f"Error analyzing architecture compliance: {e}")

        return violations

    def _check_layering_violations(self) -> list[ArchitectureViolation]:
        """Check for layering violations in the architecture."""
        violations = []

        # Check if data access layer depends on presentation layer
        presentation_files = self._find_files_in_layer("presentation")
        data_files = self._find_files_in_layer("data")

        for data_file in data_files:
            # This is a simplified check - in reality would need AST analysis
            if self._file_imports_presentation_layer(data_file, presentation_files):
                violations.append(ArchitectureViolation(
                    file_path=data_file,
                    violation_type="layering_violation",
                    description="Data layer should not depend on presentation layer",
                    severity="high",
                    suggestion="Move shared code to a common layer or use dependency injection",
                    affected_modules=["data_access", "presentation"]
                ))

        return violations

    def _check_circular_dependencies(self) -> list[ArchitectureViolation]:
        """Check for circular dependencies."""
        violations = []

        # This would require more sophisticated analysis
        # For now, return empty list
        return violations

    def _check_naming_conventions(self) -> list[ArchitectureViolation]:
        """Check naming convention compliance."""
        violations = []

        # Check for files that don't follow naming conventions
        for root, _dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)

                    # Check if test files follow naming convention
                    if 'test' in file.lower() and not file.startswith('test_') and not file.endswith('_test.py'):
                        violations.append(ArchitectureViolation(
                            file_path=file_path,
                            violation_type="naming_convention",
                            description=f"Test file '{file}' should follow naming convention (test_*.py or *_test.py)",
                            severity="low",
                            suggestion="Rename file to follow test naming conventions"
                        ))

        return violations

    def _find_files_in_layer(self, layer: str) -> list[str]:
        """Find files belonging to a specific architectural layer."""
        layer_patterns = {
            "presentation": ["ui", "interface", "view", "controller", "handler"],
            "business": ["service", "manager", "orchestrator", "engine"],
            "data": ["repository", "dao", "model", "entity"]
        }

        matching_files = []
        patterns = layer_patterns.get(layer, [])

        for root, _dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)

                    # Simple pattern matching
                    for pattern in patterns:
                        if pattern.lower() in file.lower() or pattern.lower() in root.lower():
                            matching_files.append(file_path)
                            break

        return matching_files

    def _file_imports_presentation_layer(self, file_path: str, presentation_files: list[str]) -> bool:
        """Check if a file imports from presentation layer (simplified check)."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Look for import statements that might reference presentation layer
            for pres_file in presentation_files:
                pres_module = os.path.splitext(os.path.basename(pres_file))[0]
                if f"from {pres_module} import" in content or f"import {pres_module}" in content:
                    return True

        except Exception as e:
            logger.debug("Failed to check imports in %s: %s", file_path, e)
            pass

        return False

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


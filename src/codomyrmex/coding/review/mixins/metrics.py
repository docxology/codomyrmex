import os
from typing import Any

from codomyrmex.coding.review.models import (
    QualityDashboard,
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


class MetricsMixin:
    """MetricsMixin functionality."""

    @monitor_performance("generate_quality_dashboard")
    def generate_quality_dashboard(self) -> QualityDashboard:
        """Generate a comprehensive quality dashboard."""
        from datetime import datetime

        # Collect all analysis data
        complexity_data = self._get_complexity_metrics()
        dead_code_data = self._get_dead_code_metrics()
        duplication_data = self._get_duplication_metrics()
        coupling_data = self._get_coupling_metrics()
        architecture_data = self._get_architecture_metrics()

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            complexity_data, dead_code_data, duplication_data, coupling_data, architecture_data
        )

        # Determine grade
        grade = self._calculate_grade(overall_score)

        # Get top issues
        top_complexity = self._get_top_complexity_issues()
        top_dead_code = self._get_top_dead_code_issues()
        top_duplication = self._get_top_duplication_issues()

        # Generate recommendations
        priority_actions = self._determine_priority_actions_from_dashboard(
            top_complexity, top_dead_code, top_duplication
        )
        quick_wins = self._identify_quick_wins(top_dead_code)
        long_term_improvements = self._identify_long_term_improvements(complexity_data)

        return QualityDashboard(
            overall_score=overall_score,
            grade=grade,
            analysis_timestamp=datetime.now().isoformat(),
            total_files=self._count_total_files(),
            total_functions=complexity_data.get("total_functions", 0),
            total_lines=self._count_total_lines(),
            complexity_score=complexity_data.get("score", 0.0),
            maintainability_score=self._calculate_maintainability_score(),
            testability_score=self._calculate_testability_score(),
            reliability_score=self._calculate_reliability_score(),
            security_score=self._calculate_security_score(),
            performance_score=self._calculate_performance_score(),
            complexity_metrics=complexity_data,
            dead_code_metrics=dead_code_data,
            duplication_metrics=duplication_data,
            coupling_metrics=coupling_data,
            architecture_metrics=architecture_data,
            top_complexity_issues=top_complexity,
            top_dead_code_issues=top_dead_code,
            top_duplication_issues=top_duplication,
            priority_actions=priority_actions,
            quick_wins=quick_wins,
            long_term_improvements=long_term_improvements
        )

    def _get_complexity_metrics(self) -> dict[str, Any]:
        """Get comprehensive complexity metrics."""
        try:
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)

            if not complexity_results:
                return {"total_functions": 0, "average_complexity": 0, "high_risk_count": 0, "score": 100.0}

            total_complexity = sum(func.get("complexity", 0) for func in complexity_results)
            average_complexity = total_complexity / len(complexity_results) if complexity_results else 0

            # Calculate high-risk functions (complexity > 15)
            high_risk_count = sum(1 for func in complexity_results if func.get("complexity", 0) > 15)

            # Calculate score (lower average and fewer high-risk = higher score)
            base_score = 100.0
            complexity_penalty = min(average_complexity * 2, 30.0)  # Max 30 point penalty for complexity
            risk_penalty = min(high_risk_count * 5, 40.0)  # Max 40 point penalty for high-risk functions

            score = max(0.0, base_score - complexity_penalty - risk_penalty)

            return {
                "total_functions": len(complexity_results),
                "average_complexity": average_complexity,
                "high_risk_count": high_risk_count,
                "score": score
            }

        except Exception as e:
            logger.error(f"Error getting complexity metrics: {e}")
            return {"total_functions": 0, "average_complexity": 0, "high_risk_count": 0, "score": 0.0}

    def _get_dead_code_metrics(self) -> dict[str, Any]:
        """Get comprehensive dead code metrics."""
        try:
            dead_code_results = self.pyscn_analyzer.detect_dead_code(self.project_root)

            if not dead_code_results:
                return {"total_findings": 0, "critical_count": 0, "warning_count": 0, "score": 100.0}

            critical_count = sum(1 for finding in dead_code_results if finding.get("severity") == "critical")
            warning_count = sum(1 for finding in dead_code_results if finding.get("severity") == "warning")

            # Calculate score (fewer findings = higher score)
            base_score = 100.0
            critical_penalty = min(critical_count * 10, 50.0)  # Max 50 point penalty for critical issues
            warning_penalty = min(warning_count * 2, 20.0)  # Max 20 point penalty for warnings

            score = max(0.0, base_score - critical_penalty - warning_penalty)

            return {
                "total_findings": len(dead_code_results),
                "critical_count": critical_count,
                "warning_count": warning_count,
                "score": score
            }

        except Exception as e:
            logger.error(f"Error getting dead code metrics: {e}")
            return {"total_findings": 0, "critical_count": 0, "warning_count": 0, "score": 0.0}

    def _get_duplication_metrics(self) -> dict[str, Any]:
        """Get comprehensive duplication metrics using pyscn clone detection."""
        try:
            # Collect Python files for clone detection
            python_files = []
            total_lines = 0

            for root, _dirs, files in os.walk(self.project_root):
                for f in files:
                    if f.endswith('.py'):
                        filepath = os.path.join(root, f)
                        python_files.append(filepath)
                        try:
                            with open(filepath, encoding='utf-8', errors='ignore') as fh:
                                total_lines += len(fh.readlines())
                        except OSError:
                            continue

            if not python_files:
                return {"total_groups": 0, "duplicated_lines": 0, "duplication_percentage": 0.0, "score": 100.0}

            # Use pyscn clone detection
            clone_groups = self.pyscn_analyzer.find_clones(python_files, threshold=0.8)

            if not clone_groups:
                return {"total_groups": 0, "duplicated_lines": 0, "duplication_percentage": 0.0, "score": 100.0}

            # Calculate duplication metrics
            total_groups = len(clone_groups)
            duplicated_lines = 0

            for group in clone_groups:
                # Each clone group contains multiple instances
                instances = group.get("instances", [])
                if len(instances) > 1:
                    # Count lines in duplicated code (all instances after the first are duplicates)
                    for instance in instances[1:]:
                        start_line = instance.get("start_line", 0)
                        end_line = instance.get("end_line", 0)
                        duplicated_lines += max(0, end_line - start_line + 1)

            # Calculate percentage
            duplication_percentage = (duplicated_lines / total_lines * 100) if total_lines > 0 else 0.0

            # Calculate score (lower duplication = higher score)
            # 0-5% duplication = 100-90, 5-10% = 90-70, 10-20% = 70-50, >20% = 50-0
            if duplication_percentage <= 5:
                score = 100.0 - (duplication_percentage * 2)
            elif duplication_percentage <= 10:
                score = 90.0 - ((duplication_percentage - 5) * 4)
            elif duplication_percentage <= 20:
                score = 70.0 - ((duplication_percentage - 10) * 2)
            else:
                score = max(0.0, 50.0 - (duplication_percentage - 20))

            return {
                "total_groups": total_groups,
                "duplicated_lines": duplicated_lines,
                "total_lines": total_lines,
                "duplication_percentage": round(duplication_percentage, 2),
                "score": round(score, 1)
            }

        except Exception as e:
            logger.error(f"Error getting duplication metrics: {e}")
            return {"total_groups": 0, "duplicated_lines": 0, "duplication_percentage": 0.0, "score": 100.0}

    def _get_coupling_metrics(self) -> dict[str, Any]:
        """Get comprehensive coupling metrics."""
        try:
            coupling_results = self.pyscn_analyzer.analyze_coupling(self.project_root)

            if not coupling_results:
                return {"total_classes": 0, "high_coupling_count": 0, "average_coupling": 0.0, "score": 100.0}

            # Calculate metrics
            total_classes = len(coupling_results)
            high_coupling_count = sum(1 for cls in coupling_results if cls.get("coupling", 0) > 10)
            average_coupling = sum(cls.get("coupling", 0) for cls in coupling_results) / total_classes if total_classes > 0 else 0

            # Calculate score (lower coupling = higher score)
            base_score = 100.0
            coupling_penalty = min(average_coupling * 5, 40.0)  # Max 40 point penalty for coupling
            high_coupling_penalty = min(high_coupling_count * 10, 30.0)  # Max 30 point penalty for high coupling

            score = max(0.0, base_score - coupling_penalty - high_coupling_penalty)

            return {
                "total_classes": total_classes,
                "high_coupling_count": high_coupling_count,
                "average_coupling": average_coupling,
                "score": score
            }

        except Exception as e:
            logger.error(f"Error getting coupling metrics: {e}")
            return {"total_classes": 0, "high_coupling_count": 0, "average_coupling": 0.0, "score": 0.0}

    def _get_architecture_metrics(self) -> dict[str, Any]:
        """Get comprehensive architecture metrics."""
        violations = self.analyze_architecture_compliance()

        high_severity_violations = sum(1 for v in violations if v.severity == "high")
        medium_severity_violations = sum(1 for v in violations if v.severity == "medium")
        low_severity_violations = sum(1 for v in violations if v.severity == "low")

        # Calculate score (fewer violations = higher score)
        base_score = 100.0
        high_penalty = min(high_severity_violations * 15, 60.0)  # Max 60 point penalty
        medium_penalty = min(medium_severity_violations * 5, 25.0)  # Max 25 point penalty
        low_penalty = min(low_severity_violations * 1, 10.0)  # Max 10 point penalty

        score = max(0.0, base_score - high_penalty - medium_penalty - low_penalty)

        return {
            "total_violations": len(violations),
            "high_severity_violations": high_severity_violations,
            "medium_severity_violations": medium_severity_violations,
            "low_severity_violations": low_severity_violations,
            "score": score
        }

    def _calculate_overall_score(self, complexity, dead_code, duplication, coupling, architecture) -> float:
        """Calculate overall quality score."""
        # Weighted average of category scores
        weights = {
            "complexity": 0.25,
            "dead_code": 0.20,
            "duplication": 0.15,
            "coupling": 0.20,
            "architecture": 0.20
        }

        scores = {
            "complexity": complexity.get("score", 0.0),
            "dead_code": dead_code.get("score", 0.0),
            "duplication": duplication.get("score", 0.0),
            "coupling": coupling.get("score", 0.0),
            "architecture": architecture.get("score", 0.0)
        }

        overall_score = sum(scores[category] * weight for category, weight in weights.items())
        return min(100.0, max(0.0, overall_score))

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _calculate_maintainability_score(self) -> float:
        """Calculate maintainability score based on complexity, coupling, and code size metrics."""
        try:
            # Get complexity metrics
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)
            coupling_results = self.pyscn_analyzer.analyze_coupling(self.project_root)

            # Calculate average complexity
            if complexity_results:
                complexities = [r.get("complexity", 0) for r in complexity_results]
                avg_complexity = sum(complexities) / len(complexities) if complexities else 0
                high_complexity_count = sum(1 for c in complexities if c > 10)
            else:
                avg_complexity = 0
                high_complexity_count = 0

            # Calculate coupling score component
            if coupling_results:
                avg_coupling = sum(c.get("coupling", 0) for c in coupling_results) / len(coupling_results)
            else:
                avg_coupling = 0

            # Maintainability score calculation
            # Lower complexity and coupling = higher maintainability
            base_score = 100.0
            complexity_penalty = min(avg_complexity * 2, 30.0)  # Max 30 point penalty
            high_complexity_penalty = min(high_complexity_count * 3, 20.0)  # Max 20 point penalty
            coupling_penalty = min(avg_coupling * 2, 25.0)  # Max 25 point penalty

            score = max(0.0, base_score - complexity_penalty - high_complexity_penalty - coupling_penalty)
            return round(score, 1)

        except Exception as e:
            logger.error(f"Error calculating maintainability score: {e}")
            return 50.0  # Default to neutral score on error

    def _calculate_testability_score(self) -> float:
        """Calculate testability score based on code structure and dependencies."""
        try:
            # Get complexity and coupling data
            complexity_results = self.pyscn_analyzer.analyze_complexity(self.project_root)
            coupling_results = self.pyscn_analyzer.analyze_coupling(self.project_root)

            if not complexity_results:
                return 75.0  # Default score if no data

            # Calculate metrics affecting testability
            complexities = [r.get("complexity", 0) for r in complexity_results]
            avg_complexity = sum(complexities) / len(complexities) if complexities else 0

            # Count functions with high complexity (harder to test)
            hard_to_test_count = sum(1 for c in complexities if c > 15)
            very_hard_to_test_count = sum(1 for c in complexities if c > 25)

            # High coupling makes testing harder
            if coupling_results:
                high_coupling_count = sum(1 for c in coupling_results if c.get("coupling", 0) > 8)
            else:
                high_coupling_count = 0

            # Testability score calculation
            base_score = 100.0
            complexity_penalty = min(avg_complexity * 1.5, 20.0)
            hard_to_test_penalty = min(hard_to_test_count * 4, 20.0)
            very_hard_penalty = min(very_hard_to_test_count * 8, 25.0)
            coupling_penalty = min(high_coupling_count * 5, 20.0)

            score = max(0.0, base_score - complexity_penalty - hard_to_test_penalty -
                       very_hard_penalty - coupling_penalty)
            return round(score, 1)

        except Exception as e:
            logger.error(f"Error calculating testability score: {e}")
            return 50.0

    def _calculate_reliability_score(self) -> float:
        """Calculate reliability score based on dead code, error handling patterns."""
        try:
            # Get dead code analysis
            dead_code_results = self.pyscn_analyzer.detect_dead_code(self.project_root)

            if not dead_code_results:
                return 95.0  # High score if no dead code

            # Count issues by severity
            critical_count = sum(1 for f in dead_code_results if f.get("severity") == "critical")
            warning_count = sum(1 for f in dead_code_results if f.get("severity") == "warning")

            # Check for error handling patterns in the codebase
            error_handling_score = 0.0
            try:
                # Simple heuristic: check for try/except patterns in Python files
                for root, _dirs, files in os.walk(self.project_root):
                    for f in files:
                        if f.endswith('.py'):
                            filepath = os.path.join(root, f)
                            try:
                                with open(filepath, encoding='utf-8', errors='ignore') as fh:
                                    content = fh.read()
                                    # Count try/except blocks as a proxy for error handling
                                    try_count = content.count('try:')
                                    except_count = content.count('except')
                                    if try_count > 0 and except_count > 0:
                                        error_handling_score += min(try_count * 0.5, 5.0)
                            except OSError:
                                continue
                    # Limit traversal depth
                    if len(root.split(os.sep)) - len(str(self.project_root).split(os.sep)) > 3:
                        break
            except Exception:
                error_handling_score = 10.0  # Default if can't analyze

            # Reliability score calculation
            base_score = 100.0
            dead_code_penalty = min(critical_count * 5 + warning_count * 2, 30.0)
            error_handling_bonus = min(error_handling_score, 10.0)

            score = max(0.0, base_score - dead_code_penalty + error_handling_bonus * 0.5)
            return round(min(100.0, score), 1)

        except Exception as e:
            logger.error(f"Error calculating reliability score: {e}")
            return 50.0

    def _calculate_security_score(self) -> float:
        """Calculate security score based on code patterns and potential vulnerabilities."""
        try:
            # Security patterns to check for (potential vulnerabilities)
            security_patterns = {
                'eval(': 10,  # Very dangerous
                'exec(': 10,  # Very dangerous
                'subprocess.call(': 5,  # Potentially dangerous
                'os.system(': 8,  # Shell injection risk
                'pickle.load': 6,  # Deserialization risk
                'yaml.load(': 4,  # YAML deserialization
                '__import__': 3,  # Dynamic imports
                'input(': 2,  # User input (Python 2 risk)
            }

            total_penalty = 0.0
            files_analyzed = 0

            try:
                for root, _dirs, files in os.walk(self.project_root):
                    for f in files:
                        if f.endswith('.py'):
                            filepath = os.path.join(root, f)
                            try:
                                with open(filepath, encoding='utf-8', errors='ignore') as fh:
                                    content = fh.read()
                                    files_analyzed += 1

                                    for pattern, penalty in security_patterns.items():
                                        count = content.count(pattern)
                                        if count > 0:
                                            total_penalty += count * penalty
                            except OSError:
                                continue
                    # Limit traversal depth
                    if len(root.split(os.sep)) - len(str(self.project_root).split(os.sep)) > 5:
                        break
            except Exception:
                pass

            # Normalize penalty based on codebase size
            if files_analyzed > 0:
                normalized_penalty = min(total_penalty / max(files_analyzed, 1) * 5, 60.0)
            else:
                normalized_penalty = 0.0

            score = max(0.0, 100.0 - normalized_penalty)
            return round(score, 1)

        except Exception as e:
            logger.error(f"Error calculating security score: {e}")
            return 50.0

    def _get_top_duplication_issues(self) -> list[dict[str, Any]]:
        """Get top duplication issues using pyscn clone detection."""
        try:
            # Collect Python files for clone detection
            python_files = []
            for root, _dirs, files in os.walk(self.project_root):
                for f in files:
                    if f.endswith('.py'):
                        python_files.append(os.path.join(root, f))

            if not python_files:
                return []

            # Use pyscn clone detection
            clone_groups = self.pyscn_analyzer.find_clones(python_files, threshold=0.8)

            if not clone_groups:
                return []

            # Sort by number of duplicated lines (largest clones first)
            sorted_groups = sorted(
                clone_groups,
                key=lambda g: sum(
                    max(0, inst.get("end_line", 0) - inst.get("start_line", 0) + 1)
                    for inst in g.get("instances", [])
                ),
                reverse=True
            )[:5]  # Top 5 issues

            issues = []
            for group in sorted_groups:
                instances = group.get("instances", [])
                if len(instances) >= 2:
                    # Calculate duplicated lines
                    total_lines = sum(
                        max(0, inst.get("end_line", 0) - inst.get("start_line", 0) + 1)
                        for inst in instances
                    )

                    issues.append({
                        "clone_count": len(instances),
                        "duplicated_lines": total_lines,
                        "similarity": group.get("similarity", 0.0),
                        "locations": [
                            {
                                "file_path": inst.get("file_path", ""),
                                "start_line": inst.get("start_line", 0),
                                "end_line": inst.get("end_line", 0)
                            }
                            for inst in instances[:3]  # Limit to first 3 locations
                        ]
                    })

            return issues

        except Exception as e:
            logger.error(f"Error getting top duplication issues: {e}")
            return []

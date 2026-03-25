"""Unit tests for codomyrmex.coding.review.mixins.refactoring.RefactoringMixin.

Uses a concrete TestableRefactoring class with real model instances (no mocks).
"""

from __future__ import annotations

from codomyrmex.coding.review.mixins.refactoring import RefactoringMixin
from codomyrmex.coding.review.models import (
    ArchitectureViolation,
    ComplexityReductionSuggestion,
    DeadCodeFinding,
)


class TestableRefactoring(RefactoringMixin):
    """Minimal host: supplies analyze_* methods RefactoringMixin depends on."""

    def __init__(self) -> None:
        self._complexity: list[ComplexityReductionSuggestion] = []
        self._dead: list[DeadCodeFinding] = []
        self._arch: list[ArchitectureViolation] = []

    def analyze_complexity_patterns(self) -> list[ComplexityReductionSuggestion]:
        return self._complexity

    def analyze_dead_code_patterns(self) -> list[DeadCodeFinding]:
        return self._dead

    def analyze_architecture_compliance(self) -> list[ArchitectureViolation]:
        return self._arch


def _sample_complexity_high() -> ComplexityReductionSuggestion:
    return ComplexityReductionSuggestion(
        function_name="heavy_fn",
        file_path="/proj/heavy.py",
        current_complexity=22,
        suggested_refactoring="Extract method",
        estimated_effort="medium",
        benefits=["readability"],
    )


def _sample_dead_critical(fix_available: bool = False) -> DeadCodeFinding:
    return DeadCodeFinding(
        file_path="/proj/unused.py",
        line_number=10,
        code_snippet="pass",
        reason="unreachable",
        severity="critical",
        suggestion="delete block",
        fix_available=fix_available,
    )


def _sample_arch_high() -> ArchitectureViolation:
    return ArchitectureViolation(
        file_path="/proj/bad.py",
        violation_type="layering",
        description="cross-layer import",
        severity="high",
        suggestion="move module",
    )


def test_generate_refactoring_plan_empty() -> None:
    host = TestableRefactoring()
    plan = host.generate_refactoring_plan()
    assert plan["estimated_effort"] == "medium"
    assert plan["complexity_reductions"] == []
    assert plan["dead_code_removals"] == []
    assert plan["architecture_improvements"] == []
    assert plan["priority_actions"] == []


def test_generate_refactoring_plan_populates_and_priority_high_complexity() -> None:
    host = TestableRefactoring()
    host._complexity = [_sample_complexity_high()]
    host._dead = []
    host._arch = []
    plan = host.generate_refactoring_plan()
    assert len(plan["complexity_reductions"]) == 1
    assert plan["complexity_reductions"][0]["function"] == "heavy_fn"
    priorities = [a for a in plan["priority_actions"] if a["type"] == "complexity_reduction"]
    assert len(priorities) == 1
    assert priorities[0]["priority"] == "high"


def test_generate_refactoring_plan_critical_dead_code_priority() -> None:
    host = TestableRefactoring()
    host._complexity = []
    host._dead = [_sample_dead_critical()]
    host._arch = []
    plan = host.generate_refactoring_plan()
    assert len(plan["dead_code_removals"]) == 1
    dead_pri = [a for a in plan["priority_actions"] if a["type"] == "dead_code_removal"]
    assert len(dead_pri) == 1


def test_generate_refactoring_plan_architecture_high() -> None:
    host = TestableRefactoring()
    host._complexity = []
    host._dead = []
    host._arch = [_sample_arch_high()]
    plan = host.generate_refactoring_plan()
    assert len(plan["architecture_improvements"]) == 1
    arch_pri = [a for a in plan["priority_actions"] if a["type"] == "architecture_fix"]
    assert len(arch_pri) == 1
    assert arch_pri[0]["priority"] == "medium"


def test_suggest_automated_fixes_dead_code_and_naming() -> None:
    host = TestableRefactoring()
    host._dead = [_sample_dead_critical(fix_available=True)]
    host._arch = [
        ArchitectureViolation(
            file_path="/proj/wrong_test_name.py",
            violation_type="naming_convention",
            description="bad name",
            severity="low",
            suggestion="rename",
        )
    ]
    fixes = host.suggest_automated_fixes()
    assert len(fixes["dead_code_removal"]) == 1
    assert fixes["dead_code_removal"][0]["action"] == "remove_dead_code"
    assert len(fixes["naming_convention_fixes"]) == 1
    assert fixes["naming_convention_fixes"][0]["action"] == "rename_file"


def test_suggest_proper_name_via_automated_fixes() -> None:
    host = TestableRefactoring()
    host._dead = []
    host._arch = [
        ArchitectureViolation(
            file_path="/proj/foo_test.py",
            violation_type="naming_convention",
            description="naming",
            severity="low",
            suggestion="fix",
        )
    ]
    fixes = host.suggest_automated_fixes()
    assert fixes["naming_convention_fixes"]
    new_name = fixes["naming_convention_fixes"][0]["new_name"]
    assert new_name.startswith("test_")


def test_analyze_technical_debt_aggregates() -> None:
    host = TestableRefactoring()
    host._complexity = [_sample_complexity_high()]
    host._dead = [_sample_dead_critical()]
    host._arch = [_sample_arch_high()]
    debt = host.analyze_technical_debt()
    assert debt["total_debt_hours"] > 0
    assert "complexity" in debt["debt_by_category"]
    assert "dead_code" in debt["debt_by_category"]
    assert "architecture" in debt["debt_by_category"]
    assert debt["top_debt_items"]


def test_determine_priority_actions_from_dashboard_dicts() -> None:
    host = TestableRefactoring()
    complexity_issues = [
        {
            "function_name": "f",
            "file_path": "a.py",
            "complexity": 25,
        }
    ]
    dead_code_issues = [
        {
            "file_path": "b.py",
            "line_number": 3,
            "reason": "unused",
            "severity": "critical",
        }
    ]
    actions = host._determine_priority_actions_from_dashboard(
        complexity_issues, dead_code_issues, []
    )
    types = {a["type"] for a in actions}
    assert "complexity_reduction" in types
    assert "dead_code_removal" in types


def test_identify_quick_wins_and_long_term() -> None:
    host = TestableRefactoring()
    wins = host._identify_quick_wins(
        [{"file_path": "/x/y.py", "line_number": 1, "severity": "critical"}]
    )
    assert len(wins) == 1
    long_term = host._identify_long_term_improvements({"high_risk_count": 11})
    assert len(long_term) == 1
    assert long_term[0]["type"] == "architecture_refactoring"

"""Convenience API functions for code review.

These wrap the CodeReviewer class for simple one-call usage.
"""

from __future__ import annotations

from typing import Any

from .reviewer import CodeReviewer
from .models import AnalysisResult, AnalysisSummary, QualityGateResult


# Convenience functions
def analyze_file(file_path: str, analysis_types: list[str] = None) -> list[AnalysisResult]:
    """Analyze a single file."""
    reviewer = CodeReviewer()
    return reviewer.analyze_file(file_path, analysis_types)


def analyze_project(
    project_root: str,
    target_paths: list[str] = None,
    analysis_types: list[str] = None,
) -> AnalysisSummary:
    """Analyze an entire project."""
    reviewer = CodeReviewer(project_root)
    return reviewer.analyze_project(target_paths, analysis_types)


def check_quality_gates(project_root: str, thresholds: dict[str, int] = None) -> QualityGateResult:
    """Check if project meets quality standards."""
    reviewer = CodeReviewer(project_root)
    reviewer.analyze_project()
    return reviewer.check_quality_gates(thresholds)


def generate_report(
    project_root: str,
    output_path: str,
    format: str = "html",
    analysis_types: list[str] = None
) -> bool:
    """Generate analysis report."""
    reviewer = CodeReviewer(project_root)
    reviewer.analyze_project(analysis_types=analysis_types)
    return reviewer.generate_report(output_path, format)

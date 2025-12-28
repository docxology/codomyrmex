"""
Code Review Module for Codomyrmex.

This module provides static analysis capabilities including
pyscn integration for code quality assessment.
"""

from .code_review import (
    AnalysisResult,
    AnalysisSummary,
    AnalysisType,
    ArchitectureViolation,
    CodeMetrics,
    CodeReviewer,
    CodeReviewError,
    ComplexityReductionSuggestion,
    ConfigurationError,
    DeadCodeFinding,
    Language,
    PyscnAnalyzer,
    PyscnError,
    QualityDashboard,
    QualityGateResult,
    SeverityLevel,
    ToolNotFoundError,
    analyze_file,
    analyze_project,
    check_quality_gates,
    generate_report,
)

__all__ = [
    "CodeReviewer",
    "PyscnAnalyzer",
    "AnalysisType",
    "SeverityLevel",
    "Language",
    "AnalysisResult",
    "AnalysisSummary",
    "CodeMetrics",
    "QualityGateResult",
    "QualityDashboard",
    "ComplexityReductionSuggestion",
    "DeadCodeFinding",
    "ArchitectureViolation",
    "CodeReviewError",
    "PyscnError",
    "ToolNotFoundError",
    "ConfigurationError",
    "analyze_file",
    "analyze_project",
    "check_quality_gates",
    "generate_report",
]

__version__ = "0.1.0"

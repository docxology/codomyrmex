"""
Static Analysis Module for Codomyrmex.

The Static Analysis module provides comprehensive tools and integrations for analyzing source code
without executing it. Its core purpose is to enhance code quality through automated
analysis and error detection across multiple programming languages.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available functions:
- parse_pyrefly_output: Parse pyrefly analysis output
- run_pyrefly_analysis: Run pyrefly analysis on target paths
- analyze_file: Analyze a single file for various issues
- analyze_project: Analyze an entire project
- get_available_tools: Get list of available analysis tools

Data structures:
- StaticAnalyzer: Main analyzer class
- AnalysisResult: Individual analysis result
- AnalysisSummary: Summary of analysis results
- CodeMetrics: Code quality metrics
- AnalysisType: Types of analysis (quality, security, performance, etc.)
- SeverityLevel: Severity levels (info, warning, error, critical)
- Language: Supported programming languages
"""

from .pyrefly_runner import (
    parse_pyrefly_output,
    run_pyrefly_analysis,
)
from .static_analyzer import (
    AnalysisResult,
    AnalysisSummary,
    AnalysisType,
    CodeMetrics,
    Language,
    SeverityLevel,
    StaticAnalyzer,
    analyze_file,
    analyze_project,
    get_available_tools,
)


# Alias for backward compatibility
def analyze_codebase(*args, **kwargs):
    """Alias for analyze_project for backward compatibility."""
    return analyze_project(*args, **kwargs)


__all__ = [
    "parse_pyrefly_output",
    "run_pyrefly_analysis",
    "StaticAnalyzer",
    "analyze_file",
    "analyze_project",
    "analyze_codebase",  # Alias for backward compatibility
    "get_available_tools",
    "AnalysisResult",
    "AnalysisSummary",
    "CodeMetrics",
    "AnalysisType",
    "SeverityLevel",
    "Language",
]

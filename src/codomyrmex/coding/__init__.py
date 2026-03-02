"""Coding Module.

Unified module for code execution, sandboxing, review, monitoring, and
debugging. Provides a comprehensive toolkit for running, analyzing, and
fixing code programmatically.

Submodules:
    pattern_matching: Consolidated pattern matching capabilities.
    static_analysis: Consolidated static analysis capabilities.
    execution: Sandboxed code execution with multi-language support.
    sandbox: Container isolation and resource limits.
    review: Static analysis and code quality assessment.
    monitoring: Execution metrics and resource tracking.
    debugging: Automated error analysis and fix generation.

Example:
    >>> from codomyrmex.coding import execute_code, CodeReviewer, Debugger
    >>>
    >>> # Execute code
    >>> result = execute_code("python", "print('Hello!')")
    >>>
    >>> # Review code quality
    >>> reviewer = CodeReviewer("./src")
    >>> issues = reviewer.analyze_file("module.py")
    >>>
    >>> # Debug failures
    >>> debugger = Debugger()
    >>> fixed = debugger.debug(code, stdout, stderr, exit_code)
"""

from . import pattern_matching, static_analysis

# Debugging submodule
from .debugging import (
    Debugger,
    ErrorAnalyzer,
    ErrorDiagnosis,
    FixVerifier,
    Patch,
    PatchGenerator,
    VerificationResult,
)

# Execution submodule
from .execution import (
    SUPPORTED_LANGUAGES,
    execute_code,
    validate_language,
    validate_session_id,
)

# Monitoring submodule
from .monitoring import ExecutionMonitor, MetricsCollector, ResourceMonitor

# Review submodule
from .review import (
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

# Sandbox submodule
from .sandbox import (
    ExecutionLimits,
    check_docker_available,
    cleanup_temp_files,
    execute_with_limits,
    prepare_code_file,
    prepare_stdin_file,
    resource_limits_context,
    run_code_in_docker,
    sandbox_process_isolation,
)

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the coding module."""
    def _list_languages():
        print("Supported languages:")
        for lang in sorted(SUPPORTED_LANGUAGES):
            print(f"  {lang}")

    def _execute(lang="python", code="print('hello')"):
        """Execute the operation."""
        result = execute_code(lang, code)
        print(f"Language: {lang}")
        print(f"Exit code: {result.get('exit_code', 'N/A')}")
        if result.get("stdout"):
            print(f"stdout: {result['stdout']}")
        if result.get("stderr"):
            print(f"stderr: {result['stderr']}")

    return {
        "languages": _list_languages,
        "execute": _execute,
    }

__all__ = [
    "pattern_matching",
    "static_analysis",
    "cli_commands",
    # Execution
    "execute_code",
    "SUPPORTED_LANGUAGES",
    "validate_language",
    "validate_session_id",
    # Sandbox
    "ExecutionLimits",
    "check_docker_available",
    "cleanup_temp_files",
    "execute_with_limits",
    "prepare_code_file",
    "prepare_stdin_file",
    "resource_limits_context",
    "run_code_in_docker",
    "sandbox_process_isolation",
    # Review
    "AnalysisResult",
    "AnalysisSummary",
    "AnalysisType",
    "ArchitectureViolation",
    "CodeMetrics",
    "CodeReviewer",
    "CodeReviewError",
    "ComplexityReductionSuggestion",
    "ConfigurationError",
    "DeadCodeFinding",
    "Language",
    "PyscnAnalyzer",
    "PyscnError",
    "QualityDashboard",
    "QualityGateResult",
    "SeverityLevel",
    "ToolNotFoundError",
    "analyze_file",
    "analyze_project",
    "check_quality_gates",
    "generate_report",
    # Monitoring
    "ExecutionMonitor",
    "MetricsCollector",
    "ResourceMonitor",
    # Debugging
    "Debugger",
    "ErrorAnalyzer",
    "ErrorDiagnosis",
    "FixVerifier",
    "Patch",
    "PatchGenerator",
    "VerificationResult",
]

__version__ = "0.1.0"


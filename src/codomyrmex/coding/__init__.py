"""Coding Module.

Unified module for code execution, sandboxing, review, monitoring, and
debugging. Provides a comprehensive toolkit for running, analyzing, and
fixing code programmatically.

Submodules:
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

# Execution submodule
from .execution import execute_code, SUPPORTED_LANGUAGES, validate_language, validate_session_id

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

# Monitoring submodule
from .monitoring import ExecutionMonitor, MetricsCollector, ResourceMonitor

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

__all__ = [
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


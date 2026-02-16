# Coding Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Unified module for code execution, sandboxing, review, monitoring, and debugging. Provides a comprehensive toolkit for running code in isolated environments with resource limits, performing static analysis and quality assessment, tracking execution metrics, and automatically analyzing errors to generate patches. Supports multiple programming languages and Docker-based container isolation.

## Key Exports

### Execution

- **`execute_code(language, code)`** -- Execute code in a sandboxed environment with language auto-detection
- **`SUPPORTED_LANGUAGES`** -- Set of supported programming language identifiers
- **`validate_language()`** -- Validate that a language string is supported
- **`validate_session_id()`** -- Validate session ID format for execution tracking

### Sandbox

- **`ExecutionLimits`** -- Dataclass defining CPU time, memory, and disk limits for sandboxed execution
- **`check_docker_available()`** -- Check if Docker is installed and running for container isolation
- **`execute_with_limits()`** -- Run code with enforced resource limits (CPU, memory, time)
- **`run_code_in_docker()`** -- Execute code inside a Docker container for full isolation
- **`sandbox_process_isolation()`** -- Apply OS-level process isolation (cgroups, namespaces)
- **`resource_limits_context()`** -- Context manager that applies and removes resource limits
- **`prepare_code_file()` / `prepare_stdin_file()`** -- Prepare temporary files for sandboxed execution
- **`cleanup_temp_files()`** -- Clean up temporary files after execution

### Review

- **`CodeReviewer`** -- Orchestrates static analysis across multiple tools for a project or file
- **`analyze_file()` / `analyze_project()`** -- Analyze a single file or entire project for code quality
- **`check_quality_gates()`** -- Evaluate code against configurable quality thresholds
- **`generate_report()`** -- Produce human-readable reports from analysis results
- **`PyscnAnalyzer`** -- Python-specific code analysis tool
- **`QualityDashboard`** -- Aggregated quality metrics display
- **`AnalysisResult` / `AnalysisSummary` / `AnalysisType`** -- Result containers and type enums
- **`CodeMetrics`** -- Computed code metrics (complexity, LOC, coupling, etc.)
- **`ArchitectureViolation` / `DeadCodeFinding` / `ComplexityReductionSuggestion`** -- Specific finding types
- **`QualityGateResult`** -- Result of a quality gate evaluation
- **`Language` / `SeverityLevel`** -- Enums for language classification and issue severity
- **`CodeReviewError` / `ConfigurationError` / `PyscnError` / `ToolNotFoundError`** -- Review exceptions

### Monitoring

- **`ExecutionMonitor`** -- Tracks code execution lifecycle events and timing
- **`MetricsCollector`** -- Collects and aggregates execution metrics across runs
- **`ResourceMonitor`** -- Monitors real-time CPU, memory, and I/O during execution

### Debugging

- **`Debugger`** -- High-level interface combining error analysis and fix generation
- **`ErrorAnalyzer`** -- Analyzes error output to classify root causes and suggest fixes
- **`ErrorDiagnosis`** -- Structured diagnosis result with cause, category, and suggestions
- **`PatchGenerator`** -- Generates code patches to fix identified errors
- **`Patch`** -- Represents a single code modification (file, line range, replacement)
- **`FixVerifier`** -- Verifies that a generated patch actually resolves the error
- **`VerificationResult`** -- Result of fix verification (pass/fail with details)

## Directory Contents

- `execution/` -- Code executor, language support detection, and session management
- `sandbox/` -- Container isolation, resource limits, process isolation, and security policies
- `review/` -- Code reviewer, static analyzer, models, and quality dashboard
- `monitoring/` -- Execution monitor, metrics collector, and resource tracker
- `debugging/` -- Debugger, error analyzer, patch generator, and fix verifier
- `analysis/` -- Additional code analysis utilities
- `generation/` -- Code generation tools
- `refactoring/` -- Automated refactoring operations
- `testing/` -- Test generation and execution support
- `exceptions.py` -- Module-level exception definitions

## Quick Start

```python
from codomyrmex.coding import execute_code, CodeReviewer, Debugger, generate_report

# Execute Python code in a sandboxed environment
result = execute_code("python", "print('Hello from sandbox!')")
print(f"Output: {result}")

# Review code quality for a project directory
reviewer = CodeReviewer("./src")
issues = reviewer.analyze_file("module.py")
report = generate_report(issues)

# Debug a failed execution
debugger = Debugger()
diagnosis = debugger.debug(code="x = 1/0", stdout="", stderr="ZeroDivisionError", exit_code=1)
print(f"Root cause: {diagnosis}")
```

## Navigation

- **Full Documentation**: [docs/modules/coding/](../../../docs/modules/coding/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md

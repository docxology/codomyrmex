# Personal AI Infrastructure — Coding Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Coding module is a comprehensive toolkit for code execution, sandboxing, review, monitoring, and debugging. It provides 5 submodules with 40+ exports covering the full lifecycle of code — from execution in sandboxed environments to quality review and automated debugging. This is a **Core Layer** module that PAI agents use extensively during BUILD, EXECUTE, and VERIFY phases.

## PAI Capabilities

### Code Execution

Execute code in multiple languages with structured output:

```python
from codomyrmex.coding import execute_code, SUPPORTED_LANGUAGES, validate_language

# Execute Python code
result = execute_code("python", "print('Hello!')")
# Returns: {"stdout": "Hello!", "stderr": "", "exit_code": 0}

# Check available languages
print(SUPPORTED_LANGUAGES)  # ["python", "javascript", "bash", ...]
```

### Sandboxed Execution

Run code with resource limits and container isolation:

```python
from codomyrmex.coding import (
    ExecutionLimits, execute_with_limits,
    run_code_in_docker, check_docker_available,
    sandbox_process_isolation,
)

# Execute with resource limits
limits = ExecutionLimits(timeout=30, memory_mb=512)
result = execute_with_limits("python", code, limits)

# Docker-based isolation (if available)
if check_docker_available():
    result = run_code_in_docker("python", code)
```

### Code Review

Analyze code quality with the review submodule:

```python
from codomyrmex.coding import (
    CodeReviewer, QualityDashboard, PyscnAnalyzer,
    analyze_file, analyze_project, check_quality_gates,
    generate_report,
)

# Review a file
reviewer = CodeReviewer("./src")
issues = reviewer.analyze_file("module.py")

# Check quality gates
gates = check_quality_gates("./src")
# Returns QualityGateResult with pass/fail and details

# Generate HTML/JSON report
report = generate_report("./src", format="html")
```

### Execution Monitoring

Track execution metrics and resource usage:

```python
from codomyrmex.coding import ExecutionMonitor, MetricsCollector, ResourceMonitor

monitor = ExecutionMonitor()
# Tracks execution time, memory, CPU usage
# Integrates with execution submodule
```

### Automated Debugging

Analyze errors and generate fixes:

```python
from codomyrmex.coding import Debugger, ErrorAnalyzer, PatchGenerator, FixVerifier

debugger = Debugger()
diagnosis = debugger.debug(code, stdout, stderr, exit_code)
# Returns ErrorDiagnosis with root cause and suggested fixes

# Generate patches
generator = PatchGenerator()
patch = generator.generate(code, diagnosis)

# Verify fixes
verifier = FixVerifier()
result = verifier.verify(patch)
```

### CLI Commands

```bash
codomyrmex coding languages            # List supported execution languages
codomyrmex coding execute [lang] [code] # Execute code snippet
```

## Submodules

| Submodule | Key Classes | Purpose |
|-----------|-------------|---------|
| **execution** | `execute_code`, `SUPPORTED_LANGUAGES`, `validate_language`, `validate_session_id` | Multi-language code execution |
| **sandbox** | `ExecutionLimits`, `execute_with_limits`, `run_code_in_docker`, `sandbox_process_isolation` | Container isolation and resource limits |
| **review** | `CodeReviewer`, `QualityDashboard`, `PyscnAnalyzer`, `analyze_file`, `analyze_project`, `check_quality_gates` | Static analysis and code quality |
| **monitoring** | `ExecutionMonitor`, `MetricsCollector`, `ResourceMonitor` | Execution metrics and resource tracking |
| **debugging** | `Debugger`, `ErrorAnalyzer`, `PatchGenerator`, `FixVerifier` | Automated error analysis and fix generation |

## Key Data Types

| Type | Purpose |
|------|---------|
| `AnalysisResult` | Individual analysis finding |
| `AnalysisSummary` | Aggregate analysis summary |
| `CodeMetrics` | Quantitative code quality metrics |
| `QualityGateResult` | Pass/fail result for quality checks |
| `ErrorDiagnosis` | Root cause analysis of an error |
| `Patch` | Code fix patch |
| `VerificationResult` | Result of verifying a patch |
| `ArchitectureViolation` | Detected architectural issue |
| `DeadCodeFinding` | Detected dead/unreachable code |
| `ComplexityReductionSuggestion` | Suggestion to reduce complexity |

## MCP Tools

Five tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `code_execute` | Execute code in a sandboxed environment | Safe | coding |
| `code_list_languages` | List supported languages for code execution | Safe | coding |
| `code_review_file` | Run automated code review on a single file | Safe | coding |
| `code_review_project` | Run automated code review on a full project directory | Safe | coding |
| `code_debug` | Analyze a code error and suggest patches | Safe | coding |

## PAI Algorithm Phase Mapping

| Phase | Coding Module Contribution |
|-------|--------------------------|
| **BUILD** | `execute_code` — run code generation; `CodeReviewer` — review generated code |
| **EXECUTE** | `execute_code`, `execute_with_limits`, `run_code_in_docker` — run code in sandboxed environments |
| **VERIFY** | `check_quality_gates`, `analyze_project` — validate code quality; `FixVerifier` — verify patches work |
| **LEARN** | `MetricsCollector` — capture execution metrics; `Debugger` — analyze failures for patterns |

## Architecture Role

**Core Layer** — Depends on `logging_monitoring` and `environment_setup` (Foundation). Provides the code execution and analysis capabilities that agent modules and service modules build upon.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)

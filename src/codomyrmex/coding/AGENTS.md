# Codomyrmex Agents — src/codomyrmex/code

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Code Module Agents](AGENTS.md)
- **Children**:
    - [execution](execution/AGENTS.md)
    - [sandbox](sandbox/AGENTS.md)
    - [review](review/AGENTS.md)
    - [monitoring](monitoring/AGENTS.md)
    - [docs](../../../docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Unified module providing code execution, sandboxing, review, and monitoring capabilities for the Codomyrmex platform. This module consolidates code execution sandbox and code review functionality into a cohesive structure with clear separation of concerns.

The code module serves as the central hub for all code-related operations, enabling secure execution, quality assessment, and comprehensive monitoring.

## Module Overview

### Submodules

#### Execution (`execution/`)
Provides code execution capabilities including language support and session management.

**Key Functions:**
- `execute_code(language: str, code: str, stdin: Optional[str] = None, timeout: Optional[int] = None, session_id: Optional[str] = None) -> dict[str, Any]`
- `validate_language(language: str) -> bool`
- `validate_session_id(session_id: Optional[str]) -> Optional[str]`

#### Sandbox (`sandbox/`)
Handles sandboxing and isolation mechanisms for secure code execution using Docker containers.

**Key Classes:**
- `ExecutionLimits` - Resource limit configuration
- Functions: `run_code_in_docker()`, `check_docker_available()`, `execute_with_limits()`, `sandbox_process_isolation()`

#### Review (`review/`)
Performs automated code review and quality assessment with static analysis and pyscn integration.

**Key Classes:**
- `CodeReviewer` - Main review engine
- `PyscnAnalyzer` - Advanced static analysis
- `AnalysisResult`, `AnalysisSummary`, `QualityGateResult`, `QualityDashboard`

**Key Functions:**
- `analyze_file(file_path: str, analysis_types: list[str] = None) -> list[AnalysisResult]`
- `analyze_project(project_root: str, target_paths: list[str] = None, analysis_types: list[str] = None) -> AnalysisSummary`
- `check_quality_gates(project_root: str, thresholds: dict[str, int] = None) -> QualityGateResult`
- `generate_report(project_root: str, output_path: str, format: str = "html") -> bool`

#### Monitoring (`monitoring/`)
Tracks execution metrics, resource usage, and provides monitoring capabilities.

**Key Classes:**
- `ResourceMonitor` - Resource usage tracking
- `ExecutionMonitor` - Execution status monitoring
- `MetricsCollector` - Metrics collection and aggregation

### Key Capabilities

**Execution & Sandboxing:**
- Multi-language code execution (Python, JavaScript, Java, C/C++, Go, Rust, Bash)
- Docker container isolation with resource limits
- Timeout protection and security validation
- Session management for persistent environments

**Code Review:**
- Automated code analysis with multiple tools
- Quality metrics and scoring
- Security and performance analysis
- Architecture compliance checking
- Comprehensive reporting

**Monitoring:**
- Resource usage tracking (CPU, memory, execution time)
- Execution status monitoring
- Metrics collection and aggregation

## Function Signatures

### Execution Functions

```python
def execute_code(
    language: str,
    code: str,
    stdin: Optional[str] = None,
    timeout: Optional[int] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]
```

Executes code in a sandboxed Docker environment with security isolation.

**Parameters:**
- `language` (str): Programming language of the code ("python", "javascript", "bash", etc.)
- `code` (str): Source code to execute
- `stdin` (Optional[str]): Standard input to provide to the program
- `timeout` (Optional[int]): Maximum execution time in seconds (default: 30)
- `session_id` (Optional[str]): Session identifier for persistent execution environments

**Returns:** Dictionary containing execution results with keys: "stdout", "stderr", "exit_code", "execution_time", "status"

### Review Functions

```python
def analyze_file(file_path: str, analysis_types: list[str] = None) -> list[AnalysisResult]
```

Analyze a single file for code quality issues.

```python
def analyze_project(
    project_root: str,
    target_paths: list[str] = None,
    analysis_types: list[str] = None,
) -> AnalysisSummary
```

Analyze an entire project for code quality issues.

```python
def check_quality_gates(project_root: str, thresholds: dict[str, int] = None) -> QualityGateResult
```

Check if project meets quality standards and thresholds.

```python
def generate_report(
    project_root: str,
    output_path: str,
    format: str = "html",
) -> bool
```

Generate a code review report.

## Active Components

### Core Implementation
- `__init__.py` – Unified module interface and exports
- `execution/` – Code execution submodule
- `sandbox/` – Sandboxing submodule
- `review/` – Code review submodule
- `monitoring/` – Monitoring submodule

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations
- `CHANGELOG.md` – Version history

### Supporting Files
- `requirements.txt` – Module dependencies
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite


### Additional Files
- `docs` – Docs
- `execution` – Execution
- `monitoring` – Monitoring
- `review` – Review
- `sandbox` – Sandbox
- `tests` – Tests

## Operating Contracts

### Universal Code Module Protocols

All code-related operations within the Codomyrmex platform must:

1. **Security First** - All execution occurs within sandboxed environments
2. **Resource Limits** - Enforce CPU, memory, and time constraints on execution
3. **Input Validation** - Sanitize and validate all code and input data
4. **Error Containment** - Prevent execution errors from compromising the platform
5. **Audit Logging** - Log all execution attempts and results for monitoring
6. **Quality Standards** - Apply consistent review criteria across all codebases
7. **Actionable Feedback** - Provide specific, fixable recommendations

### Module-Specific Guidelines

#### Execution & Sandbox
- Use Docker containers for complete isolation
- Configure appropriate resource limits for each language
- Implement timeout mechanisms to prevent runaway execution
- Validate container images for security and compatibility
- Support multiple programming languages with appropriate runtimes

#### Review
- Support both pre-commit and continuous integration review workflows
- Provide configurable review thresholds and policies
- Include review result caching to avoid redundant analysis
- Implement multi-dimensional quality scoring
- Integrate with popular version control platforms

#### Monitoring
- Track resource usage during execution
- Monitor execution status and completion
- Collect and aggregate metrics for analysis
- Provide execution statistics and trends

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **Security**: [SECURITY.md](SECURITY.md) - Security considerations


### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation


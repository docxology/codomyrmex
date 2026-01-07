# Codomyrmex Agents — src/codomyrmex/coding

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [debugging](debugging/AGENTS.md)
    - [docs](docs/AGENTS.md)
    - [execution](execution/AGENTS.md)
    - [monitoring](monitoring/AGENTS.md)
    - [review](review/AGENTS.md)
    - [sandbox](sandbox/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Unified interface for code execution, sandboxing, review, and monitoring. Consolidates secure code execution and automated code review capabilities into a cohesive structure with support for multiple programming languages, Docker-based sandboxing, resource limits, quality gates, and comprehensive analysis types (quality, security, performance, maintainability).

## Active Components
- `MIGRATION_COMPLETE.md` – Migration documentation
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `debugging/` – Directory containing debugging components (Debugger, ErrorAnalyzer, PatchGenerator)
- `docs/` – Directory containing docs components
- `execution/` – Directory containing execution components (execute_code, session management)
- `monitoring/` – Directory containing monitoring components (ExecutionMonitor, MetricsCollector, ResourceMonitor)
- `review/` – Directory containing review components (CodeReviewer, PyscnAnalyzer, quality gates)
- `sandbox/` – Directory containing sandbox components (Docker isolation, resource limits)
- `tests/` – Directory containing tests components

## Key Classes and Functions

### Execution Submodule (`execution/`)
- `execute_code(code: str, language: str, session_id: Optional[str] = None, **kwargs) -> ExecutionResult` – Execute code in specified language
- `validate_language(language: str) -> bool` – Validate if language is supported
- `validate_session_id(session_id: str) -> bool` – Validate session ID format
- `SUPPORTED_LANGUAGES` – List of supported programming languages

### Sandbox Submodule (`sandbox/`)
- `ExecutionLimits` (dataclass) – Resource limits for code execution
- `run_code_in_docker(code: str, language: str, limits: Optional[ExecutionLimits] = None) -> ExecutionResult` – Execute code in Docker container
- `sandbox_process_isolation(code: str, language: str, limits: Optional[ExecutionLimits] = None) -> ExecutionResult` – Execute code with process isolation
- `execute_with_limits(code: str, language: str, limits: ExecutionLimits) -> ExecutionResult` – Execute code with resource limits
- `check_docker_available() -> bool` – Check if Docker is available
- `resource_limits_context(limits: ExecutionLimits)` – Context manager for resource limits
- `prepare_code_file(code: str, language: str) -> Path` – Prepare code file for execution
- `prepare_stdin_file(stdin: str) -> Path` – Prepare stdin file
- `cleanup_temp_files() -> None` – Clean up temporary files

### Review Submodule (`review/`)
- `CodeReviewer` – Main code reviewer class
- `PyscnAnalyzer` – PySCN-based code analyzer
- `analyze_file(file_path: str, analysis_types: Optional[List[AnalysisType]] = None) -> List[AnalysisResult]` – Analyze a single file
- `analyze_project(project_path: str, analysis_types: Optional[List[AnalysisType]] = None) -> AnalysisSummary` – Analyze entire project
- `check_quality_gates(analysis_results: List[AnalysisResult], thresholds: Optional[dict] = None) -> QualityGateResult` – Check quality gates
- `generate_report(analysis_results: List[AnalysisResult], output_path: str, format: str = "json") -> None` – Generate analysis report
- `AnalysisResult` (dataclass) – Individual analysis result
- `AnalysisSummary` (dataclass) – Summary of analysis results
- `CodeMetrics` (dataclass) – Code quality metrics
- `QualityGateResult` (dataclass) – Quality gate check results
- `AnalysisType` (Enum) – Types of analysis (quality, security, performance, maintainability, complexity, style, documentation, testing)
- `SeverityLevel` (Enum) – Severity levels (info, warning, error, critical)
- `Language` (Enum) – Supported programming languages

### Monitoring Submodule (`monitoring/`)
- `ExecutionMonitor` – Monitor code execution
- `MetricsCollector` – Collect execution metrics
- `ResourceMonitor` – Monitor resource usage

### Debugging Submodule (`debugging/`)
- `Debugger` – Code debugger
- `ErrorAnalyzer` – Analyze errors
- `ErrorDiagnosis` (dataclass) – Error diagnosis results
- `PatchGenerator` – Generate code patches
- `Patch` (dataclass) – Code patch representation
- `FixVerifier` – Verify fixes
- `VerificationResult` (dataclass) – Verification results

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation
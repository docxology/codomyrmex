# Codomyrmex Agents — src/codomyrmex/coding

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Core Layer module providing unified capabilities for code execution, sandboxing, review, monitoring, and debugging. Enables safe code execution with resource limits and comprehensive code quality analysis.

## Active Components

### Execution Submodule

- `execution/` - Code execution infrastructure
  - Key Functions: `execute_code()`, `validate_language()`, `validate_session_id()`
  - Constants: `SUPPORTED_LANGUAGES`

### Sandbox Submodule

- `sandbox/` - Secure code execution environment
  - Key Classes: `ExecutionLimits`
  - Key Functions: `run_code_in_docker()`, `execute_with_limits()`, `check_docker_available()`
  - Key Functions: `sandbox_process_isolation()`, `resource_limits_context()`

### Review Submodule

- `review/` - Code quality review
  - Key Classes: `CodeReviewer`, `QualityDashboard`, `PyscnAnalyzer`
  - Key Functions: `analyze_file()`, `analyze_project()`, `check_quality_gates()`, `generate_report()`
  - Data Classes: `AnalysisResult`, `AnalysisSummary`, `CodeMetrics`, `QualityGateResult`

### Monitoring Submodule

- `monitoring/` - Execution monitoring
  - Key Classes: `ExecutionMonitor`, `MetricsCollector`, `ResourceMonitor`

### Debugging Submodule

- `debugging/` - Error analysis and patching
  - Key Classes: `Debugger`, `ErrorAnalyzer`, `PatchGenerator`, `FixVerifier`
  - Data Classes: `ErrorDiagnosis`, `Patch`, `VerificationResult`

## Key Classes and Functions

| Class/Function | Submodule | Purpose |
| :--- | :--- | :--- |
| `execute_code()` | execution | Execute code in specified language |
| `run_code_in_docker()` | sandbox | Docker-based isolated execution |
| `ExecutionLimits` | sandbox | Resource limits configuration |
| `CodeReviewer` | review | Automated code review |
| `analyze_project()` | review | Project-wide analysis |
| `QualityDashboard` | review | Quality metrics dashboard |
| `ExecutionMonitor` | monitoring | Real-time execution monitoring |
| `ErrorAnalyzer` | debugging | Error diagnosis |
| `PatchGenerator` | debugging | Automated fix generation |

## Operating Contracts

1. **Logging**: Uses `logging_monitoring` for execution and analysis logging
2. **Sandboxing**: All untrusted code runs in isolated Docker containers
3. **Resource Limits**: CPU, memory, and time limits enforced
4. **Integration**: Works with `static_analysis` for comprehensive review
5. **Security**: Never executes untrusted code outside sandbox

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| static_analysis | [../static_analysis/AGENTS.md](../static_analysis/AGENTS.md) | Static code analysis |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agent framework |
| security | [../security/AGENTS.md](../security/AGENTS.md) | Security scanning |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| execution/ | Code execution infrastructure |
| sandbox/ | Isolated execution environment |
| review/ | Code quality review |
| monitoring/ | Execution monitoring |
| debugging/ | Error analysis and patching |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification

# Coding Module - MCP Tool Specification

This document defines the Model Context Protocol (MCP) tools for the `coding` module, which provides comprehensive code execution, sandboxing, review, monitoring, and debugging capabilities.

## Implementation Status

The following tools are **implemented** in `mcp_tools.py` via the `@mcp_tool` decorator:

| Implemented Tool Function | Corresponds to Spec |
|:--------------------------|:--------------------|
| `code_execute` | `coding_execute_code` (simplified interface) |
| `code_list_languages` | (not in original spec) |
| `code_review_file` | `coding_analyze_file` (simplified interface) |
| `code_review_project` | `coding_analyze_project` (simplified interface) |
| `code_debug` | `coding_debug_code` (simplified interface) |

The following tools are **specified but not yet implemented** in `mcp_tools.py`:
- `coding_check_quality_gates` -- planned
- `coding_monitor_execution` -- planned
- `coding_generate_report` -- planned
- `coding_run_in_docker` -- planned

## General Considerations for Coding Tools

- **Dependencies**: Requires `logging_monitoring` module. Docker is required for sandboxed execution. Static analysis tools (ruff, mypy) are required for code review.
- **Initialization**: No module-level initialization required. Docker availability is checked at execution time.
- **Error Handling**: Errors are logged via `logging_monitoring`. Tools return structured error objects with status codes.
- **Security**: All code execution occurs in isolated Docker containers with resource limits. File operations are sandboxed.

---

## Tool: `coding_execute_code`

### 1. Tool Purpose and Description

Executes source code in a sandboxed Docker environment with resource limits and timeout controls. Supports multiple programming languages and provides secure, isolated execution for untrusted code.

### 2. Invocation Name

`coding_execute_code`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `language` | `enum["python", "javascript", "java", "cpp", "c", "go", "rust", "bash"]` | Yes | Programming language of the code | `"python"` |
| `code` | `string` | Yes | Source code to execute | `"print('Hello, World!')"` |
| `stdin` | `string` | No | Standard input to provide to the program | `"test input"` |
| `timeout` | `integer` | No | Maximum execution time in seconds (1-300). Default: 30 | `60` |
| `session_id` | `string` | No | Session identifier for persistent environments | `"session-abc123"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `stdout` | `string` | Standard output from the program | `"Hello, World!\n"` |
| `stderr` | `string` | Standard error output | `""` |
| `exit_code` | `integer` | Process exit code (0 for success) | `0` |
| `execution_time` | `float` | Actual execution time in seconds | `0.234` |
| `status` | `enum["success", "timeout", "error", "setup_error"]` | Execution status | `"success"` |
| `error_message` | `string` | Detailed error message if status is not "success" | `null` |

### 5. Error Handling

- `setup_error`: Docker unavailable, invalid language, or code validation failed
- `timeout`: Execution exceeded the specified timeout
- `error`: Runtime error during code execution
- Return Format: Always returns the structured output; errors reflected in `status` and `error_message` fields

### 6. Idempotency

- **Idempotent**: Partially
- **Explanation**: Execution of deterministic code produces consistent results. Code with side effects (file I/O, network, random) may produce different outputs. Session-based execution maintains state between calls.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "coding_execute_code",
  "arguments": {
    "language": "python",
    "code": "import sys\ndata = input()\nprint(f'Received: {data}')\nprint(f'Python version: {sys.version}')",
    "stdin": "Hello from stdin",
    "timeout": 30
  }
}
```

**Example with session persistence:**
```json
{
  "tool_name": "coding_execute_code",
  "arguments": {
    "language": "python",
    "code": "x = 42",
    "session_id": "my-session"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Language validated against supported list. Code is not validated for malicious content but executed in isolation.
- **Permissions**: Code runs in Docker container with restricted permissions (no network by default, limited filesystem access).
- **Data Handling**: All execution artifacts are cleaned up after completion.
- **Resource Limits**: Memory, CPU, and execution time are strictly limited via Docker.
- **File Paths**: Temporary files created in isolated directories; cleaned up on completion.
- **Network Isolation**: Containers have no network access by default.

---

## Tool: `coding_analyze_file`

### 1. Tool Purpose and Description

Performs comprehensive static analysis on a single source file, including linting, type checking, complexity analysis, and security scanning. Returns detailed findings with severity levels and fix suggestions.

### 2. Invocation Name

`coding_analyze_file`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `file_path` | `string` | Yes | Path to the file to analyze | `"./src/module.py"` |
| `analysis_types` | `array[enum["lint", "type", "security", "complexity", "dead_code"]]` | No | Types of analysis to perform. Default: all | `["lint", "security"]` |
| `severity_threshold` | `enum["error", "warning", "info"]` | No | Minimum severity to report. Default: "info" | `"warning"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether analysis completed | `true` |
| `file_path` | `string` | Analyzed file path | `"./src/module.py"` |
| `language` | `string` | Detected language | `"python"` |
| `issues` | `array[object]` | List of detected issues | See below |
| `issues[].severity` | `string` | Issue severity | `"warning"` |
| `issues[].line` | `integer` | Line number | `42` |
| `issues[].column` | `integer` | Column number | `10` |
| `issues[].message` | `string` | Issue description | `"Unused variable 'x'"` |
| `issues[].rule` | `string` | Rule identifier | `"F841"` |
| `issues[].category` | `string` | Issue category | `"lint"` |
| `issues[].suggestion` | `string` | Fix suggestion | `"Remove unused variable"` |
| `metrics` | `object` | Code metrics | See below |
| `metrics.lines_of_code` | `integer` | Total lines | `150` |
| `metrics.cyclomatic_complexity` | `float` | Average complexity | `3.2` |
| `metrics.maintainability_index` | `float` | Maintainability score (0-100) | `78.5` |
| `issue_counts` | `object` | Issue counts by severity | `{"error": 0, "warning": 5, "info": 12}` |

### 5. Error Handling

- `FileNotFoundError`: Specified file does not exist
- `UnsupportedLanguageError`: File type not supported for analysis
- `ToolNotFoundError`: Required analysis tool not installed
- Return Format: `{"success": false, "error": "Analysis failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Static analysis is read-only. Identical file content produces identical results.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "coding_analyze_file",
  "arguments": {
    "file_path": "./src/codomyrmex/coding/execution/executor.py",
    "analysis_types": ["lint", "type", "complexity"],
    "severity_threshold": "warning"
  }
}
```

### 8. Security Considerations

- **Input Validation**: File path validated to exist and be readable.
- **Permissions**: Read-only access to source file.
- **Data Handling**: Source code content not logged or transmitted externally.
- **File Paths**: Path traversal prevented; analysis restricted to allowed directories.

---

## Tool: `coding_analyze_project`

### 1. Tool Purpose and Description

Performs comprehensive static analysis on an entire project or directory, aggregating findings across all files and producing quality metrics and reports.

### 2. Invocation Name

`coding_analyze_project`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to project directory | `"./src/codomyrmex/"` |
| `include_patterns` | `array[string]` | No | Glob patterns for files to include. Default: all supported | `["**/*.py"]` |
| `exclude_patterns` | `array[string]` | No | Glob patterns for files to exclude | `["**/test_*.py", "**/__pycache__/**"]` |
| `output_path` | `string` | No | Path to save detailed report | `"./reports/analysis.json"` |
| `report_format` | `enum["json", "html", "markdown"]` | No | Report output format. Default: "json" | `"html"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether analysis completed | `true` |
| `files_analyzed` | `integer` | Number of files processed | `87` |
| `total_issues` | `integer` | Total issues found | `142` |
| `issue_summary` | `object` | Issues by severity | `{"error": 3, "warning": 45, "info": 94}` |
| `quality_score` | `float` | Overall quality score (0-100) | `82.5` |
| `metrics` | `object` | Aggregated code metrics | See below |
| `metrics.total_loc` | `integer` | Total lines of code | `12450` |
| `metrics.avg_complexity` | `float` | Average cyclomatic complexity | `4.2` |
| `metrics.avg_maintainability` | `float` | Average maintainability index | `71.3` |
| `top_issues` | `array[object]` | Most critical issues | See `coding_analyze_file` |
| `files_with_issues` | `array[string]` | Files containing issues | `["./src/module.py"]` |
| `output_path` | `string` | Path to saved report | `"./reports/analysis.json"` |

### 5. Error Handling

- `DirectoryNotFoundError`: Specified path does not exist or is not a directory
- `AnalysisError`: Critical failure during analysis
- Return Format: `{"success": false, "error": "Project analysis failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Static analysis is read-only. Produces consistent results for unchanged code.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "coding_analyze_project",
  "arguments": {
    "path": "./src/codomyrmex/",
    "include_patterns": ["**/*.py"],
    "exclude_patterns": ["**/tests/**", "**/__pycache__/**"],
    "output_path": "./reports/codomyrmex-analysis.html",
    "report_format": "html"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Path validated as directory. Glob patterns sanitized.
- **Permissions**: Read access to source files, write access to output path.
- **Data Handling**: Source code analyzed locally; not transmitted externally.
- **File Paths**: Path traversal prevented; restricted to allowed directories.

---

## Tool: `coding_check_quality_gates`

### 1. Tool Purpose and Description

Evaluates code against configurable quality gates (thresholds for complexity, coverage, issue counts, etc.). Used in CI/CD pipelines to enforce quality standards.

### 2. Invocation Name

`coding_check_quality_gates`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to analyze | `"./src/"` |
| `gates` | `object` | No | Quality gate thresholds (uses defaults if not specified) | See below |
| `gates.max_complexity` | `float` | No | Maximum allowed average complexity. Default: 10 | `8.0` |
| `gates.min_maintainability` | `float` | No | Minimum maintainability index. Default: 50 | `60.0` |
| `gates.max_errors` | `integer` | No | Maximum error-level issues. Default: 0 | `0` |
| `gates.max_warnings` | `integer` | No | Maximum warning-level issues. Default: 50 | `20` |
| `fail_on_violation` | `boolean` | No | Return failure status on violation. Default: true | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether all quality gates passed | `true` |
| `gates_checked` | `integer` | Number of gates evaluated | `4` |
| `gates_passed` | `integer` | Number of gates that passed | `4` |
| `results` | `array[object]` | Per-gate results | See below |
| `results[].gate` | `string` | Gate name | `"max_complexity"` |
| `results[].passed` | `boolean` | Whether gate passed | `true` |
| `results[].threshold` | `float` | Configured threshold | `10.0` |
| `results[].actual` | `float` | Actual measured value | `5.3` |
| `results[].margin` | `float` | Distance from threshold | `4.7` |
| `overall_status` | `enum["pass", "fail", "warn"]` | Overall quality status | `"pass"` |

### 5. Error Handling

- `AnalysisError`: Unable to compute metrics
- `ConfigurationError`: Invalid gate configuration
- Return Format: `{"success": false, "error": "Quality gate check failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Read-only analysis with deterministic gate evaluation.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "coding_check_quality_gates",
  "arguments": {
    "path": "./src/codomyrmex/coding/",
    "gates": {
      "max_complexity": 8.0,
      "min_maintainability": 65.0,
      "max_errors": 0,
      "max_warnings": 10
    },
    "fail_on_violation": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: Path validated. Gate thresholds validated as positive numbers.
- **Permissions**: Read-only access to source files.
- **Data Handling**: No sensitive data involved.

---

## Tool: `coding_debug_code`

### 1. Tool Purpose and Description

Autonomous debugging tool that analyzes execution failures, diagnoses errors, generates fix patches using LLM assistance, and verifies repairs. Designed for automated code repair pipelines.

### 2. Invocation Name

`coding_debug_code`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `source_code` | `string` | Yes | The source code that failed | `"def divide(a, b):\n    return a / b"` |
| `stdout` | `string` | Yes | Standard output from failed execution | `""` |
| `stderr` | `string` | Yes | Standard error from failed execution (includes stack trace) | `"ZeroDivisionError: division by zero"` |
| `exit_code` | `integer` | Yes | Exit code from failed execution | `1` |
| `language` | `string` | No | Programming language. Default: auto-detect | `"python"` |
| `max_retries` | `integer` | No | Maximum fix attempts. Default: 3 | `5` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether a fix was found and verified | `true` |
| `fixed_code` | `string` | Repaired source code (if successful) | `"def divide(a, b):\n    if b == 0:\n        return None\n    return a / b"` |
| `diagnosis` | `object` | Error diagnosis details | See below |
| `diagnosis.error_type` | `string` | Classified error type | `"ZeroDivisionError"` |
| `diagnosis.line_number` | `integer` | Line where error occurred | `2` |
| `diagnosis.root_cause` | `string` | Identified root cause | `"Division by zero not handled"` |
| `patches_attempted` | `integer` | Number of fix attempts | `1` |
| `patch_description` | `string` | Description of applied fix | `"Added zero division guard"` |
| `verification` | `object` | Fix verification result | See below |
| `verification.tests_passed` | `boolean` | Whether fixed code executes cleanly | `true` |

### 5. Error Handling

- `DiagnosisError`: Unable to diagnose the error
- `PatchGenerationError`: Could not generate fix suggestions
- `VerificationError`: All fix attempts failed verification
- Return Format: `{"success": false, "error": "Debugging failed: <details>", "diagnosis": {...}}`

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: LLM-generated patches may vary between calls. The debugging process attempts multiple fixes until one succeeds.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "coding_debug_code",
  "arguments": {
    "source_code": "def process_data(items):\n    total = sum(items)\n    return total / len(items)",
    "stdout": "",
    "stderr": "Traceback (most recent call last):\n  File \"<string>\", line 3, in process_data\nZeroDivisionError: division by zero",
    "exit_code": 1,
    "language": "python",
    "max_retries": 3
  }
}
```

### 8. Security Considerations

- **Input Validation**: Source code and error messages are processed but not executed during diagnosis.
- **Permissions**: LLM API access required for patch generation.
- **Data Handling**: Source code sent to LLM provider; avoid debugging code containing secrets.
- **Verification**: Fixed code is re-executed in sandboxed environment.
- **Output Sanitization**: Generated patches should be reviewed before deployment.

---

## Tool: `coding_monitor_execution`

### 1. Tool Purpose and Description

Real-time monitoring tool for tracking code execution metrics including CPU usage, memory consumption, I/O operations, and execution timeline. Useful for performance profiling and resource optimization.

### 2. Invocation Name

`coding_monitor_execution`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `language` | `string` | Yes | Programming language | `"python"` |
| `code` | `string` | Yes | Code to execute with monitoring | `"import time; time.sleep(1)"` |
| `sample_interval_ms` | `integer` | No | Metric sampling interval. Default: 100 | `50` |
| `include_memory_profile` | `boolean` | No | Detailed memory profiling. Default: false | `true` |
| `timeout` | `integer` | No | Execution timeout in seconds. Default: 60 | `30` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether execution completed | `true` |
| `execution_result` | `object` | Standard execution output | See `coding_execute_code` |
| `metrics` | `object` | Collected performance metrics | See below |
| `metrics.peak_memory_mb` | `float` | Peak memory usage in MB | `45.2` |
| `metrics.avg_cpu_percent` | `float` | Average CPU utilization | `23.5` |
| `metrics.total_duration_ms` | `float` | Total execution duration | `1023.4` |
| `metrics.io_read_bytes` | `integer` | Bytes read from disk | `4096` |
| `metrics.io_write_bytes` | `integer` | Bytes written to disk | `1024` |
| `timeline` | `array[object]` | Time-series metric samples | See below |
| `timeline[].timestamp_ms` | `float` | Sample timestamp | `100.0` |
| `timeline[].memory_mb` | `float` | Memory at sample | `32.1` |
| `timeline[].cpu_percent` | `float` | CPU at sample | `15.2` |

### 5. Error Handling

- `MonitoringError`: Unable to collect metrics
- `ExecutionError`: Code execution failed
- Return Format: `{"success": false, "error": "Monitoring failed: <details>", "partial_metrics": {...}}`

### 6. Idempotency

- **Idempotent**: Partially
- **Explanation**: Execution may have side effects. Metrics for identical code vary due to system load.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "coding_monitor_execution",
  "arguments": {
    "language": "python",
    "code": "import numpy as np\ndata = np.random.rand(10000, 10000)\nresult = np.linalg.svd(data)",
    "sample_interval_ms": 100,
    "include_memory_profile": true,
    "timeout": 120
  }
}
```

### 8. Security Considerations

- **Input Validation**: Code executed in sandboxed environment (see `coding_execute_code`).
- **Permissions**: Same restrictions as code execution.
- **Data Handling**: Performance metrics may reveal system information.
- **Resource Limits**: Monitoring adds overhead; timeout enforced.

---

## Tool: `coding_generate_report`

### 1. Tool Purpose and Description

Generates comprehensive code quality reports from analysis results in various formats (HTML, PDF, Markdown). Suitable for documentation, CI/CD artifacts, and stakeholder communication.

### 2. Invocation Name

`coding_generate_report`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `analysis_results` | `object` | Yes | Results from `coding_analyze_project` or equivalent | `{...}` |
| `output_path` | `string` | Yes | Path for generated report | `"./reports/quality-report.html"` |
| `format` | `enum["html", "markdown", "json"]` | No | Report format. Default: "html" | `"html"` |
| `include_charts` | `boolean` | No | Include visual charts (HTML only). Default: true | `true` |
| `include_recommendations` | `boolean` | No | Include improvement recommendations. Default: true | `true` |
| `title` | `string` | No | Report title | `"Codomyrmex Code Quality Report"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether report was generated | `true` |
| `output_path` | `string` | Path to generated report | `"./reports/quality-report.html"` |
| `format` | `string` | Report format | `"html"` |
| `size_bytes` | `integer` | Report file size | `45678` |
| `sections_included` | `array[string]` | Report sections | `["summary", "issues", "metrics", "recommendations"]` |

### 5. Error Handling

- `InvalidResultsError`: Analysis results malformed
- `WriteError`: Unable to write report file
- Return Format: `{"success": false, "error": "Report generation failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Identical inputs produce identical reports. Output file is overwritten.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "coding_generate_report",
  "arguments": {
    "analysis_results": {
      "files_analyzed": 42,
      "total_issues": 23,
      "quality_score": 85.5
    },
    "output_path": "./reports/weekly-quality.html",
    "format": "html",
    "include_charts": true,
    "title": "Weekly Code Quality Report - Codomyrmex"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Analysis results validated for expected structure.
- **Permissions**: Write access required for output path.
- **Data Handling**: Report may include file paths and code snippets from analysis.
- **File Paths**: Output path validated and restricted to allowed directories.

---

## Tool: `coding_run_in_docker`

### 1. Tool Purpose and Description

Low-level tool for executing code in a specific Docker container configuration. Provides fine-grained control over container settings, environment variables, and volume mounts.

### 2. Invocation Name

`coding_run_in_docker`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `language` | `string` | Yes | Programming language | `"python"` |
| `code` | `string` | Yes | Code to execute | `"print('Hello')"` |
| `image` | `string` | No | Docker image. Default: language-specific default | `"python:3.11-slim"` |
| `environment` | `object` | No | Environment variables | `{"DEBUG": "true"}` |
| `memory_limit` | `string` | No | Memory limit. Default: "256m" | `"512m"` |
| `cpu_limit` | `float` | No | CPU cores limit. Default: 1.0 | `2.0` |
| `network_enabled` | `boolean` | No | Enable network access. Default: false | `false` |
| `timeout` | `integer` | No | Execution timeout in seconds. Default: 30 | `60` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `stdout` | `string` | Standard output | `"Hello\n"` |
| `stderr` | `string` | Standard error | `""` |
| `exit_code` | `integer` | Exit code | `0` |
| `execution_time` | `float` | Execution duration in seconds | `0.45` |
| `status` | `string` | Execution status | `"success"` |
| `container_id` | `string` | Docker container ID used | `"abc123def"` |
| `resource_usage` | `object` | Container resource usage | See below |
| `resource_usage.memory_peak_mb` | `float` | Peak memory | `45.2` |
| `resource_usage.cpu_seconds` | `float` | CPU time used | `0.32` |

### 5. Error Handling

- `DockerNotAvailableError`: Docker daemon not running
- `ImageNotFoundError`: Specified image not available
- `ContainerError`: Container execution failed
- `ResourceLimitError`: Exceeded resource limits
- Return Format: `{"success": false, "error": "Docker execution failed: <details>", "status": "setup_error"}`

### 6. Idempotency

- **Idempotent**: Partially
- **Explanation**: Deterministic code produces consistent results. Network-enabled execution may vary.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "coding_run_in_docker",
  "arguments": {
    "language": "python",
    "code": "import requests\nprint(requests.get('https://api.example.com/health').status_code)",
    "image": "python:3.11-slim",
    "environment": {
      "PYTHONUNBUFFERED": "1"
    },
    "memory_limit": "512m",
    "cpu_limit": 1.0,
    "network_enabled": true,
    "timeout": 30
  }
}
```

### 8. Security Considerations

- **Input Validation**: Image name validated against allowed list. Environment variables sanitized.
- **Permissions**: Docker daemon access required. Container runs with restricted user.
- **Data Handling**: Code and output isolated within container.
- **Network Isolation**: Network disabled by default. Enable only when necessary.
- **Resource Limits**: Strictly enforced via Docker cgroups.
- **File Paths**: No host filesystem access except explicitly mounted volumes.

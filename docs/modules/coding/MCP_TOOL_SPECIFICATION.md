# Coding Module - MCP Tool Specification

This document defines the Model Context Protocol (MCP) tools for the `coding` module, which provides code execution, sandboxing, review, monitoring, and debugging capabilities. Tools are defined with `@mcp_tool` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

## Implementation Status

The module-level tools in `mcp_tools.py` are documented below:

| Tool | Purpose |
| :--- | :--- |
| `code_execute` | Run a code snippet through the sandboxed executor |
| `code_list_languages` | List the languages the executor supports |
| `code_review_file` | Run `CodeReviewer` analysis on one file |
| `code_review_project` | Run `CodeReviewer` analysis on a directory |
| `code_debug` | Ask the `Debugger` for a patched version of failing code |

Other `@mcp_tool` functions live in submodules:

| Tool | Defined in |
| :--- | :--- |
| `execute_code` | `execution/executor.py` (the function `code_execute` wraps; also accepts `stdin` and `session_id`) |
| `analyze_file` | `static_analysis/static_analyzer.py` |
| `analyze_project` | `static_analysis/static_analyzer.py` |
| `match_pattern` | `pattern_matching/mcp_tools.py` (documented in `pattern_matching/MCP_TOOL_SPECIFICATION.md`) |
| `list_patterns` | `pattern_matching/mcp_tools.py` |

Quality gates, reports, execution monitoring and raw Docker runs are available from the Python API (`check_quality_gates`, `generate_report`, `ExecutionMonitor`, `run_code_in_docker`) but are not MCP tools.

## General Considerations for Coding Tools

- **Dependencies**: Docker is required for sandboxed execution. Static analysis tools (ruff, ty) are required for code review.
- **Initialization**: No module-level initialization required. Docker availability is checked at execution time.
- **Error Handling**: Each tool catches exceptions and returns `{"status": "error", "message": "<description>"}`.
- **Security**: Code execution runs in Docker containers with resource limits.

---

## Tool: `code_execute`

### 1. Tool Purpose and Description

Executes a code snippet with `execute_code` (sandboxed Docker execution) and wraps the executor's result.

### 2. Invocation Name

`code_execute`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `language` | `string` | Yes | One of the languages returned by `code_list_languages` | `"python"` |
| `code` | `string` | Yes | Source code to run | `"print(sum(range(10)))"` |
| `timeout` | `integer` | No | Timeout in seconds (default `30`; the executor caps it at 300) | `10` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `status` | `string` | `"success"` when the executor returned, else `"error"` |
| `result` | `object` | Executor result: `stdout`, `stderr`, `exit_code`, `execution_time`, `status` (`"success"`, `"timeout"`, `"execution_error"`, `"setup_error"`) and `error_message` |
| `message` | `string` | Error description (only on error) |

The outer `status` only reports whether the call completed; check `result.status` and `result.exit_code` for the program's outcome.

### 5. Idempotency

- **Idempotent**: Depends on the code executed.

### 6. Usage Examples

```json
{
  "tool_name": "code_execute",
  "arguments": {"language": "python", "code": "print(sum(range(10)))"}
}
```

### 7. Security Considerations

- Runs arbitrary code; requires Docker and should be gated behind explicit trust.

---

## Tool: `code_list_languages`

### 1. Tool Purpose and Description

Lists the languages supported by the executor.

### 2. Invocation Name

`code_list_languages`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "languages": ["bash", "c", "cpp", "go", "java", "javascript", "python", "rust"]
}
```

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `code_review_file`

### 1. Tool Purpose and Description

Runs `codomyrmex.coding.analyze_file` (a `CodeReviewer` analysis) on one file.

### 2. Invocation Name

`code_review_file`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `string` | Yes | Path to the file to analyse | `"src/app/main.py"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` |
| `analysis` | `array` | `AnalysisResult` entries reported for the file (only on success) |
| `message` | `string` | Error description, e.g. `"File not found: <path>"` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `code_review_project`

### 1. Tool Purpose and Description

Runs `codomyrmex.coding.analyze_project` (a `CodeReviewer` analysis) on a directory.

### 2. Invocation Name

`code_review_project`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `path` | `string` | Yes | Project root directory | `"src/app"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` |
| `analysis` | `object` | `AnalysisSummary` for the project (only on success) |
| `message` | `string` | Error description, e.g. `"Directory not found: <path>"` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `code_debug`

### 1. Tool Purpose and Description

Passes failing code and its output to `Debugger.debug`, which analyses the error, generates candidate patches and verifies them.

### 2. Invocation Name

`code_debug`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `code` | `string` | Yes | Source code that failed | `"x = 1 / 0"` |
| `stdout` | `string` | No | Captured standard output (default `""`) | `""` |
| `stderr` | `string` | No | Captured standard error (default `""`) | `"ZeroDivisionError: division by zero"` |
| `exit_code` | `integer` | No | Exit code of the failed run (default `1`) | `1` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` |
| `diagnosis` | `string` or `null` | Fixed source code, or `null` if no verified fix was found |
| `message` | `string` | Error description (only on error) |

### 5. Idempotency

- **Idempotent**: Depends on the code; patch verification executes it.

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->

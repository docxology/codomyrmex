# CLI Module - MCP Tool Specification

This document defines the Model Context Protocol (MCP) tools for the `cli` module, which serves as the primary command-line interface entry point for the Codomyrmex platform.

## General Considerations for CLI Tools

- **Dependencies**: Requires `logging_monitoring` module. Many handlers depend on their respective domain modules (e.g., `handle_ai_generate` requires `agents` module).
- **Initialization**: No module-level initialization required. Individual handlers may initialize their dependencies lazily.
- **Error Handling**: Errors are logged via `logging_monitoring`. Tools return `{"success": false, "error": "description"}` on failure.
- **Security**: CLI tools execute with the permissions of the calling process. File path parameters are validated against the working directory.

---

## Tool: `cli_check_environment`

### 1. Tool Purpose and Description

Verifies the Codomyrmex environment setup, checking for required dependencies, configuration files, and system prerequisites. Essential for diagnosing installation issues and ensuring the platform is ready for use.

### 2. Invocation Name

`cli_check_environment`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `verbose` | `boolean` | No | Enable verbose output with detailed dependency information. Default: false | `true` |

**Notes on Input Schema:**
- This tool has minimal parameters as it performs a standardized environment check.

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether all environment checks passed | `true` |
| `checks` | `array[object]` | List of individual check results | See below |
| `checks[].name` | `string` | Name of the check | `"python_version"` |
| `checks[].passed` | `boolean` | Whether the check passed | `true` |
| `checks[].message` | `string` | Detailed status message | `"Python 3.11.4 detected"` |
| `missing_dependencies` | `array[string]` | List of missing required dependencies | `["docker"]` |
| `warnings` | `array[string]` | Non-critical issues detected | `["Optional module 'spatial' not installed"]` |

### 5. Error Handling

- `EnvironmentError`: Raised when critical environment checks fail
- `PermissionError`: Raised when unable to access required paths
- Return Format: `{"success": false, "error": "Environment check failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: This tool only performs read operations and checks. Repeated calls will return the same result given an unchanged environment.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_check_environment",
  "arguments": {
    "verbose": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: No user-supplied paths or code execution.
- **Permissions**: Reads environment variables and checks file existence only.
- **Data Handling**: No sensitive data processed.

---

## Tool: `cli_show_modules`

### 1. Tool Purpose and Description

Lists all available Codomyrmex modules with their status, version, and health information. Useful for discovering platform capabilities and diagnosing module-specific issues.

### 2. Invocation Name

`cli_show_modules`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `filter_status` | `enum["available", "unavailable", "all"]` | No | Filter modules by availability status. Default: "all" | `"available"` |
| `include_details` | `boolean` | No | Include detailed module information (version, dependencies). Default: false | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `modules` | `array[object]` | List of module information | See below |
| `modules[].name` | `string` | Module name | `"coding"` |
| `modules[].status` | `string` | Availability status | `"available"` |
| `modules[].version` | `string` | Module version | `"0.1.0"` |
| `modules[].description` | `string` | Brief module description | `"Code execution and review"` |
| `total_count` | `integer` | Total number of modules | `55` |
| `available_count` | `integer` | Number of available modules | `52` |

### 5. Error Handling

- `ModuleNotFoundError`: If module discovery fails
- Return Format: `{"success": false, "error": "Failed to enumerate modules: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Read-only operation that queries module registry.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_show_modules",
  "arguments": {
    "filter_status": "available",
    "include_details": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: Enum validation for `filter_status`.
- **Permissions**: Read-only access to module metadata.
- **Data Handling**: No sensitive data exposed.

---

## Tool: `cli_show_system_status`

### 1. Tool Purpose and Description

Displays comprehensive system status including resource utilization, active workflows, running processes, and service health. Provides a dashboard view of the Codomyrmex platform state.

### 2. Invocation Name

`cli_show_system_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `include_resources` | `boolean` | No | Include CPU/memory/disk usage. Default: true | `true` |
| `include_workflows` | `boolean` | No | Include active workflow status. Default: true | `true` |
| `format` | `enum["text", "json"]` | No | Output format. Default: "json" | `"json"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | Overall system status | `"healthy"` |
| `resources` | `object` | Resource utilization (if requested) | See below |
| `resources.cpu_percent` | `float` | CPU utilization percentage | `45.2` |
| `resources.memory_percent` | `float` | Memory utilization percentage | `68.5` |
| `resources.disk_percent` | `float` | Disk utilization percentage | `32.1` |
| `workflows` | `object` | Workflow status (if requested) | See below |
| `workflows.active` | `integer` | Number of running workflows | `2` |
| `workflows.queued` | `integer` | Number of queued workflows | `5` |
| `services` | `array[object]` | Service health status | See below |
| `timestamp` | `string` | ISO timestamp of status check | `"2026-02-03T10:30:00Z"` |

### 5. Error Handling

- `RuntimeError`: If unable to collect system metrics
- Return Format: `{"success": false, "error": "Status collection failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Read-only status query with no side effects.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_show_system_status",
  "arguments": {
    "include_resources": true,
    "include_workflows": true,
    "format": "json"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Enum validation for format parameter.
- **Permissions**: Requires read access to system metrics.
- **Data Handling**: May expose system resource information; appropriate for trusted environments.

---

## Tool: `cli_workflow_run`

### 1. Tool Purpose and Description

Executes a defined workflow by name, optionally with custom parameters. Workflows orchestrate multi-step operations across Codomyrmex modules.

### 2. Invocation Name

`cli_workflow_run`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `workflow_name` | `string` | Yes | Name of the workflow to execute | `"ai-analysis"` |
| `params` | `object` | No | JSON parameters to pass to the workflow | `{"target_path": "./src"}` |
| `async_execution` | `boolean` | No | Run workflow asynchronously. Default: false | `false` |
| `timeout` | `integer` | No | Execution timeout in seconds. Default: 300 | `600` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether workflow completed successfully | `true` |
| `workflow_id` | `string` | Unique identifier for this execution | `"wf-abc123"` |
| `status` | `string` | Execution status | `"completed"` |
| `result` | `object` | Workflow output data | `{"files_processed": 42}` |
| `duration_seconds` | `float` | Execution duration | `23.5` |
| `steps_completed` | `integer` | Number of workflow steps completed | `5` |

### 5. Error Handling

- `WorkflowNotFoundError`: Specified workflow does not exist
- `WorkflowTimeoutError`: Execution exceeded timeout
- `WorkflowExecutionError`: Step failure during execution
- Return Format: `{"success": false, "error": "Workflow failed: <details>", "failed_step": "<step_name>"}`

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Workflow execution may modify files, create resources, or have other side effects depending on workflow definition.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_workflow_run",
  "arguments": {
    "workflow_name": "code-review",
    "params": {
      "target_path": "./src/codomyrmex/coding",
      "output_format": "json"
    },
    "timeout": 300
  }
}
```

### 8. Security Considerations

- **Input Validation**: Workflow name validated against registered workflows. Parameters validated per workflow schema.
- **Permissions**: Workflow execution inherits CLI process permissions.
- **Data Handling**: Workflows may process source code; ensure appropriate access controls.
- **File Paths**: All file paths in params are validated and sandboxed.

---

## Tool: `cli_ai_generate`

### 1. Tool Purpose and Description

Generates code using AI assistance based on a natural language prompt. Leverages configured LLM providers to produce code in the specified programming language.

### 2. Invocation Name

`cli_ai_generate`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `prompt` | `string` | Yes | Natural language description of code to generate | `"Create a function to validate email addresses"` |
| `language` | `string` | No | Target programming language. Default: "python" | `"typescript"` |
| `provider` | `string` | No | LLM provider to use. Default: "openai" | `"anthropic"` |
| `output_path` | `string` | No | File path to save generated code | `"./src/validators.py"` |
| `max_tokens` | `integer` | No | Maximum tokens in response. Default: 2048 | `4096` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether generation succeeded | `true` |
| `code` | `string` | Generated source code | `"def validate_email..."` |
| `language` | `string` | Language of generated code | `"python"` |
| `provider` | `string` | LLM provider used | `"openai"` |
| `model` | `string` | Specific model used | `"gpt-4o"` |
| `tokens_used` | `integer` | Total tokens consumed | `856` |
| `output_path` | `string` | Path where code was saved (if specified) | `"./src/validators.py"` |

### 5. Error Handling

- `ProviderError`: LLM provider unavailable or authentication failed
- `RateLimitError`: Provider rate limit exceeded
- `GenerationError`: AI failed to generate valid code
- Return Format: `{"success": false, "error": "Generation failed: <details>"}`

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Each call may produce different generated code. If `output_path` is specified, file will be overwritten.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_ai_generate",
  "arguments": {
    "prompt": "Create a TypeScript function that fetches data from a REST API with retry logic and exponential backoff",
    "language": "typescript",
    "provider": "anthropic",
    "output_path": "./src/api/fetcher.ts"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Prompt sanitized for injection attacks. Language validated against supported list.
- **Permissions**: Requires API keys for LLM providers (read from environment/config).
- **Data Handling**: Prompts sent to external LLM providers; do not include sensitive data in prompts.
- **File Paths**: Output paths validated and restricted to project directory.
- **Output Sanitization**: Generated code is not automatically executed.

---

## Tool: `cli_analyze_code`

### 1. Tool Purpose and Description

Performs static code analysis on a file or directory, checking for code quality issues, security vulnerabilities, and style violations. Integrates with multiple analysis tools.

### 2. Invocation Name

`cli_analyze_code`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to file or directory to analyze | `"./src/codomyrmex/"` |
| `output` | `string` | No | Directory for analysis reports | `"./reports/"` |
| `include_security` | `boolean` | No | Include security vulnerability scan. Default: true | `true` |
| `include_metrics` | `boolean` | No | Include code metrics (complexity, etc). Default: true | `true` |
| `format` | `enum["text", "json", "html"]` | No | Report output format. Default: "json" | `"json"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether analysis completed | `true` |
| `files_analyzed` | `integer` | Number of files processed | `42` |
| `issues` | `array[object]` | List of detected issues | See below |
| `issues[].severity` | `string` | Issue severity (error, warning, info) | `"warning"` |
| `issues[].file` | `string` | File path containing issue | `"./src/module.py"` |
| `issues[].line` | `integer` | Line number | `45` |
| `issues[].message` | `string` | Issue description | `"Function too complex"` |
| `issues[].rule` | `string` | Rule/check identifier | `"C901"` |
| `metrics` | `object` | Code metrics summary | See below |
| `security_findings` | `array[object]` | Security issues found | See below |
| `output_path` | `string` | Path to detailed report | `"./reports/analysis.json"` |

### 5. Error Handling

- `FileNotFoundError`: Specified path does not exist
- `AnalysisError`: Analysis tool failed
- Return Format: `{"success": false, "error": "Analysis failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Analysis is read-only. Repeated calls on unchanged code produce identical results.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_analyze_code",
  "arguments": {
    "path": "./src/codomyrmex/coding/",
    "output": "./reports/",
    "include_security": true,
    "include_metrics": true,
    "format": "json"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Path validated to exist within allowed directories.
- **Permissions**: Read access to source files, write access to output directory.
- **Data Handling**: Source code is analyzed but not transmitted externally.
- **File Paths**: Strict path validation prevents traversal attacks.

---

## Tool: `cli_project_create`

### 1. Tool Purpose and Description

Creates a new Codomyrmex project with specified template, setting up directory structure, configuration files, and initial dependencies.

### 2. Invocation Name

`cli_project_create`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `name` | `string` | Yes | Project name (alphanumeric, hyphens, underscores) | `"my-analysis-project"` |
| `template` | `string` | No | Project template to use. Default: "ai_analysis" | `"web_application"` |
| `description` | `string` | No | Project description | `"Data analysis pipeline"` |
| `path` | `string` | No | Parent directory for project. Default: current directory | `"./projects/"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether project was created | `true` |
| `project_path` | `string` | Full path to created project | `"./projects/my-analysis-project"` |
| `template_used` | `string` | Template applied | `"ai_analysis"` |
| `files_created` | `array[string]` | List of created files | `["pyproject.toml", "README.md"]` |
| `next_steps` | `array[string]` | Suggested next actions | `["cd my-project", "uv sync"]` |

### 5. Error Handling

- `ProjectExistsError`: Project directory already exists
- `TemplateNotFoundError`: Specified template not available
- `PermissionError`: Cannot create directory at specified path
- Return Format: `{"success": false, "error": "Project creation failed: <details>"}`

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Creates new files and directories. Re-running with same name will fail if project exists.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_project_create",
  "arguments": {
    "name": "code-review-system",
    "template": "ai_analysis",
    "description": "Automated code review with LLM integration",
    "path": "./projects/"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Project name sanitized (alphanumeric, hyphens, underscores only). Path validated.
- **Permissions**: Requires write access to parent directory.
- **Data Handling**: No sensitive data processed.
- **File Paths**: Path traversal prevented; projects created within allowed directories.

---

## Tool: `cli_skills_search`

### 1. Tool Purpose and Description

Searches available skills by keyword or category. Skills are reusable capability definitions that can be composed into workflows.

### 2. Invocation Name

`cli_skills_search`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `query` | `string` | Yes | Search query for skills | `"code analysis"` |
| `category` | `string` | No | Filter by skill category | `"Development"` |
| `limit` | `integer` | No | Maximum results to return. Default: 20 | `10` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether search succeeded | `true` |
| `results` | `array[object]` | Matching skills | See below |
| `results[].name` | `string` | Skill name | `"code_review"` |
| `results[].category` | `string` | Skill category | `"Development"` |
| `results[].description` | `string` | Skill description | `"Automated code review"` |
| `results[].match_score` | `float` | Search relevance score | `0.95` |
| `total_results` | `integer` | Total matching skills | `5` |

### 5. Error Handling

- `SearchError`: Search index unavailable
- Return Format: `{"success": false, "error": "Search failed: <details>"}`

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Read-only search operation.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_skills_search",
  "arguments": {
    "query": "security vulnerability scanning",
    "category": "Security",
    "limit": 10
  }
}
```

### 8. Security Considerations

- **Input Validation**: Query sanitized, category validated against known categories.
- **Permissions**: Read-only access to skills registry.
- **Data Handling**: No sensitive data involved.

---

## Tool: `cli_run_quick`

### 1. Tool Purpose and Description

Quick execution tool for running scripts, modules, or directories with minimal configuration. Supports parallel execution and glob patterns.

### 2. Invocation Name

`cli_run_quick`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:--------------|:-----|:---------|:------------|:--------------|
| `target` | `string` | Yes | Script path, module name, directory, or glob pattern | `"./scripts/*.py"` |
| `args` | `array[string]` | No | Additional arguments to pass | `["--verbose", "--output", "results/"]` |
| `timeout` | `integer` | No | Timeout per script in seconds. Default: 60 | `120` |
| `parallel` | `boolean` | No | Run matching targets in parallel. Default: false | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `success` | `boolean` | Whether all executions succeeded | `true` |
| `targets_run` | `integer` | Number of targets executed | `5` |
| `results` | `array[object]` | Per-target results | See below |
| `results[].target` | `string` | Target that was run | `"./scripts/analyze.py"` |
| `results[].exit_code` | `integer` | Process exit code | `0` |
| `results[].stdout` | `string` | Standard output (truncated) | `"Analysis complete"` |
| `results[].duration_ms` | `float` | Execution duration | `2340.5` |
| `total_duration_ms` | `float` | Total execution time | `5420.2` |

### 5. Error Handling

- `TargetNotFoundError`: No matching targets found
- `ExecutionError`: Script execution failed
- `TimeoutError`: Execution exceeded timeout
- Return Format: `{"success": false, "error": "Execution failed: <details>", "failed_targets": [...]}`

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Executes scripts which may have side effects.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "cli_run_quick",
  "arguments": {
    "target": "./scripts/tests/*.py",
    "args": ["--verbose"],
    "timeout": 120,
    "parallel": true
  }
}
```

### 8. Security Considerations

- **Input Validation**: Target paths validated and sandboxed. Glob patterns restricted.
- **Permissions**: Executes scripts with CLI process permissions.
- **Data Handling**: Script output captured but may contain sensitive data.
- **File Paths**: Strict validation prevents arbitrary code execution outside allowed directories.

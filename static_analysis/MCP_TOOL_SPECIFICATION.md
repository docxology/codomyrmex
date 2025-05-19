# Static Analysis - MCP Tool Specification

This document outlines the specification for tools within the Static Analysis module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Tool Integration**: This module aims to integrate various static analysis tools (linters, security scanners, complexity checkers).
- **Configuration**: Tools may rely on specific configuration files (e.g., `.pylintrc`, `.flake8`) or allow configuration via parameters.

---

## Tool: `run_static_analysis`

### 1. Tool Purpose and Description

Runs specified static analysis tools (e.g., linters, security scanners, complexity analyzers) on a given file or directory. It returns a summary of findings and/or detailed reports from each tool.

### 2. Invocation Name

`run_static_analysis`

### 3. Input Schema (Parameters)

| Parameter Name   | Type          | Required | Description                                                                                                | Example Value                                  |
| :--------------- | :------------ | :------- | :--------------------------------------------------------------------------------------------------------- | :--------------------------------------------- |
| `target_paths`   | `array[string]`| Yes      | List of file or directory paths to analyze relative to the project root.                                     | `["src/my_module/", "tests/test_file.py"]`     |
| `tools`          | `array[string]`| No       | Specific tools to run (e.g., "pylint", "flake8", "bandit", "radon", "lizard"). Default: runs a predefined set of primary tools. | `["pylint", "bandit"]`                       |
| `language`       | `string`      | No       | The primary programming language of the target_paths, to help select appropriate tools or configurations. (e.g., "python", "javascript") | `"python"`                                     |
| `config_file`    | `string`      | No       | Path to a custom configuration file for the analysis tools (format depends on tools being run).          | `"./.custom_pylintrc"`                         |
| `options`        | `object`      | No       | Additional tool-specific options. Structure depends on tools. (e.g. `{"pylint": {"disable": "C0114"}}`) | `{"pylint": {"jobs": "2"}}`                 |

**Notes on Input Schema:**
- Supported `tools` and `language` values will depend on the module's implementation.
- `target_paths` should be relative to the project root to ensure clarity and prevent access to arbitrary system paths.

### 4. Output Schema (Return Value)

| Field Name        | Type          | Description                                                                                                | Example Value                                                                 |
| :---------------- | :------------ | :--------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| `status`          | `string`      | Overall status: "success", "completed_with_issues", "error".                                               | `"completed_with_issues"`                                                       |
| `summary`         | `string`      | A brief human-readable summary of the analysis findings (e.g., "Pylint: 5 issues. Bandit: 2 high severity."). | `"Analysis complete. 10 issues found across 2 tools."`                      |
| `tool_results`    | `array[object]`| Array of results, one object per tool executed.                                                            | `[{"tool": "pylint", "issue_count": 5, "report_path": "output/pylint_report.txt"}]` |
| `error_message`   | `string`      | A descriptive error message if `status` is "error" (e.g., tool not found, config error).                   | `"Pylint tool not found or configuration error."`                             |

**Structure for `tool_results` objects:**

| Field Name      | Type     | Description                                                                      |
| :-------------- | :------- | :------------------------------------------------------------------------------- |
| `tool_name`     | `string` | Name of the tool (e.g., "pylint", "bandit").                                     |
| `issue_count`   | `integer`| Number of issues found by this tool. Can be -1 if not applicable.                |
| `issues`        | `array[object]`| Optional: A list of structured issue objects (see below).                      |
| `raw_output`    | `string` | Optional: Raw text output from the tool.                                         |
| `report_path`   | `string` | Optional: Path to a generated report file (e.g., HTML, JSON, TXT).               |
| `error`         | `string` | Optional: Error message specific to this tool's execution.                       |

**Structure for `issues` objects (example for a linter):**

| Field Name      | Type     | Description                                                              |
| :-------------- | :------- | :----------------------------------------------------------------------- |
| `file_path`     | `string` | Path to the file where the issue was found.                              |
| `line_number`   | `integer`| Line number of the issue.                                                |
| `column_number` | `integer`| Column number (if applicable).                                           |
| `code`          | `string` | Issue code or identifier (e.g., "E501" for Pylint).                      |
| `message`       | `string` | Description of the issue.                                                |
| `severity`      | `string` | Severity (e.g., "error", "warning", "info", or tool-specific like "HIGH"). |

### 5. Error Handling

- **Tool Not Found/Configuration Error**: If a specified tool cannot be run or its configuration is invalid, `status` will be "error", and `error_message` will provide details.
- **Execution Errors within Tools**: Individual tools might encounter errors analyzing specific files. These should be captured within the `tool_results[N].error` field for that tool, and the overall `status` might be `completed_with_issues` or `error` depending on severity.

### 6. Idempotency

- **Idempotent**: Yes, if the `target_paths` and their content, and the tool configurations do not change between calls.
- **Explanation**: Running the same analysis on the same code with the same configuration should produce the same results.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "run_static_analysis",
  "arguments": {
    "target_paths": ["src/module_a/file.py"],
    "tools": ["pylint", "bandit"],
    "language": "python"
  }
}
```

Expected output (example):
```json
{
  "status": "completed_with_issues",
  "summary": "Pylint found 3 issues. Bandit found 1 high severity issue.",
  "tool_results": [
    {
      "tool_name": "pylint",
      "issue_count": 3,
      "issues": [
        {"file_path": "src/module_a/file.py", "line_number": 10, "code": "C0301", "message": "Line too long"}
      ],
      "report_path": "./output/static_analysis/pylint_report_datetime.txt"
    },
    {
      "tool_name": "bandit",
      "issue_count": 1,
      "issues": [
        {"file_path": "src/module_a/file.py", "line_number": 25, "code": "B101", "message": "Use of assert detected."}
      ],
      "report_path": "./output/static_analysis/bandit_report_datetime.json"
    }
  ],
  "error_message": null
}
```

### 8. Security Considerations

- **Input Validation**: `target_paths` must be validated to ensure they are within the project directory and do not represent attempts at path traversal. `language` and `tools` must be from an allow-list.
- **Tool Execution**: Static analysis tools themselves can sometimes have vulnerabilities or be resource-intensive. Running them should be done with appropriate user permissions and potentially resource limits if analyzing very large or complex codebases.
- **Configuration Files**: If `config_file` is accepted, its path and content should be validated. Malicious configuration files could potentially alter tool behavior undesirably.
- **Output Handling**: Reports from tools might contain snippets of source code. Ensure these are handled appropriately if displayed or stored, respecting data privacy if the code is sensitive.

---

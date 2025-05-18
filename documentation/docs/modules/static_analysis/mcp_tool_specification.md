---
id: static-analysis-mcp-tool-specification
title: Static Analysis - MCP Tool Specification
sidebar_label: MCP Tool Specification
---

# Static Analysis - MCP Tool Specification

This document outlines MCP tools provided by the Static Analysis module.

## Tool: `static_analysis.run_scan`

### 1. Tool Purpose and Description

Allows an LLM or AI agent to initiate a static analysis scan on specified parts of the codebase using configured tools (linters, security scanners, etc.). The tool can return a summary of issues or a reference to a detailed report.

### 2. Invocation Name

`static_analysis.run_scan`

### 3. Input Schema (Parameters)

| Parameter Name | Type          | Required | Description                                                                 | Example Value                                  |
| :------------- | :------------ | :------- | :-------------------------------------------------------------------------- | :--------------------------------------------- |
| `target_paths` | `array[string]`| Yes      | List of relative file or directory paths to scan.                           | `["src/module_a/", "utils/helpers.py"]`        |
| `tools`        | `array[string]`| No       | Specific tools to run (e.g., `["pylint", "bandit"]`). If empty, use configured defaults for path. | `["pylint"]`                                   |
| `output_format`| `string`      | No       | Desired output format: `summary`, `full_json`, `sarif`. Default: `summary`. | `"full_json"`                                  |

**JSON Schema Example:**

```json
{
  "type": "object",
  "properties": {
    "target_paths": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of relative file or directory paths to scan."
    },
    "tools": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Specific tools to run (e.g., [\"pylint\", \"bandit\"]). If empty, use configured defaults."
    },
    "output_format": {
      "type": "string",
      "enum": ["summary", "full_json", "sarif"],
      "default": "summary",
      "description": "Desired output format."
    }
  },
  "required": ["target_paths"]
}
```

### 4. Output Schema (Return Value)

(Structure depends on `output_format`)

**For `output_format: "summary"`:**

| Field Name     | Type     | Description                                       | Example Value                                      |
| :------------- | :------- | :------------------------------------------------ | :------------------------------------------------- |
| `status`       | `string` | `success` or `failure`.                           | `"success"`                                        |
| `total_issues` | `integer`| Total number of issues found.                     | `15`                                               |
| `errors`       | `integer`| Number of error-level issues.                     | `2`                                                |
| `warnings`     | `integer`| Number of warning-level issues.                   | `13`                                               |
| `report_id`    | `string` | (Optional) ID to fetch full report if applicable. | `"scan_report_xyz789"`                             |

**For `output_format: "full_json"` (simplified example):**

```json
{
  "status": "success",
  "issues": [
    {
      "file_path": "src/module_a/main.py",
      "line": 25,
      "tool": "pylint",
      "rule_id": "C0301",
      "message": "Line too long (120/100)",
      "severity": "warning"
    }
    // ... more issues
  ]
}
```
(A `sarif` output would conform to the SARIF JSON schema.)

### 5. Error Handling

- **Error Code `TOOL_NOT_FOUND`**: A specified tool in the `tools` array is not configured or installed.
- **Error Code `PATH_NOT_FOUND`**: One of the `target_paths` does not exist.
- **Error Code `SCAN_FAILED`**: The underlying static analysis tool(s) failed to execute.
- General error message format: `{"error": "description_of_error", "code": "ERROR_CODE"}`

### 6. Idempotency

- Idempotent: Yes (Running the same scan multiple times on unchanged code should yield the same results, assuming tool configurations are stable. It does not alter system state beyond creating temporary files for analysis, which should be cleaned up.)
- Side Effects: May create temporary files during analysis. Performance-intensive.

### 7. Usage Examples (for MCP context)

**Example 1: Run default scan on a directory and get summary**

```json
{
  "tool_name": "static_analysis.run_scan",
  "arguments": {
    "target_paths": ["src/important_module/"],
    "output_format": "summary"
  }
}
```

**Example 2: Run specific tools on a file and get full JSON output**

```json
{
  "tool_name": "static_analysis.run_scan",
  "arguments": {
    "target_paths": ["src/utils/parser.py"],
    "tools": ["bandit", "pylint"],
    "output_format": "full_json"
  }
}
```

### 8. Security Considerations

- **Tool Configuration**: The behavior of this tool is heavily dependent on the configuration of the underlying static analysis tools. Misconfiguration could lead to missed vulnerabilities or excessive false positives.
- **Resource Usage**: Static analysis can be resource-intensive (CPU, memory). Unrestricted calls could lead to performance degradation. Consider rate limiting or job queuing.
- **Interpretation of Results**: LLMs using this tool should be guided to interpret results correctly, especially security warnings, and not just pass them on without context or potential remediation advice.

--- 
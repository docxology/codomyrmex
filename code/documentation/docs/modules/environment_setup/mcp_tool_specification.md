---
sidebar_label: 'MCP Tool Specification'
title: 'Environment Setup - MCP Tool Specification'
---

# Environment Setup - MCP Tool Specification

This document outlines the specification for tools within the Environment Setup module that are intended to be integrated with the Model Context Protocol (MCP).

## Tool: `check_codomyrmex_environment`

### 1. Tool Purpose and Description

Verifies key aspects of the Codomyrmex development environment. This tool can be used by an AI agent to diagnose setup issues or to confirm prerequisites before attempting operations that depend on specific tools or configurations.

### 2. Invocation Name

`check_codomyrmex_environment`

### 3. Input Schema (Parameters)

**Format:** Table

| Parameter Name  | Type      | Required | Description                                                                 | Example Value |
| :-------------- | :-------- | :------- | :-------------------------------------------------------------------------- | :------------ |
| `check_area`    | `string`  | No       | Specific area to check: "python", "nodejs", "docusaurus", "git", "graphviz", "all". Default: "all". | `"python"`    |
| `detail_level`  | `integer` | No       | Level of detail in output (0=summary, 1=detailed). Default: `0`.            | `1`           |

**JSON Schema Example:**

```json
{
  "type": "object",
  "properties": {
    "check_area": {
      "type": "string",
      "description": "Specific area to check: \"python\", \"nodejs\", \"docusaurus\", \"git\", \"graphviz\", \"all\". Default: \"all\".",
      "enum": ["python", "nodejs", "docusaurus", "git", "graphviz", "all"],
      "default": "all"
    },
    "detail_level": {
      "type": "integer",
      "description": "Level of detail in output (0=summary, 1=detailed). Default: 0.",
      "default": 0
    }
  }
}
```

### 4. Output Schema (Return Value)

**Format:** JSON

```json
{
  "status": "success" | "failure" | "partial_success",
  "summary": {
    "python_version": "3.9.1 (actual version or error message)",
    "pip_installed": true | false,
    "git_installed": true | false,
    "nodejs_version": "18.10.0 (actual version or error message, if checked)",
    "npm_installed": true | false, // (if checked)
    "docusaurus_deps_installed": true | false | "not_checked", // (if docusaurus check_area)
    "graphviz_installed": true | false | "not_checked"
  },
  "details": [
    // Array of strings with detailed check messages if detail_level > 0
    "Python check: Version 3.9.1 found.",
    "Node.js check: Version 18.10.0 found."
  ],
  "recommendations": [
    // Array of strings with recommended actions if issues are found
    "Node.js not found. Please install Node.js version 18.0 or higher."
  ]
}
```

### 5. Error Handling

- Errors within the tool's execution (e.g., script crashing) would result in a standard MCP error response.
- Environment check failures are indicated within the `status` field of the successful tool output (e.g., `status: "failure"`) and detailed in `summary` and `recommendations`.

### 6. Idempotency

- Idempotent: Yes. Running the check multiple times does not change the environment state.

### 7. Usage Examples (for MCP context)

**Example 1: Basic Check (All Areas, Summary)**

```json
{
  "tool_name": "check_codomyrmex_environment",
  "arguments": {}
}
```

**Example 2: Check Python Environment (Detailed)**

```json
{
  "tool_name": "check_codomyrmex_environment",
  "arguments": {
    "check_area": "python",
    "detail_level": 1
  }
}
```

### 8. Security Considerations

- This tool primarily reads environment information (versions, paths) and does not modify the system.
- If it executes external commands (e.g., `python --version`), it should ensure those commands are safe and inputs are not user-controlled in a way that allows arbitrary command execution.

---

(No other MCP tools are currently defined for this module.) 
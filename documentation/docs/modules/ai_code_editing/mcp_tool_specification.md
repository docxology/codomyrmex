---
id: ai-code-editing-mcp-tool-specification
title: AI Code Editing - MCP Tool Specification
sidebar_label: MCP Tool Specification
---

# Ai Code Editing - MCP Tool Specification

This document outlines the specification for tools within the Ai Code Editing module that are intended to be integrated with the Model Context Protocol (MCP).

## Tool: `ai_edit_code`

### 1. Tool Purpose and Description

This tool allows an LLM or AI agent to request modifications to a code file. It can be used for refactoring, adding new functionality, fixing bugs, or generating code based on a prompt. The agent specifies the target file, the type of edit (e.g., insert, replace, delete lines), and the content for the edit.

### 2. Invocation Name

`ai_code_editing.edit_file`

### 3. Input Schema (Parameters)

| Parameter Name   | Type     | Required | Description                                                                 | Example Value                                     |
| :--------------- | :------- | :------- | :-------------------------------------------------------------------------- | :------------------------------------------------ |
| `target_file`    | `string` | Yes      | The relative path to the file to be edited.                                 | `"src/feature_x/utils.py"`                        |
| `edit_instruction` | `string` | Yes      | A natural language description of the desired edit or the code to insert. | `"Add a function that sums two numbers"`            |
| `start_line`     | `integer`| No       | The 1-indexed line number where the edit should begin (for replace/delete).  | `10`                                              |
| `end_line`       | `integer`| No       | The 1-indexed line number where the edit should end (for replace/delete).    | `12`                                              |
| `code_block`     | `string` | No       | The actual code to insert or replace. If not provided, `edit_instruction` might be used to generate it. | `"def add(a, b):\n  return a + b"` |
| `edit_type`      | `string` | No       | Type of edit: `insert`, `replace`, `delete`. Default: `insert` if `code_block` provided and no lines, `replace` if lines provided. | `"replace"`                                     |

**JSON Schema Example:**

```json
{
  "type": "object",
  "properties": {
    "target_file": {
      "type": "string",
      "description": "The relative path to the file to be edited."
    },
    "edit_instruction": {
      "type": "string",
      "description": "A natural language description of the desired edit or the code to insert/generate."
    },
    "start_line": {
      "type": "integer",
      "description": "The 1-indexed line number where the edit should begin (for replace/delete)."
    },
    "end_line": {
      "type": "integer",
      "description": "The 1-indexed line number where the edit should end (for replace/delete)."
    },
    "code_block": {
      "type": "string",
      "description": "The actual code to insert or replace. May be generated if not provided."
    },
    "edit_type": {
      "type": "string",
      "enum": ["insert", "replace", "delete"],
      "description": "Type of edit."
    }
  },
  "required": ["target_file", "edit_instruction"]
}
```

### 4. Output Schema (Return Value)

| Field Name    | Type     | Description                                                        | Example Value                        |
| :------------ | :------- | :----------------------------------------------------------------- | :----------------------------------- |
| `status`      | `string` | `success` or `failure`.                                            | `"success"`                          |
| `file_path`   | `string` | The path of the modified file.                                     | `"src/feature_x/utils.py"`         |
| `message`     | `string` | A message indicating the result, or an error description.          | `"File updated successfully."`         |
| `diff`        | `string` | (Optional) A diff of the changes made.                             | `"--- a/src/utils.py..."`            |

**JSON Schema Example:**

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "failure"]
    },
    "file_path": {
      "type": "string"
    },
    "message": {
      "type": "string"
    },
    "diff": {
      "type": "string",
      "description": "A diff of the changes made, if available."
    }
  },
  "required": ["status", "file_path", "message"]
}
```

### 5. Error Handling

- **Error Code `FILE_NOT_FOUND`**: The specified `target_file` does not exist.
- **Error Code `PERMISSION_DENIED`**: The tool does not have permission to write to the file.
- **Error Code `EDIT_CONFLICT`**: The specified lines for editing have changed since the context was gathered.
- **Error Code `INVALID_INPUT`**: Parameters are missing or malformed.
- General error message format: `{"error": "description_of_error", "code": "ERROR_CODE"}`

### 6. Idempotency

- Idempotent: No (Applying the same edit twice could lead to duplicated code or unintended changes if the file state changes between calls).
- Side Effects: Modifies the file system by writing to the `target_file`.

### 7. Usage Examples (for MCP context)

**Example 1: Insert a new function**

```json
{
  "tool_name": "ai_code_editing.edit_file",
  "arguments": {
    "target_file": "src/utils.py",
    "edit_instruction": "Add a new Python function called 'greet' that takes a name and prints a greeting.",
    "code_block": "def greet(name):\n  print(f\"Hello, {name}!\")",
    "edit_type": "insert" // Could be inferred or explicitly set
  }
}
```

**Example 2: Replace a block of code**

```json
{
  "tool_name": "ai_code_editing.edit_file",
  "arguments": {
    "target_file": "src/calculations.py",
    "edit_instruction": "Replace the old_sum_function with a more efficient version.",
    "start_line": 15,
    "end_line": 20,
    "code_block": "def new_sum_function(arr):\n  return sum(arr)",
    "edit_type": "replace"
  }
}
```

### 8. Security Considerations

- **File System Access**: This tool directly modifies files on the user's system. It must be used with caution and ideally with user confirmation for each edit, especially in less trusted environments.
- **Code Injection**: The `code_block` content is written to files. While the LLM generates it, there's a risk of malicious or malformed code. Validation or sandboxing might be considered depending on the execution context of the modified code.
- **Scope Limitation**: It might be advisable to restrict the tool's access to only files within the current project workspace.

---

## Tool: `ai_get_code_context`

(This is an example of another potential tool. Specification would follow the same structure.)

### 1. Tool Purpose and Description

Retrieves relevant code snippets, symbol definitions, or project structure information to provide context to an LLM for code generation or analysis tasks.

(Further details would follow the pattern above...) 
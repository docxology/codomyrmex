# Model Context Protocol (MCP) - Usage Examples

This document provides practical examples related to the Model Context Protocol (MCP). It shows how other modules should structure their tool specifications and how AI agents might interact with these tools using MCP messages.

## 1. Example: Defining a Tool in a Module's `MCP_TOOL_SPECIFICATION.md`

Modules that expose functionality as MCP tools must create an `MCP_TOOL_SPECIFICATION.md` file. This file describes each tool the module offers. The structure of this file MUST follow the canonical template found in ../../../../../../src/codomyrmex/module_template/MCP_TOOL_SPECIFICATION.md and the guidelines in `model_context_protocol/MCP_TOOL_SPECIFICATION.md` (the meta-specification).

Below is a snippet illustrating how a hypothetical module, `file_utility_module`, might define a tool called `read_file_content` in its own `file_utility_module/MCP_TOOL_SPECIFICATION.md`:

```markdown
## Tool: `file_utility.read_file_content`

**Version**: 1.0.0

**Purpose and Description**:
Reads the content of a specified file and returns it as a string. This tool is useful for fetching file contents for an agent to process or analyze.

**Invocation Name**:
`file_utility.read_file_content`

**Input Schema (Parameters)**:

| Parameter Name | Type     | Required | Description                                     | Example Value         |
| :------------- | :------- | :------- | :---------------------------------------------- | :-------------------- |
| `file_path`    | `string` | Yes      | The absolute or relative path to the file.    | `"src/data/input.txt"` |
| `max_chars`    | `integer`| No       | Optional: Maximum characters to read.         | `1024`                |
| `encoding`     | `string` | No       | Optional: File encoding (e.g., "utf-8"). Default: "utf-8". | `"utf-8"`             |

**JSON Schema for `arguments`**:
```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "The absolute or relative path to the file."
    },
    "max_chars": {
      "type": "integer",
      "description": "Optional: Maximum characters to read.",
      "minimum": 1
    },
    "encoding": {
      "type": "string",
      "description": "Optional: File encoding (e.g., \"utf-8\"). Default: \"utf-8\".",
      "default": "utf-8"
    }
  },
  "required": ["file_path"]
}
```

**Output Schema (Return Value)**:

On success, the tool returns a JSON object containing the file content.

| Field Name     | Type     | Description                                      |
| :------------- | :------- | :----------------------------------------------- |
| `file_content` | `string` | The content of the file as a string.             |
| `chars_read`   | `integer`| The number of characters read from the file.     |
| `encoding_used`| `string` | The encoding used to read the file.              |

**JSON Schema for `data` (on success)**:
```json
{
  "type": "object",
  "properties": {
    "file_content": {
      "type": "string",
      "description": "The content of the file as a string."
    },
    "chars_read": {
      "type": "integer",
      "description": "The number of characters read from the file."
    },
    "encoding_used": {
      "type": "string",
      "description": "The encoding used to read the file."
    }
  },
  "required": ["file_content", "chars_read", "encoding_used"]
}
```

**Error Handling**:

Errors are returned in the standard MCP error format (see `model_context_protocol/docs/technical_overview.md`).
Common `error_type` values for this tool include:
- `FileNotFoundError`: If `file_path` does not exist.
- `PermissionError`: If the tool lacks permissions to read the file.
- `UnsupportedEncodingError`: If the specified `encoding` is not supported.
- `FileTooLargeError`: If `max_chars` is specified and the file exceeds a reasonable limit for direct reading (tool-specific).

**Idempotency**:
This tool is **idempotent**. Calling it multiple times with the same `file_path` will yield the same `file_content` (assuming the file itself has not changed externally).

**Usage Examples (for MCP context)**:

```json
{
  "tool_name": "file_utility.read_file_content",
  "arguments": {
    "file_path": "project/docs/README.md",
    "max_chars": 2000
  }
}
```

**Security Considerations**:
- **Path Traversal**: The implementation of this tool MUST validate `file_path` to prevent path traversal attacks (e.g., disallow `../../etc/passwd`). It should ideally be restricted to reading files within a predefined base directory or the project workspace.
- **Resource Limits**: Reading very large files could consume significant memory. The `max_chars` parameter offers some control, but the tool should have internal safeguards against excessive memory usage.
- **Information Disclosure**: Ensure the agent invoking this tool has legitimate reasons to access the content of the specified file. The calling system is responsible for authorizing access.
- **Encoding Attacks**: While `encoding` is specifiable, the tool should default to a safe encoding (like UTF-8) and handle encoding errors gracefully to prevent crashes or misinterpretation of malicious byte sequences.
```

---

## 2. Example: MCP Tool Call Message

This is an example of a JSON message an AI agent would construct and send to invoke the `file_utility.read_file_content` tool defined above.

```json
{
  "tool_name": "file_utility.read_file_content",
  "arguments": {
    "file_path": "src/app/main.py",
    "encoding": "utf-8"
  }
}
```

## 3. Example: MCP Tool Result Message (Success)

This is an example of a JSON message the `file_utility.read_file_content` tool would return upon successful execution.

```json
{
  "status": "success",
  "data": {
    "file_content": "def main():
  print(\"Hello, World!\")

if __name__ == \"__main__\":
  main()",
    "chars_read": 65,
    "encoding_used": "utf-8"
  },
  "error": null,
  "explanation": "Successfully read 65 characters from src/app/main.py using utf-8 encoding."
}
```

## 4. Example: MCP Tool Result Message (Failure)

This is an example of a JSON message the `file_utility.read_file_content` tool would return if it failed (e.g., file not found).

```json
{
  "status": "failure",
  "data": null,
  "error": {
    "error_type": "FileNotFoundError",
    "error_message": "The file specified by file_path could not be found.",
    "error_details": {
      "path_attempted": "src/app/non_existent_file.py"
    }
  },
  "explanation": null
}
```

These examples should guide developers in both defining their tools according to MCP and in structuring the messages for agent-tool communication.

## Common Pitfalls & Troubleshooting

- **Issue**: (A common problem users might encounter.)
  - **Solution**: (How to resolve it.) 
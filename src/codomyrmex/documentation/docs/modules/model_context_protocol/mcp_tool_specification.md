# Model Context Protocol (MCP) - Meta-Specification for Tool Definitions

## 1. Purpose of this Document

This document is the **authoritative meta-specification** for how `MCP_TOOL_SPECIFICATION.md` files must be created and maintained across all Codomyrmex modules. It does **not** define MCP tools for the `model_context_protocol` module itself (as this module defines the protocol, not tools that use it directly in the same way other modules do, unless a meta-tool like an MCP validator is introduced).

Instead, it establishes the **standards, structure, and requirements** that developers **must** adhere to when specifying tools that their respective modules expose via the Model Context Protocol (MCP). The goal is to ensure consistency, clarity, and machine-parsability of tool definitions across the entire Codomyrmex ecosystem, enabling AI agents and other systems to reliably understand and utilize these tools.

## 2. Canonical Template for MCP Tool Specifications

All modules that expose tools via MCP **must** base their `MCP_TOOL_SPECIFICATION.md` file on the canonical template located at:

[`module_template/MCP_TOOL_SPECIFICATION.md`](../../../../../../src/codomyrmex/module_template/MCP_TOOL_SPECIFICATION.md)

This template provides a detailed, commented structure covering all required sections for defining a tool. Developers should **copy this template** into their module and fill it out for each tool they expose.

## 3. Structure of a Tool Specification

As outlined in the canonical template, each tool definition within a module's `MCP_TOOL_SPECIFICATION.md` file must include the following sections:

1.  **Tool Purpose and Description**: A clear, concise explanation of what the tool does, its intended use, and any high-level operational notes.
2.  **Invocation Name**: The unique, machine-readable name used to call the tool (e.g., `ai_code_editing.generate_code_snippet`).
3.  **Input Schema (Parameters)**: A detailed definition of all input parameters the tool accepts, including their names, types, whether they are required, descriptions, and example values. **JSON Schema is the recommended standard for defining this.**
4.  **Output Schema (Return Value)**: A detailed definition of the structure of the data returned by the tool upon successful execution. This includes field names, types, descriptions, and example values. **JSON Schema is the recommended standard for defining this.**
5.  **Error Handling**: A description of potential error conditions, how errors are reported (ideally as part of the Output Schema), and any standard error codes or messages.
6.  **Idempotency**: A clear statement on whether the tool is idempotent and an explanation of its behavior on repeated calls with the same inputs.
7.  **Usage Examples (for MCP context)**: At least one complete, valid JSON example of how an AI agent would invoke the tool, including the `tool_name` and `arguments`.
8.  **Security Considerations**: A thorough discussion of potential security risks associated with using the tool and any mitigation strategies or best practices.

## 4. Defining Input and Output Schemas with JSON Schema

To ensure precision and enable automated validation, the `Input Schema (Parameters)` and `Output Schema (Return Value)` for each tool **should be defined using JSON Schema** ([json-schema.org](https://json-schema.org/)).

While the template provides a Markdown table format for readability, it is highly recommended to also include or reference a formal JSON Schema definition, especially for complex tools.

**Example Snippet for Input Schema (within the Markdown):**

```markdown
| Parameter Name | Type     | Required | Description                                      | Example Value |
| :------------- | :------- | :------- | :----------------------------------------------- | :------------ |
| `target_file`  | `string` | Yes      | The path to the file to be processed.            | `"src/main.py"` |
| `max_lines`    | `integer`| No       | Optional maximum number of lines to process.     | `100`         |
```

**Conceptual JSON Schema for the above `arguments`:**

```json
{
  "type": "object",
  "properties": {
    "target_file": {
      "type": "string",
      "description": "The path to the file to be processed."
    },
    "max_lines": {
      "type": "integer",
      "description": "Optional maximum number of lines to process."
    }
  },
  "required": ["target_file"]
}
```

Modules should provide clear JSON Schema definitions for the `arguments` object expected by the tool and for the structure of the JSON object returned by the tool on success.

## 5. Standardized Error Reporting

While specific error details will vary per tool, tools should strive to return errors in a consistent format as part of their `Output Schema`. It is recommended that if a tool call results in an error, the output JSON object includes at least:

```json
{
  "status": "failure", // Or a more specific failure status if applicable
  "error_type": "UniqueErrorCodeOrType", // e.g., "ValidationError", "FileNotFound", "ApiLimitExceeded"
  "error_message": "A descriptive message explaining the error.",
  "error_details": { // Optional: for more structured error information
    "parameter_name": "target_file", // Example if it's a validation error
    "issue": "File does not exist at the specified path."
  }
}
```

This allows the calling agent to programmatically understand and potentially handle different types of errors.
The `status` field should clearly differentiate success from failure (e.g., `"status": "success"` vs. `"status": "failure"`).

## 6. Tool Versioning

-   Each tool specification should ideally include a version number (e.g., as part of its description or a dedicated metadata field if the template is extended). Example: `Version: 1.0.2`.
-   Changes to a tool's input parameters (adding required parameters, removing parameters, changing types) or significant changes to its output schema are considered **breaking changes** and **must** result in an increment of the tool's major version (e.g., `1.x.x` to `2.0.0`).
-   Adding new optional parameters or adding new non-breaking fields to the output is generally considered a minor or patch update.
-   The `Invocation Name` should remain stable. If a breaking change is so significant that it represents a fundamentally different tool, a new invocation name with its own versioning should be considered.
-   The overall MCP protocol will also have its own version, managed by this `model_context_protocol` module.

## 7. Key Principles for Defining MCP Tools

When defining tools for your module, adhere to the following principles, which are also embedded in the canonical template's instructions:

1.  **Clarity and Conciseness**: The tool's purpose, inputs, outputs, and behavior must be immediately understandable to both human developers and AI agents. Use precise language.
2.  **Action-Oriented & Granular**: Tools should represent discrete, well-defined actions or queries that an LLM or other agent can meaningfully invoke to achieve a specific step in a larger task. Avoid overly broad or multi-purpose tools.
3.  **Well-Defined Schemas (using JSON Schema)**: Input and output schemas must be precisely defined using JSON Schema. Clearly specify data types (string, integer, boolean, object, array), format constraints (e.g., for dates, URIs), required vs. optional fields, and provide clear descriptions for each field.
4.  **Robust and Predictable Error Handling**: Define how your tool reports errors clearly and consistently, following the Standardized Error Reporting guidelines (Section 5). Be specific about potential error conditions an agent might encounter.
5.  **Idempotency Considerations**: Clearly state whether your tool is idempotent (i.e., calling it multiple times with the same inputs has the same effect as calling it once). Explain any side effects of repeated calls.
6.  **Security First**: Pay close attention to the security implications of your tool. This is especially critical if it involves file system access, network requests, code execution, data modification, or handling sensitive information. The "Security Considerations" section in the tool spec must be detailed and actionable.
7.  **Practical and Valid Examples**: Provide realistic, complete, and valid JSON usage examples in the MCP format to illustrate exactly how the tool should be called by an agent.
8.  **Testability**: Design tools in a way that they can be reliably tested, both at the unit level (mocking dependencies) and integration level (as part of an agent workflow, if feasible).

## 8. Responsibility

Each module owner/development team is responsible for:
-   Creating and maintaining an `MCP_TOOL_SPECIFICATION.md` file for all tools exposed by their module.
-   Ensuring this specification strictly adheres to the canonical template and the guidelines laid out in this meta-specification document.
-   Keeping the tool specifications accurate and up-to-date with the actual behavior of the tools.
-   Properly versioning their tools when changes are made.

## 9. Future Enhancements

As the Model Context Protocol and the Codomyrmex project evolve, the canonical template and these meta-specification guidelines may be updated. Module developers should refer back to this document and the ../../../../../../src/codomyrmex/module_template/MCP_TOOL_SPECIFICATION.md periodically for the latest standards. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

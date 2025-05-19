# [Module Name] - MCP Tool Specification Template

This document serves as a template for defining tools within the `[Module Name]` module that are intended to be integrated with the Model Context Protocol (MCP).

**Instructions for Use:**
1.  Replace `[Module Name]` in the title above and throughout this document with the actual name of your module.
2.  For each tool you define, copy the "Tool: `[YourToolName]`" section.
3.  Replace all bracketed placeholders (e.g., `[YourToolName]`, `[Brief description...]`, `[ParameterName]`, `[DataType]`, etc.) with specific details for your tool.
4.  Provide concrete examples for Input/Output schemas and MCP usage.
5.  If a section (like Idempotency or specific Security Considerations beyond general file path validation) is not applicable, clearly state "N/A" or provide a relevant explanation.
6.  Refer to the `model_context_protocol` module's documentation for overarching MCP guidelines and schema definitions.

## General Considerations for [Module Name] Tools

- **Dependencies**: Clearly list any other Codomyrmex modules or significant external libraries required by the tools in this module. (e.g., "All tools require the `logging_monitoring` module. Ensure `setup_logging()` is called.")
- **Initialization**: Specify any module-level initialization required before tools can be invoked.
- **Error Handling**: Describe the general error handling strategy for tools in this module (e.g., "Errors are logged using `logging_monitoring`. Tools return an `{'error': 'description'}` object on failure.").
- **Security**: Outline any module-wide security considerations. Specific tool security notes can be added to each tool's section.

---

## Tool: `[YourToolName]`

### 1. Tool Purpose and Description

[Brief description of what the tool does, its primary function, and its intended use case within the MCP framework.]

### 2. Invocation Name

`[your_tool_invocation_name]`
(This should be a unique, descriptive name, typically in snake_case, used to call the tool via MCP.)

### 3. Input Schema (Parameters)

Describe the expected input parameters for the tool. Use a table format.

| Parameter Name   | Type        | Required | Description                                      | Example Value      |
| :-------------- | :---------- | :------- | :----------------------------------------------- | :----------------- |
| `[Parameter1Name]` | `[DataType]` | Yes/No   | `[Description of parameter1]`                  | `[ExampleValue1]`  |
| `[Parameter2Name]` | `[DataType]` | Yes/No   | `[Description of parameter2 (e.g., optional, with default value X)]` | `[ExampleValue2]`  |
| `output_path`   | `string`    | No       | `[Commonly, if the tool generates a file: File path to save the output. If None/not provided, behavior should be defined (e.g., not saved, returned directly).]` | `"./output/[module_name]/[tool_name]/result.txt"`  |
| `...`           | `...`       | ...      | `...`                                            | `...`              |

**Notes on Input Schema:**
- Specify data types clearly (e.g., `string`, `integer`, `float`, `boolean`, `array[string]`, `object`, `enum["val1", "val2"]`).
- For complex objects, you might reference a JSON schema definition or detail the object structure.

### 4. Output Schema (Return Value)

Describe the structure of the data returned by the tool upon successful execution.

| Field Name      | Type        | Description                                                                   | Example Value      |
| :-------------- | :---------- | :---------------------------------------------------------------------------- | :----------------- |
| `[ResultField1]`| `[DataType]`| `[Description of the result field]`                                           | `[ExampleResult1]` |
| `[ResultField2]`| `[DataType]`| `[Description of another result field]`                                       | `[ExampleResult2]` |
| `output_path`   | `string`    | `[If applicable: The path where the output file was saved. Null if not saved.]` | `"./output/[module_name]/[tool_name]/result.txt"` |
| `status`        | `string`    | `[e.g., "success", "completed_with_warnings"]`                                | `"success"`        |

**Notes on Output Schema:**
- Clearly define what constitutes a successful output.
- If the tool primarily has side effects (e.g., saving a file, modifying system state) and doesn't return substantial data, reflect that (e.g., `{"status": "success", "message": "Operation completed."}`).

### 5. Error Handling

- **Specific Errors**: Detail any specific error conditions or codes the tool might return, beyond general module errors.
    - `[ErrorCode1]`: `[Description of error and when it occurs]`
    - `[ErrorCode2]`: `[Description of error and when it occurs]`
- **Return Format on Error**: Reiterate or specify the error object format (e.g., `{"error": "Specific error message related to [YourToolName]", "details": {...}}`).

### 6. Idempotency

- **Idempotent**: Yes/No/Partially
- **Explanation**: `[Explain why the tool is or isn't idempotent. If not fully idempotent, describe the conditions under which repeated calls might have different effects (e.g., if it modifies state or relies on external non-idempotent services).]`
    - Example (Idempotent): "Yes. Calling the tool multiple times with the same input parameters will produce the same output file (if `output_path` is specified) or return the same result without further side effects."
    - Example (Not Idempotent): "No. Each call creates a new unique resource."

### 7. Usage Examples (for MCP context)

Provide one or more examples of how this tool would be invoked within an MCP message. Use JSON format.

```json
{
  "tool_name": "[your_tool_invocation_name]",
  "arguments": {
    "[Parameter1Name]": "[ExampleValue1]",
    "[Parameter2Name]": "[ExampleValue2]"
    // Add other necessary arguments for a comprehensive example
  }
}
```

### 8. Security Considerations

- **Input Validation**: `[Describe any specific input validation performed by the tool beyond basic type checking, especially for strings that might be used in file paths, commands, or queries.]`
- **Permissions**: `[If the tool interacts with the file system, network, or other system resources, specify any required permissions for the environment executing the tool.]`
- **Data Handling**: `[Note any sensitive data types handled by the tool and how they are protected (e.g., "User IDs are processed but not logged").]`
- **Output Sanitization**: `[If the tool's output could be displayed in a sensitive context, mention any sanitization performed.]`
- **File Paths**: (If `output_path` or similar is used) "Ensure that any user-supplied file paths are rigorously validated and restricted to designated writable directories to prevent unauthorized file access, overwrites, or path traversal vulnerabilities. The application running the MCP tool server must operate with appropriate, least-privilege file system permissions."

---
<!-- Add more tool specifications below by copying the "Tool: `[YourToolName]`" section. --> 
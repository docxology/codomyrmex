# Model Context Protocol (MCP) - Tool Specification Guidelines

## Purpose of this Document

This document serves as the **meta-specification** for how `MCP_TOOL_SPECIFICATION.md` files should be created and maintained across all Codomyrmex modules. It does not define MCP tools for the `model_context_protocol` module itself (as this module defines the protocol, not tools that use it directly in the same way other modules do).

Instead, it establishes the standards and points to the resources developers should use when specifying tools that their modules expose via the Model Context Protocol.

## Canonical Template for MCP Tool Specifications

All modules that expose tools via MCP **must** use the canonical template located at:

[`template/module_template/MCP_TOOL_SPECIFICATION.md`](../../template/module_template/MCP_TOOL_SPECIFICATION.md)

This template provides a detailed structure and instructions for defining:
- Tool Purpose and Description
- Invocation Name
- Input Schema (Parameters)
- Output Schema (Return Value)
- Error Handling
- Idempotency
- Usage Examples (for MCP context)
- Security Considerations

## Key Principles for Defining MCP Tools

When defining tools for your module, adhere to the following principles, which are also embedded in the template's instructions:

1.  **Clarity and Conciseness**: The tool's purpose, inputs, and outputs should be immediately understandable.
2.  **Action-Oriented**: Tools should represent discrete actions or queries that an LLM or other agent can meaningfully invoke.
3.  **Well-Defined Schemas**: Input and output schemas must be precise. Use clear data types and specify required fields. The template provides guidance on using tables or JSON Schema snippets.
4.  **Robust Error Handling**: Define how your tool reports errors. Be specific about potential error conditions.
5.  **Idempotency Considerations**: Clearly state whether your tool is idempotent and explain any side effects of repeated calls.
6.  **Security First**: Pay close attention to the security implications of your tool, especially if it involves file system access, network requests, code execution, or handling sensitive data. The template includes a dedicated section for this.
7.  **Practical Examples**: Provide realistic usage examples in the MCP JSON format to illustrate how the tool should be called.

## Responsibility

Each module owner is responsible for ensuring their `MCP_TOOL_SPECIFICATION.md` accurately reflects the tools their module provides and adheres to the structure and guidelines provided by the canonical template.

## Future Enhancements

As the Model Context Protocol evolves, the canonical template and these guidelines may be updated. Module developers should refer back to this document and the template periodically. 
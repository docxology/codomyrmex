# Security Policy for Model Context Protocol

This document outlines security procedures and policies specifically relevant to the Model Context Protocol (MCP) and its implementation within the Codomyrmex ecosystem.

## Reporting a Vulnerability

If you discover a security vulnerability related to the MCP specification itself, its reference implementations (if any provided by this module), or its interaction with other Codomyrmex modules, please report it to us as soon as possible.
We take all security reports seriously.

**DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email blanket@activeinference.institute with the subject line: "SECURITY Vulnerability Report: Model Context Protocol - [Brief Description]".

Please include the following information in your report:

- A description of the vulnerability and its potential impact.
- Steps to reproduce the vulnerability, including any specific configurations or conditions required.
- Any proof-of-concept code or examples.
- The version(s) of the MCP specification or related module(s) affected.
- Your name and contact information (optional).

We aim to acknowledge receipt of your vulnerability report within 2-3 business days and will work with you to understand and remediate the issue. We may request additional information if needed.

Public disclosure of the vulnerability will be coordinated with you after the vulnerability has been fixed and an update is available, or after a reasonable period if a fix is not immediately possible.

## Security Updates

Updates to the MCP specification or security guidance will be documented in the [CHANGELOG.md](./CHANGELOG.md) and may be part of regular version updates to the `model_context_protocol` module. Critical vulnerabilities might warrant immediate updates and notifications.

## Scope

This security policy applies to the Model Context Protocol specification, its meta-specification for tool definitions (`MCP_TOOL_SPECIFICATION.md` in this module), and the general security implications of using MCP for agent-tool communication within Codomyrmex.

## Key Security Considerations for MCP Implementations & Tool Developers

The Model Context Protocol facilitates communication; therefore, security relies heavily on the secure implementation of both the AI agents consuming MCP and the tools exposing functionality via MCP.

1.  **Data Validation is Critical**: 
    *   **Strict Schema Adherence**: All systems sending or receiving MCP messages **must** strictly validate these messages against the defined JSON Schemas (for Tool Calls, Tool Results, and Error Objects as outlined in `docs/technical_overview.md`). Reject any messages that do not conform. This is the first line of defense against malformed or malicious payloads.
    *   **Secure Schema Parsing**: Agents or systems that dynamically load or parse JSON Schema definitions from `MCP_TOOL_SPECIFICATION.md` files must do so securely. Malformed or overly complex schemas could be a vector for denial-of-service or other attacks against the parsing system.

2.  **Authentication and Authorization of Tool Calls**: 
    *   **MCP is a Protocol, Not an Auth System**: MCP messages themselves do not inherently carry authenticated user identity or authorization tokens. 
    *   **Responsibility of the Tool Hosting Environment**: The system or service that receives an MCP Tool Call message and dispatches it to the actual tool implementation is **solely responsible** for: 
        *   **Authentication**: Verifying the identity of the source of the MCP message (e.g., the AI agent or the user on whose behalf the agent is acting).
        *   **Authorization**: Ensuring the authenticated identity has the explicit permission to invoke the specified `tool_name` with the provided `arguments`. This includes checks against access control lists (ACLs), roles, or other permission models.
    *   Authorization should be granular, considering not just the tool, but potentially the specific resources or actions the tool might take based on its arguments.

3.  **Input Sanitization and Parameter Handling by Tools**: 
    *   Even if an MCP Tool Call message validates against its schema, the *values* within the `arguments` object might originate from untrusted sources (e.g., user input to an LLM).
    *   Individual tool implementations **must** treat all incoming parameters as potentially unsafe and perform appropriate sanitization and validation before using them in security-sensitive operations (e.g., OS commands, file paths, database queries, HTML rendering, external API calls).
    *   Apply the principle of least privilege: if a tool parameter is used to construct a file path, ensure it cannot be used for directory traversal.

4.  **Secure Tool Design (`MCP_TOOL_SPECIFICATION.md` and Implementation)**:
    *   **Truth in Advertising**: A tool's `MCP_TOOL_SPECIFICATION.md` must accurately represent its behavior, especially its security considerations. Misleading specifications can lead to agents misusing tools.
    *   **Integrity of Specifications**: Protect `MCP_TOOL_SPECIFICATION.md` files from unauthorized modification. If an attacker can alter a tool specification, they might trick an agent into performing unintended actions.
    *   **Principle of Least Privilege**: Tools should be designed to operate with the minimum permissions necessary to perform their stated function.

5.  **Confidentiality and Integrity of MCP Messages**: 
    *   If MCP messages (Tool Calls or Tool Results) carry sensitive information, the transport mechanism used (e.g., inter-process communication, network protocols) **must** ensure:
        *   **Confidentiality**: Encryption in transit to prevent eavesdropping (e.g., using TLS for network communication).
        *   **Integrity**: Mechanisms to prevent tampering with messages in transit (e.g., MACs, digital signatures if appropriate for the transport).

6.  **Error Handling and Information Disclosure**: 
    *   Error messages returned in MCP Tool Result messages should be informative but **must not** leak sensitive internal system details, stack traces, or private data that could aid an attacker.
    *   Use the structured error format (with `error_type`, `error_message`, `error_details`) to provide clear, actionable error information without verbosity that might compromise security.

7.  **Rate Limiting and Resource Management**: 
    *   Systems exposing tools via MCP should implement rate limiting on tool invocations to prevent abuse, brute-forcing of parameters, or denial-of-service (DoS) attacks against the tools or underlying resources.
    *   Monitor resource consumption by tools. Implement safeguards against tools that might be triggered (intentionally or unintentionally) in ways that lead to excessive CPU, memory, network, or disk usage.

8.  **Logging and Monitoring**: 
    *   Maintain detailed logs of MCP tool calls and results, including the `tool_name`, key arguments (potentially scrubbed of sensitive data), and the `status` of the operation.
    *   Regularly review these logs for suspicious activity, repeated errors, or patterns indicative of attempted abuse.

9.  **Dependencies and Supply Chain**: 
    *   Be mindful of the security of libraries used in this `model_context_protocol` module (e.g., `jsonschema`) and in any tool implementations. Keep dependencies up to date.

## Security of this Module (`model_context_protocol`)

-   This module primarily provides specifications, templates (`template/module_template/MCP_TOOL_SPECIFICATION.md`), and potentially schema validation utilities.
-   If this module provides Python-based validation utilities (e.g., using `jsonschema` as listed in its `requirements.txt`), vulnerabilities in those libraries could affect systems using these utilities. Keep these dependencies updated.

Thank you for helping keep Codomyrmex and the Model Context Protocol secure. 
# Security - MCP Tool Specification

This document outlines the specification for tools within the Security module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Security module provides comprehensive security capabilities organized into four specialized submodules -- digital (vulnerability scanning, secrets detection, compliance checking, encryption, SSL validation, security reporting), physical (access control, asset inventory, surveillance, perimeter management), cognitive (social engineering detection, phishing analysis, awareness training, behavior analysis), and theory (security principles, frameworks, threat modeling, risk assessment, best practices) -- for internal use by other Codomyrmex modules. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. While several of this module's functions have tool-like signatures (e.g., `scan_vulnerabilities`, `scan_file_for_secrets`, `check_compliance`, `analyze_file_security`), they operate on filesystem paths and stateful security infrastructure that requires careful access control and context that does not translate well to ad-hoc MCP invocation.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., scanning a code snippet for security vulnerabilities without filesystem access, running a compliance check against a configuration payload, or generating a threat model from structured input), this document will be updated accordingly.

For details on how to use the security functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

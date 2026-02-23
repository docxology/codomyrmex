# Utils - MCP Tool Specification

This document outlines the specification for tools within the Utils module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Utils module provides common utility functions and helpers used across the Codomyrmex codebase including subprocess execution, JSON handling, file/path utilities, retry decorators, timing utilities, script execution base classes, health checking, and module registry infrastructure for internal use by other Codomyrmex modules. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal utility functions, subprocess wrappers, and infrastructure helpers do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., running a health check across registered modules and returning structured status, or executing a command and returning structured output), this document will be updated accordingly.

For details on how to use the utils functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

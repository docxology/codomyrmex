# IDE - MCP Tool Specification

This document outlines the specification for tools within the IDE module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The IDE module provides programmatic integration and automation capabilities for various Integrated Development Environments for internal use by other Codomyrmex modules, including Cursor AI-first code editor, Visual Studio Code, and Google DeepMind Antigravity IDE support. It enables AI agents to achieve maximum agentic operation of IDEs through an abstract IDEClient interface with command execution, file management, event handling, and batch operations. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal IDE automation mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., executing an IDE command in a connected session, or querying the list of open files), this document will be updated accordingly.

For details on how to use the ide functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

# Tools - MCP Tool Specification

This document outlines the specification for tools within the Tools module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Tools module provides development utilities and helper tools for project analysis, dependency management, and maintenance tasks including project structure analysis, dependency analysis and consolidation, code quality metrics, circular import detection, and deprecation notice management for internal use by other Codomyrmex modules. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal project analysis, dependency management, and maintenance utility mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., analyzing a project directory and returning a structured dependency graph, or running code quality checks and returning scored results), this document will be updated accordingly.

For details on how to use the tools functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

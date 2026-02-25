# Templating - MCP Tool Specification

This document outlines the specification for tools within the Templating module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Templating module provides template engine support (Jinja2, Mako) for code generation, documentation templates, and dynamic content rendering with convenience functions for string and file-based template rendering for internal use by other Codomyrmex modules. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal template rendering and engine management mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., rendering a template string with provided context data on demand, or listing available template files), this document will be updated accordingly.

For details on how to use the templating functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

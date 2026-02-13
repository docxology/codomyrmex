# Tree-sitter - MCP Tool Specification

This document outlines the specification for tools within the Tree-sitter module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Tree-sitter module provides AST (Abstract Syntax Tree) parsing capabilities using tree-sitter grammars, including language management, source code parsing, query execution, and AST transformations for internal use by other Codomyrmex modules. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal AST parsing, query execution, and transformation mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., parsing a code snippet and returning a structured AST representation, or extracting function/class definitions from source code on demand), this document will be updated accordingly.

For details on how to use the tree_sitter functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

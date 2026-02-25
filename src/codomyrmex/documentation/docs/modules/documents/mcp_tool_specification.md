# Documents - MCP Tool Specification

This document outlines the specification for tools within the Documents module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Documents module provides robust, abstractable methods for reading and writing various document formats for internal use by other Codomyrmex modules, including support for multiple formats (markdown, JSON, PDF, YAML, XML, CSV, HTML, text), document operations (read, write, parse, validate, convert, merge, split), metadata extraction and management, document search and indexing, templates and formatting, and document versioning. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal document I/O mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., converting a document between formats at a given path, or extracting metadata from a document file), this document will be updated accordingly.

For details on how to use the documents functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

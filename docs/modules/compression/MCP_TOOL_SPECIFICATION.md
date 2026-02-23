# Compression - MCP Tool Specification

This document outlines the specification for tools within the Compression module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Compression module provides data compression utilities and archive handling for internal use by other Codomyrmex modules, including gzip, zlib, ZIP, and Zstandard format support, configurable compression levels, stream-based and parallel compression, automatic format detection, and file/archive compression and extraction. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal data compression mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., compressing a file at a given path and returning the compressed output path, or listing contents of an archive), this document will be updated accordingly.

For details on how to use the compression functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

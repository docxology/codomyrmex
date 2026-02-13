# Schemas - MCP Tool Specification

This document outlines the specification for tools within the Schemas module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Schemas module provides the shared schema registry and standardized type definitions (Result, Config, Task, CodeEntity, Deployment, Pipeline, Metric, and others) used across all Codomyrmex modules to enable cross-module interoperability. As a Foundation layer type library, these are data structures rather than invocable actions, and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal type definitions and schema registry mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., validating arbitrary data against registered schemas, or listing all available schema types with their field definitions), this document will be updated accordingly.

For details on how to use the schemas functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

# Dependency Injection - MCP Tool Specification

This document outlines the specification for tools within the Dependency Injection module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Dependency Injection module provides internal IoC container infrastructure (`Container`, `Scope`, `ScopeContext`, decorators) for programmatic use within the codomyrmex application. These components manage service lifetimes and constructor-based dependency injection and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal container and resolution mechanisms do not fit this paradigm.

If future enhancements introduce features appropriate for MCP (e.g., a tool to query container registrations at runtime, or to dynamically register services via external command), this document will be updated accordingly.

For details on how to use the dependency injection facilities within your Python code, refer to the module's [README.md](README.md) and [API_SPECIFICATION.md](API_SPECIFICATION.md).

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

# Feature Flags - MCP Tool Specification

This document outlines the specification for tools within the Feature Flags module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Feature Flags module provides feature flag management capabilities for internal use by other Codomyrmex modules, including flag evaluation, rollout strategies, storage backends, and a FeatureManager for centralized flag lifecycle management. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal feature flag evaluation mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., toggling a feature flag by name, or querying the current state of all flags for a given context), this document will be updated accordingly.

For details on how to use the feature_flags functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

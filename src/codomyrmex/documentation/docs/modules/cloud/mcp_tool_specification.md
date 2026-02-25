# Cloud - MCP Tool Specification

This document outlines the specification for tools within the Cloud module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Cloud module provides integrations with various cloud service APIs for internal use by other Codomyrmex modules, including Coda.io document and database API, AWS S3, Google Cloud Storage, Azure Blob Storage, and Infomaniak OpenStack-based public cloud services (Compute, Storage, Network, DNS, Heat, and more). These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal cloud provider abstraction mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., listing cloud resources across providers, or performing a cross-cloud storage operation), this document will be updated accordingly.

For details on how to use the cloud functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

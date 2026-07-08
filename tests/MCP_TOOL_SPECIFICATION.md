# Tests - MCP Tool Specification

This document outlines the specification for tools within the Tests module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Tests module contains the project's test infrastructure including unit tests, integration tests, and test utilities. Test execution is already exposed via the `codomyrmex.run_tests` MCP tool in the PAI MCP bridge, which runs pytest for specific modules or the whole project.

The test files themselves are not suitable for direct MCP exposure as they are meant to be invoked through pytest rather than as standalone tools.

For running tests via MCP, use:
- `codomyrmex.run_tests` — Run pytest for a specific module or the whole project
- `codomyrmex.run_tests(module="agents")` — Run tests for a specific module

For details on the test infrastructure, refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

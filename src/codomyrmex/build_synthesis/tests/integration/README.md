# src/codomyrmex/build_synthesis/tests/integration

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration tests for the Build Synthesis module. These tests verify the full lifecycle of complex builds and module synthesis operations, ensuring correct directory creation and artifact generation.

## Test Areas

- **Full Module Synthesis**: testing the `synthesize_code_component` tool on multiple module types.
- **Multi-component Builds**: orchestration of builds across multiple dependent modules.
- **MCP Tool Registration**: Verifying that build tools are correctly exposed and callable via MCP.

## Navigation
- **Project Root**: [README](../../../../../README.md)
- **Parent Directory**: [tests](../README.md)
- **Src Hub**: [src](../../../../../src/README.md)
# src/codomyrmex/code_execution_sandbox/tests/unit

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Unit tests for the Code Execution Sandbox components. These tests ensure that the foundational isolation and monitoring functions perform correctly in isolation.

## Test Areas

- **Cgroup/Resource Limits**: Verifying that CPU/MEM limits are correctly parsed and applied.
- **Environment Isolation**: Ensuring that temporary directories are correctly mapped and isolated.
- **Process Management**: Testing the ability to track and terminate sub-processes within the sandbox.

## Navigation
- **Project Root**: [README](../../../../../README.md)
- **Parent Directory**: [tests](../README.md)
- **Src Hub**: [src](../../../../../src/README.md)
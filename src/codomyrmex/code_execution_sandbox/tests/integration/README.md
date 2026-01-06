# src/codomyrmex/code_execution_sandbox/tests/integration

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration tests for the Code Execution Sandbox. These tests verify the full lifecycle of execution tasks, from environment initialization to final output collection and cleanup.

## Test Areas

- **End-to-End Execution**: Running complex Python scripts and verifying standard output/error capture.
- **Escape Prevention**: Attempting to breach sandbox isolation to verify security controls.
- **Cleanup Verification**: Ensuring that all resources are released and temporary files are deleted after execution.

## Navigation
- **Project Root**: [README](../../../../../README.md)
- **Parent Directory**: [tests](../README.md)
- **Src Hub**: [src](../../../../../src/README.md)
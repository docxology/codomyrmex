# src/codomyrmex/git_operations/tests/integration

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration tests for the Git Operations module. These tests verify the end-to-end functionality of complex git workflows, including interactions with live (temporary) repositories and mock remote services.

## Test Areas

- **Workflow Orchestration**: Testing the full lifecycle of a feature branch from creation to PR and merge.
- **Cross-module Integration**: Verifying how `git_operations` works with `build_synthesis` (e.g., tagging builds).
- **Fallback Logic**: Testing system behavior when remote APIs return errors or time out.

## Navigation
- **Project Root**: [README](../../../../../README.md)
- **Parent Directory**: [tests](../README.md)
- **Src Hub**: [src](../../../../../src/README.md)
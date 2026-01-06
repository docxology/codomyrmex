# src/codomyrmex/code_review/tests/integration

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration tests for the Code Review module. These tests verify the full review pipeline, from initial code ingestion to final consolidated feedback and metric reporting.

## Test Areas

- **Review Pipeline Orchestration**: Testing the sequence of multiple analysis passes on full module directories.
- **Cross-module Feedback**: Verifying how `code_review` interacts with `git_operations` to post comments on simulated PRs.
- **E2E Quality Gates**: Testing droids that blocking "merges" when quality scores fall below the specified threshold.

## Navigation
- **Project Root**: [README](../../../../../README.md)
- **Parent Directory**: [tests](../README.md)
- **Src Hub**: [src](../../../../../src/README.md)
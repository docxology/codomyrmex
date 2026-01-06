# src/codomyrmex/ai_code_editing/tests/integration

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration tests for the AI Code Editing module. These tests verify the end-to-end functionality of coding droids, ensuring that different components (composition, provider interface, and output validation) work together correctly.

## Test Areas

- **Droid Workflows**: Testing full task execution from prompt to final code output.
- **Provider Fallback**: Verifying that the system correctly switches providers when one is unavailable.
- **Rate Limit Resilience**: Ensuring retry logic handled across multiple simulated requests.
- **Multi-task Sequencing**: Testing droids on sequences of related coding tasks.

## Navigation
- **Project Root**: [README](../../../../../README.md)
- **Parent Directory**: [tests](../README.md)
- **Src Hub**: [src](../../../../../src/README.md)
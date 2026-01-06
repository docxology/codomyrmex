# code/tests

## Signposting
- **Parent**: [Code Module](../README.md)
- **Siblings**: [execution](../execution/), [sandbox](../sandbox/), [review](../review/), [monitoring](../monitoring/)
- **Children**:
    - [execution](execution/)
    - [sandbox](sandbox/)
    - [review](review/)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Test suite for the code module, providing comprehensive unit and integration tests for execution, sandboxing, review, and monitoring components.

## Test Categories

### execution/
Tests for the code execution engine including language support, session management, and executor functionality.

### sandbox/
Tests for sandbox isolation, container management, resource limits, and security controls.

### review/
Tests for automated code review, analysis, and quality metrics.

## Running Tests

```bash
# Run all code module tests
pytest src/codomyrmex/code/tests/

# Run specific test category
pytest src/codomyrmex/code/tests/sandbox/
pytest src/codomyrmex/code/tests/execution/
pytest src/codomyrmex/code/tests/review/
```

## Navigation Links

- **Parent**: [Code Module](../README.md)
- **Code AGENTS**: [../AGENTS.md](../AGENTS.md)

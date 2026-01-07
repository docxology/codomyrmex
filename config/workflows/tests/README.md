# tests

## Signposting
- **Parent**: [workflows](../README.md)
- **Children**: None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Test workflows used for system validation, performance testing, and error handling verification.

## Test Workflows

### concurrent_workflow_0/1/2.json
Concurrent execution test workflows. Used to validate:
- Parallel workflow execution
- Resource management
- Concurrent step handling

### error_test_workflow.json
Error handling test workflow. Uses:
- Non-existent module (`nonexistent_module`)
- Non-existent action (`nonexistent_action`)

Validates:
- Error detection and reporting
- Graceful failure handling
- Error logging

### perf_test_workflow.json
Performance testing workflow. Used to:
- Measure workflow execution time
- Validate performance monitoring
- Test timeout handling

### test_workflow.json
Basic test workflow with environment setup. Used for:
- Basic workflow execution validation
- Environment check integration
- Simple dependency testing

## Usage

These workflows are used by the test suite. They are not loaded by default in production environments.

To run tests:
```bash
pytest src/codomyrmex/tests/unit/project_orchestration/
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [workflows](../README.md)
- **Project Root**: [README](../../../README.md)


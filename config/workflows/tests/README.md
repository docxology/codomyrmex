# tests

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Workflow fixtures for orchestration tests (see [../README.md](../README.md)
for the format). `error_test_workflow.json` fails on purpose: its action does
not exist.

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `concurrent_workflow_0.json`, `concurrent_workflow_1.json`, `concurrent_workflow_2.json` – identical single-step workflows for concurrency tests
- `error_test_workflow.json` – intentionally fails (`environment_setup.nonexistent_action_for_error_tests`)
- `perf_test_workflow.json` – single quick step for timing overhead
- `test_workflow.json` – smoke test: `environment_setup.validate_environment`

## Navigation

- **Parent Directory**: [workflows](../README.md)
- **Project Root**: ../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

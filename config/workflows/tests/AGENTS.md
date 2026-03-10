# Codomyrmex Agents — config/workflows/tests

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `concurrent_workflow_0.json` – Project file
- `concurrent_workflow_1.json` – Project file
- `concurrent_workflow_2.json` – Project file
- `error_test_workflow.json` – Project file
- `perf_test_workflow.json` – Project file
- `test_workflow.json` – Project file

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `PAI.md`
- `README.md`
- `SPEC.md`
- `concurrent_workflow_0.json`
- `concurrent_workflow_1.json`
- `concurrent_workflow_2.json`
- `error_test_workflow.json`
- `perf_test_workflow.json`
- `test_workflow.json`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [workflows](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation

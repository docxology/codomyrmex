# Codomyrmex Agents — src/codomyrmex/code_review/tests

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2025

## Purpose
Test agents for validating code review functionality and ensuring analysis accuracy.

## Active Components
- `unit/` – Agent surface for `unit` components.
- `integration/` – Agent surface for `integration` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Test agents verify code review accuracy across all supported programming languages.
- Pyscn integration testing maintains high-performance analysis validation.
- Security scanning tests identify vulnerabilities without false positives exceeding threshold.

## Test Coverage Areas
- **Unit Tests**: Individual component testing with mocked dependencies
- **Integration Tests**: Full workflow testing with real pyscn and external tools
- **Performance Tests**: Analysis speed and memory usage validation
- **Accuracy Tests**: False positive/negative rate verification

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.


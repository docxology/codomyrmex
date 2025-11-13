# Codomyrmex Agents — src/codomyrmex/static_analysis/tests

## Purpose
Test suite for static analysis functionality, covering unit tests for individual components and integration tests for complete analysis workflows, ensuring code quality, security, and performance analysis capabilities.

## Active Components
- `integration/` – Agent surface for `integration` components.
- `unit/` – Agent surface for `unit` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Tests maintain comprehensive coverage of static analysis functionality.
- Test execution validates code quality, security, and performance analysis capabilities.

## Related Modules
- **Static Analysis Module** (`../`) - Provides the module being tested
- **Unit Tests** (`unit/`) - Unit-level test validation
- **Integration Tests** (`integration/`) - Integration test scenarios

## Navigation Links
- **📚 Module Overview**: [../README.md](../README.md) - Static analysis module documentation
- **🧪 Unit Tests**: [unit/AGENTS.md](unit/AGENTS.md) - Unit test coordination
- **🧪 Integration Tests**: [integration/AGENTS.md](integration/AGENTS.md) - Integration test coordination
- **🏠 Package Root**: [../../../README.md](../../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../../docs/README.md](../../../../docs/README.md) - Complete documentation

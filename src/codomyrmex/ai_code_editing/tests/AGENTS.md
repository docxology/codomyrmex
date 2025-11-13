# Codomyrmex Agents — src/codomyrmex/ai_code_editing/tests

## Purpose
Test suite for ai code editing functionality, covering unit tests for individual components and integration tests for complete workflows.

## Active Components
- `integration/` – Agent surface for `integration` components.
- `unit/` – Agent surface for `unit` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Tests maintain comprehensive coverage of AI code editing functionality.
- Test execution validates code generation, refactoring, and droid automation capabilities.

## Related Modules
- **AI Code Editing Module** (`../`) - Provides the module being tested
- **Unit Tests** (`unit/`) - Unit-level test validation
- **Integration Tests** (`integration/`) - Integration test scenarios

## Navigation Links
- **📚 Module Overview**: [../README.md](../README.md) - AI code editing module documentation
- **🧪 Unit Tests**: [unit/AGENTS.md](unit/AGENTS.md) - Unit test coordination
- **🧪 Integration Tests**: [integration/AGENTS.md](integration/AGENTS.md) - Integration test coordination
- **🏠 Package Root**: [../../../README.md](../../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../../docs/README.md](../../../../docs/README.md) - Complete documentation

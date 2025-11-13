# Codomyrmex Agents — testing/unit

## Purpose
Unit-level validation harnesses executed by testing agents.

## Active Components
- Key files: test_ai_code_editing.py, test_api_documentation.py, test_build_synthesis.py, test_ci_cd_automation.py

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Unit tests maintain comprehensive coverage and validate individual component functionality.
- Test execution maintains isolation and reproducibility across different environments.

## Related Modules
- **Integration Testing** (`../integration/`) - Provides integration test scenarios
- **Testing Suite** (`../`) - Coordinates overall testing strategy

## Navigation Links
- **📚 Testing Overview**: [../README.md](../README.md) - Testing suite documentation
- **🧪 Integration Tests**: [../integration/AGENTS.md](../integration/AGENTS.md) - Integration test coordination
- **🏠 Project Root**: [../../README.md](../../README.md) - Main project README
- **📖 Documentation Hub**: [../../docs/README.md](../../docs/README.md) - Complete documentation structure
- **🧪 Testing Strategy**: [../../docs/development/testing-strategy.md](../../docs/development/testing-strategy.md) - Testing approach and best practices

# Codomyrmex Agents — src/codomyrmex/ai_code_editing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2025

## Purpose
Code editing agents, including droid automation and refactoring utilities.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `droid/` – Agent surface for `droid` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All AI code generation maintains security boundaries and validates inputs before processing.
- Code refactoring operations preserve original functionality while improving structure and performance.
- Droid automation maintains execution safety with timeout and resource limits.

## Related Modules
- **Language Models** (`language_models/`) - Provides LLM integration for code generation
- **Static Analysis** (`static_analysis/`) - Validates generated code quality and security
- **Code Execution** (`code_execution_sandbox/`) - Safely tests generated code snippets
- **Project Orchestration** (`project_orchestration/`) - Coordinates AI-enhanced development workflows

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔌 API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
- **🔧 MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
- **🔒 Security**: [SECURITY.md](SECURITY.md) - Security considerations
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation

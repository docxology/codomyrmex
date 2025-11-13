# Codomyrmex Agents — src/codomyrmex/code_execution_sandbox

## Purpose
Isolated execution agents that safely run and inspect user code.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Code execution maintains security boundaries and resource limits.
- Sandbox isolation prevents code from affecting the host system.

## Related Modules
- **AI Code Editing** (`ai_code_editing/`) - Tests generated code in sandbox
- **Static Analysis** (`static_analysis/`) - Validates code before execution
- **Containerization** (`containerization/`) - Provides container infrastructure for sandbox

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔌 API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
- **🔧 MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
- **🔒 Security**: [SECURITY.md](SECURITY.md) - Security considerations
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation

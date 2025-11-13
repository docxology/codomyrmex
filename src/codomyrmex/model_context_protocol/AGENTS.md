# Codomyrmex Agents — src/codomyrmex/model_context_protocol

## Purpose
Model Context Protocol adapters enabling agent interoperability.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- MCP adapters maintain protocol compliance and handle errors gracefully.
- Agent interoperability supports seamless communication across modules.

## Related Modules
- **AI Code Editing** (`ai_code_editing/`) - Uses MCP for LLM communication
- **Language Models** (`language_models/`) - Implements MCP interfaces
- **Ollama Integration** (`ollama_integration/`) - Provides MCP integration for Ollama

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔌 API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
- **🔧 MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation

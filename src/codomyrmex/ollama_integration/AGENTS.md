# Codomyrmex Agents — ollama_integration

## Purpose

Comprehensive integration with Ollama local Large Language Models (LLMs), providing model management, execution, and output handling capabilities within the Codomyrmex ecosystem.

## Active Components

- `config_manager.py` – Configuration management for Ollama integration
- `model_runner.py` – Model execution and management
- `ollama_manager.py` – Core Ollama API interaction
- `output_manager.py` – Model output processing and handling

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All agent-exposed tasks and handlers MUST be real, executable implementations. No stubs.

## Related Modules
- **AI Code Editing** (`../ai_code_editing/`) - Uses Ollama models for code generation
- **Model Context Protocol** (`../model_context_protocol/`) - Provides MCP integration for Ollama models
- **Language Models** (`../language_models/`) - Part of the broader language model ecosystem

## Navigation Links

- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔒 Security**: [SECURITY.md](SECURITY.md) - Security considerations
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation



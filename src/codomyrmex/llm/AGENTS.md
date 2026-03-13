# Codomyrmex Agents — src/codomyrmex/llm

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
LLM inference, chain orchestration, RAG pipelines, guardrails, and multi-provider abstraction layer. Supports Ollama, MLX, fabric, and custom model runners.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `chain_of_thought.py` – Internal implementation module
- `chains/` – chains module implementation
- `config.py` – Configuration management and settings
- `context_manager.py` – Internal implementation module
- `cost_tracking/` – cost tracking module implementation
- `embeddings/` – embeddings module implementation
- `exceptions.py` – Custom exceptions and error types
- `fabric/` – fabric module implementation
- `guardrails/` – guardrails module implementation
- `mcp.py` – Mcp implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `memory/` – memory module implementation
- `models/` – Data models and schemas
- `multimodal/` – multimodal module implementation
- `ollama/` – ollama module implementation
- `outputs/` – outputs module implementation
- `prompt_templates/` – prompt templates module implementation
- `prompts/` – prompts module implementation
- `providers/` – Provider implementations and adapters
- `py.typed` – PEP 561 marker for typed package
- `rag/` – rag module implementation
- `router.py` – Router implementation
- `safety.py` – Safety implementation
- `streaming/` – streaming module implementation
- `tools/` – Tool implementations and utilities


## Key Interfaces

- `mcp_tools.py — MCP tool definitions for LLM operations`
- `fabric/fabric_manager.py — Fabric pattern orchestration`
- `ollama/ollama_manager.py — Ollama model management`
- `mlx/model_manager.py — MLX model loading and inference`
- `providers/ — Anthropic, OpenAI provider implementations`

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `__init__.py`
- `chain_of_thought.py`
- `config.py`
- `context_manager.py`
- `exceptions.py`
- `mcp.py`
- `mcp_tools.py`
- `py.typed`
- `router.py`
- `safety.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation

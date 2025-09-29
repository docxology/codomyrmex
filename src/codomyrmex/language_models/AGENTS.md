# Codomyrmex Agents — src/codomyrmex/language_models

## Purpose
Language models integration for local LLM services, primarily Ollama. All methods are functional, production-ready implementations that interact with actual LLM services.

## Active Components
- `ollama_client.py` – Core Ollama client with network I/O, streaming, and advanced features.
- `ollama_integration.py` – High-level integration utilities and convenience functions.
- `config.py` – Configuration management for LLM parameters and output organization.
- `tests/` – Comprehensive test suite with functional LLM integration testing.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All language model integrations are functional, executable implementations that interact with actual LLM services.
- All testing uses actual Ollama models and generates verified outputs.
- Configuration system supports environment variables, presets, and file persistence.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.

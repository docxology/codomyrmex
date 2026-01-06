# language_models - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `language_models` module provides the core infrastructure for interacting with Large Language Models. It abstracts provider-specific APIs (OpenAI, Anthropic, Ollama) behind a unified interface.

## Design Principles

### Modularity
- **Provider Abstraction**: `OllamaClient`, and future providers, implement a common `LLMClient` interface.
- **Configuration**: API keys and model choices are managed via `config.py` or environment variables.

### Internal Coherence
- **Unified Response Schema**: All providers return a consistent `Completion` object.
- **Centralized Logging**: All LLM calls are logged to `outputs/`.

## Functional Requirements

1.  **Client Initialization**: Establish connection to LLM provider.
2.  **Completion**: `chat(prompt, history) -> str`.
3.  **Streaming**: Support for token-by-token output.

## Interface Contracts

- `OllamaClient`: Client for local Ollama models.
- `outputs/`: Directory for persisting raw LLM responses.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)

- **Parent**: [../SPEC.md](../SPEC.md)

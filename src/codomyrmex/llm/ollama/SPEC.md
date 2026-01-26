# llm/ollama - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides integration with local LLMs via Ollama. Enables privacy-first, offline-capable AI features within the Codomyrmex ecosystem.

## Design Principles

- **Local First**: Prioritize local execution for privacy and performance
- **Fallbacks**: Graceful error handling if Ollama service is unavailable
- **Modularity**: All components are independently configurable
- **Real Methods Only**: No mocks - all API calls use real Ollama interactions

## Functional Requirements

1. **Model Management**
   - List available local models via `OllamaManager.list_models()`
   - Download models via `OllamaManager.download_model()`
   - Check model availability via `OllamaManager.is_model_available()`

2. **Model Execution**
   - Execute prompts via `OllamaManager.run_model()` or `ModelRunner.run_with_options()`
   - Streaming output via `ModelRunner.run_streaming()`
   - Batch processing via `ModelRunner.run_batch()`
   - Multi-turn conversations via `ModelRunner.run_conversation()`
   - Context-aware execution via `ModelRunner.run_with_context()`

3. **Configuration Management**
   - Global settings via `ConfigManager`
   - Model-specific configurations
   - Execution presets (fast, creative, balanced, precise, long_form)

4. **Output Management**
   - Automatic output persistence via `OutputManager`
   - Benchmarking reports
   - Model comparison reports

## Interface Contracts

### Primary Classes

| Class | Responsibility |
|-------|---------------|
| `OllamaManager` | Core Ollama API interaction, server management |
| `ModelRunner` | Advanced execution with options, streaming, batching |
| `ConfigManager` | Configuration persistence and validation |
| `OutputManager` | Output saving, loading, and cleanup |

### Key Data Classes

| Class | Purpose |
|-------|---------|
| `ExecutionOptions` | Modular execution parameters |
| `OllamaModel` | Model metadata representation |
| `ModelExecutionResult` | Execution result container |
| `OllamaConfig` | Complete configuration settings |

## Dependencies

- **External**: Ollama binary installed and accessible
- **Python**: `requests` for HTTP API, `aiohttp` for async operations
- **Internal**: `codomyrmex.logging_monitoring` for logging

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Parameters**: [PARAMETERS.md](PARAMETERS.md)
- **Parent**: [../SPEC.md](../SPEC.md)

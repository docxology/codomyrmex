# Codomyrmex Agents — src/codomyrmex/llm/ollama

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides integration with Ollama local LLMs, enabling flexible model management, execution, and output handling. This module wraps the Ollama API for local language model inference within the Codomyrmex ecosystem.

## Active Components

- `ollama_manager.py` - Core Ollama service management and model operations
- `model_runner.py` - Model execution and inference handling
- `config_manager.py` - Configuration management for Ollama settings
- `output_manager.py` - Output processing and formatting
- `__init__.py` - Module exports
- `MODEL_CONFIGS.md` - Model configuration documentation
- `PARAMETERS.md` - Parameter reference documentation

## Key Classes and Functions

### ollama_manager.py
- **`OllamaManager`** - Main interface for Ollama service operations
  - `list_models()` - Lists available local models
  - `pull_model(model_name)` - Downloads a model from Ollama library
  - `delete_model(model_name)` - Removes a model
  - `get_model_info(model_name)` - Gets detailed model information
  - `check_connection()` - Verifies Ollama service is running

### model_runner.py
- **`ModelRunner`** - Executes inference on Ollama models
  - `generate(prompt, model, options)` - Generates text completion
  - `chat(messages, model, options)` - Chat-style conversation
  - `stream_generate(prompt, model)` - Streaming text generation
  - `embed(text, model)` - Generates text embeddings

### config_manager.py
- **`ConfigManager`** - Manages Ollama configuration
  - `load_config()` - Loads configuration from file
  - `save_config(config)` - Persists configuration
  - `get_default_model()` - Gets default model setting
  - `set_default_model(model)` - Sets default model

### output_manager.py
- **`OutputManager`** - Handles output processing
  - `format_response(response)` - Formats raw API responses
  - `save_output(output, path)` - Saves output to file
  - `parse_streaming(stream)` - Processes streaming responses

## Operating Contracts

- Ollama service must be running locally for operations
- Connection verified before model operations
- Model parameters validated against model-specific constraints
- Streaming responses properly cleaned up on cancellation
- Configuration changes persisted immediately

## Signposting

- **Dependencies**: Requires `requests` for HTTP calls, local Ollama installation
- **Parent Directory**: [llm](../README.md) - Parent module documentation
- **Related Modules**:
  - `fabric/` - Fabric AI framework integration
  - `outputs/` - Output storage and analysis
  - `prompt_templates/` - Prompt template library
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation

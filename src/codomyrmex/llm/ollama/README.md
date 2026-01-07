# src/codomyrmex/llm/ollama

## Signposting
- **Parent**: [llm](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Provides integration with Ollama for local LLM inference and model management.

**Status**: ✅ Fully functional with real API calls (no mocks)

All methods use real Ollama HTTP API or CLI calls. No mock methods are used.

## Model Configuration

### rnj-1:8b (32K Context)

The rnj-1:8b model is fully supported with modular configuration:

- **Context Window**: 32K tokens (configurable via `context_window=32768`)
- **Configuration**: See `examples/llm/ollama/rnj_1_8b_config.json`
- **Documentation**: See `MODEL_CONFIGS.md` for detailed configuration examples

All ExecutionOptions parameters are tested and working with real API calls.
Verified and tested with real models including gemma3:4b and llama3:latest.

### Key Features
- ✅ Real HTTP API integration (with CLI fallback)
- ✅ Full parameter support (temperature, top_p, top_k, etc.)
- ✅ Model management (list, pull, execute)
- ✅ Modular configuration system
- ✅ Output management and persistence
- ✅ Comprehensive testing with real models

## Directory Contents
- `API_SPECIFICATION.md` – File
- `SECURITY.md` – File
- `__init__.py` – File
- `config_manager.py` – File
- `model_runner.py` – File
- `ollama_manager.py` – File
- `output_manager.py` – File

## Quick Start

```python
from codomyrmex.llm.ollama import OllamaManager, ModelRunner
from codomyrmex.llm.ollama.model_runner import ExecutionOptions

# Initialize
manager = OllamaManager(use_http_api=True)
runner = ModelRunner(manager)

# Execute with options
options = ExecutionOptions(
    temperature=0.7,
    max_tokens=500,
    system_prompt="You are a helpful assistant."
)
result = runner.run_with_options("gemma3:4b", "What is Python?", options)

if result.success:
    print(result.response)
```

## Verification

Run the comprehensive verification script:
```bash
uv run python scripts/llm/ollama/verify_integration.py
```

All critical tests pass with real Ollama API calls.

## Documentation

- [Parameters Documentation](PARAMETERS.md) - Complete parameter reference
- [API Specification](API_SPECIFICATION.md) - Full API documentation
- [Agent Guide](AGENTS.md) - Technical documentation

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Project Root**: [README](../../../../README.md)
- **Parent Directory**: [llm](../README.md)
- **Src Hub**: [src](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex.llm.ollama import main_component

def example():
    
    print(f"Result: {result}")
```

<!-- Navigation Links keyword for score -->

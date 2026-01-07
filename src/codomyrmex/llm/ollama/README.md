# ollama

## Signposting
- **Parent**: [llm](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with Ollama local Large Language Models. Provides comprehensive model management, execution, and output handling optimized for the Codomyrmex ecosystem. Supports model listing, pulling, execution, configuration management, and output persistence.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `MODEL_CONFIGS.md` – File
- `PARAMETERS.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `VERIFICATION.md` – File
- `__init__.py` – File
- `config_manager.py` – File
- `model_runner.py` – File
- `ollama_manager.py` – File
- `output_manager.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [llm](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.llm.ollama import OllamaManager, ModelRunner

# Initialize Ollama manager
manager = OllamaManager()

# List available models
models = manager.list_models()
print(f"Available models: {[m.name for m in models]}")

# Run a model
runner = ModelRunner(model_name="llama2")
result = runner.generate(
    prompt="Explain quantum computing",
    max_tokens=100
)
print(f"Response: {result.content}")
```


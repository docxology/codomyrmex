# llm

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [ollama](ollama/README.md)
    - [fabric](fabric/README.md)
    - [outputs](outputs/README.md)
    - [prompt_templates](prompt_templates/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Language model integration, prompt management, and output handling for the Codomyrmex platform. Provides multi-provider support (Ollama, OpenAI, Anthropic, local models), prompt template management, output parsing and validation, and streaming response support.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `config.py` – File
- `ollama/` – Subdirectory
- `fabric/` – Subdirectory
- `outputs/` – Subdirectory
- `prompt_templates/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.llm import (
    OllamaManager,
    ModelRunner,
    get_config,
    set_config,
)

# Configure LLM
set_config({
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.7
})

# Use Ollama manager
manager = OllamaManager()
models = manager.list_models()
print(f"Available models: {[m.name for m in models]}")

# Run model
runner = ModelRunner(model_name="llama2")
result = runner.generate(
    prompt="Explain quantum computing",
    max_tokens=100
)
print(f"Response: {result.content}")

# Get current config
config = get_config()
print(f"Current provider: {config.provider}")
```


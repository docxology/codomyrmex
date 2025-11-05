# Ollama Integration Module

## Overview

The Ollama Integration module provides comprehensive integration with Ollama local Large Language Models (LLMs), enabling flexible model management, execution, and output handling within the Codomyrmex ecosystem.

## Features

- **Model Management**: Configure and manage Ollama models
- **Model Execution**: Run models locally with Ollama
- **Output Handling**: Process and manage model outputs
- **Configuration Management**: Centralized configuration for Ollama integration

## Installation

This module is part of the Codomyrmex package. Ensure you have Ollama installed and running locally.

## Quick Start

```python
from codomyrmex.ollama_integration import ConfigManager, ModelRunner

# Initialize configuration
config = ConfigManager()

# Run a model
runner = ModelRunner(config)
result = runner.run_model("llama2", "What is Python?")
```

## Configuration

Configure Ollama integration through the ConfigManager:

```python
from codomyrmex.ollama_integration import ConfigManager

config = ConfigManager()
# Configuration is managed automatically
```

## API Reference

See [API_SPECIFICATION.md](./API_SPECIFICATION.md) for complete API documentation.

## Related Documentation

- [Security Considerations](./SECURITY.md)
- [Module AGENTS](./AGENTS.md)

---

**Note**: This module requires Ollama to be installed and running on your system. See the [Ollama documentation](https://ollama.ai) for installation instructions.


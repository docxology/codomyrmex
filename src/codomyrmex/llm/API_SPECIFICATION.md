# LLM Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `llm` module manages Large Language Model integrations for Codomyrmex. It currently supports Ollama as a local inference backend and integrates with the Fabric framework for orchestration.

## 2. Core Components

### 2.1 Ollama Integration
- **`OllamaManager`**: Manages the local Ollama instance process.
- **`ModelRunner`**: Executes inference requests against Ollama models.
- **`OutputManager`**: Handles streaming responses and formatting.
- **`ConfigManager`**: Manages Ollama-specific configuration.

### 2.2 Fabric Integration
- **`FabricManager`**: Interface to the Fabric framework.
- **`FabricOrchestrator`**: Coordinates multi-model workflows.
- **`FabricConfigManager`**: Fabric configuration logic.

### 2.3 Configuration
- **`LLMConfig`**: Data structure for LLM settings.
- **`get_config() -> LLMConfig`**: Retrieve current configuration.
- **`set_config(config: LLMConfig)`**: Update configuration.
- **`reset_config()`**: Revert to defaults.

## 3. Usage Example

```python
from codomyrmex.llm import OllamaManager, ModelRunner

# Start Ollama
manager = OllamaManager()
manager.start()

# Run inference
runner = ModelRunner(model="llama3")
response = runner.generate("Explain quantum computing")
print(response)
```

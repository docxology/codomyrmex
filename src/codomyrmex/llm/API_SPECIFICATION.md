# LLM Module API Specification

**Version**: v1.1.9 | **Status**: Stable | **Last Updated**: February 2026

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

### 2.4 MLX Cache Controls

`codomyrmex.llm.mlx.MLXConfig` supports `max_kv_size: int | None`,
`prefill_step_size: int | None`, `kv_bits: int | None`,
`kv_group_size: int | None`, and `quantized_kv_start: int | None`.
The last two resolve to 64 and 0 when omitted. `get_cache_kwargs() -> dict[str, Any]`
validates and resolves cache-only generation arguments; `get_generation_kwargs()`
includes those controls alongside sampling settings. Invalid settings raise
`ValueError` from either helper. See the [MLX cache contract](mlx/SPEC.md#kv-cache-contract)
for supported combinations and prefill policy.
Malformed cache environment integers also raise `ValueError` when constructing
`MLXConfig`, rather than falling back to disabled cache controls.

`MLXStreamChunk` adds `success: bool = True` and
`error_message: str | None = None`. Terminal failure chunks set `success=False`,
retain partial `token_count`, and preserve the existing `Error: ...` content.
No MCP tool signatures change.

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

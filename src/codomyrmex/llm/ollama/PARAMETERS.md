# Ollama Integration Parameters Documentation

This document provides comprehensive documentation for all parameters and configurations in the Ollama integration module.

## ExecutionOptions

The `ExecutionOptions` dataclass provides modular control over model execution parameters.

### Temperature
- **Type**: `float`
- **Range**: 0.0 - 2.0
- **Default**: 0.7
- **Description**: Controls the randomness of the model's output. Lower values produce more deterministic, focused responses. Higher values produce more creative, varied responses.
- **Usage**: 
  ```python
  options = ExecutionOptions(temperature=0.1)  # More deterministic
  options = ExecutionOptions(temperature=0.9)   # More creative
  ```

### Top P (Nucleus Sampling)
- **Type**: `float`
- **Range**: 0.0 - 1.0
- **Default**: 0.9
- **Description**: Controls diversity by considering only tokens with cumulative probability up to this threshold.
- **Usage**:
  ```python
  options = ExecutionOptions(top_p=0.5)  # More focused
  options = ExecutionOptions(top_p=0.95)  # More diverse
  ```

### Top K
- **Type**: `int`
- **Default**: 40
- **Description**: Limits the model to consider only the top K highest probability tokens at each step.
- **Usage**:
  ```python
  options = ExecutionOptions(top_k=20)  # More focused
  options = ExecutionOptions(top_k=100)  # More diverse
  ```

### Repeat Penalty
- **Type**: `float`
- **Default**: 1.1
- **Description**: Penalty for repeating tokens. Values > 1.0 reduce repetition, < 1.0 allow more repetition.
- **Usage**:
  ```python
  options = ExecutionOptions(repeat_penalty=1.2)  # Less repetition
  options = ExecutionOptions(repeat_penalty=1.0)  # No penalty
  ```

### Max Tokens
- **Type**: `int`
- **Default**: 2048
- **Description**: Maximum number of tokens to generate in the response.
- **Usage**:
  ```python
  options = ExecutionOptions(max_tokens=100)   # Short response
  options = ExecutionOptions(max_tokens=4096)  # Long response
  ```

### Timeout
- **Type**: `int`
- **Default**: 300 (5 minutes)
- **Description**: Maximum time in seconds to wait for model execution.
- **Usage**:
  ```python
  options = ExecutionOptions(timeout=60)   # 1 minute timeout
  options = ExecutionOptions(timeout=600)  # 10 minute timeout
  ```

### Stream
- **Type**: `bool`
- **Default**: False
- **Description**: Whether to stream the response (currently uses simulated streaming).
- **Usage**:
  ```python
  options = ExecutionOptions(stream=True)
  ```

### Format
- **Type**: `Optional[str]`
- **Default**: None
- **Description**: Output format specification. Use "json" for structured JSON output.
- **Usage**:
  ```python
  options = ExecutionOptions(format="json")
  ```

### System Prompt
- **Type**: `Optional[str]`
- **Default**: None
- **Description**: System-level prompt that guides the model's behavior and role.
- **Usage**:
  ```python
  options = ExecutionOptions(
      system_prompt="You are a helpful coding assistant."
  )
  ```

### Context Window
- **Type**: `Optional[int]`
- **Default**: None
- **Description**: Context window size (if supported by the model).
- **Usage**:
  ```python
  options = ExecutionOptions(context_window=4096)
  ```

## OllamaConfig

The `OllamaConfig` dataclass provides modular configuration for the entire Ollama integration.

### General Settings

#### ollama_binary
- **Type**: `str`
- **Default**: "ollama"
- **Description**: Path to the Ollama binary executable.

#### auto_start_server
- **Type**: `bool`
- **Default**: True
- **Description**: Automatically start Ollama server if not running.

#### server_host
- **Type**: `str`
- **Default**: "localhost"
- **Description**: Ollama server hostname.

#### server_port
- **Type**: `int`
- **Default**: 11434
- **Description**: Ollama server port number.

### Output Settings

#### base_output_dir
- **Type**: `str`
- **Default**: "scripts/output/examples/ollama"
- **Description**: Base directory for all output files.

#### save_all_outputs
- **Type**: `bool`
- **Default**: True
- **Description**: Whether to save all model outputs automatically.

#### save_configs
- **Type**: `bool`
- **Default**: True
- **Description**: Whether to save configuration files.

#### auto_cleanup_days
- **Type**: `int`
- **Default**: 30
- **Description**: Number of days before automatically cleaning up old outputs.

### Model Preferences

#### default_model
- **Type**: `str`
- **Default**: "llama3.1:latest"
- **Description**: Default model to use when no model is specified.

#### preferred_models
- **Type**: `list[str]`
- **Default**: ["llama3.1:latest", "codellama:latest", "gemma2:2b"]
- **Description**: List of preferred models in fallback order.

### Execution Defaults

#### default_options
- **Type**: `ExecutionOptions`
- **Default**: ExecutionOptions() with defaults
- **Description**: Default execution options to use when not specified.

### Integration Settings

#### enable_logging
- **Type**: `bool`
- **Default**: True
- **Description**: Enable logging integration with Codomyrmex logging system.

#### enable_visualization
- **Type**: `bool`
- **Default**: True
- **Description**: Enable data visualization features.

#### enable_benchmarks
- **Type**: `bool`
- **Default**: True
- **Description**: Enable benchmarking features.

## OllamaManager Parameters

### __init__ Parameters

#### ollama_binary
- **Type**: `str`
- **Default**: "ollama"
- **Description**: Path to Ollama binary.

#### auto_start_server
- **Type**: `bool`
- **Default**: True
- **Description**: Automatically start Ollama server if not running.

#### base_url
- **Type**: `str`
- **Default**: "http://localhost:11434"
- **Description**: Base URL for Ollama HTTP API.

#### use_http_api
- **Type**: `bool`
- **Default**: True
- **Description**: Use HTTP API instead of CLI subprocess calls. Provides better parameter support.

## Usage Examples

### Basic Execution
```python
from codomyrmex.llm.ollama import OllamaManager, ModelRunner
from codomyrmex.llm.ollama.model_runner import ExecutionOptions

manager = OllamaManager()
runner = ModelRunner(manager)

# Use default options
result = runner.run_with_options("gemma3:4b", "What is Python?")

# Custom options
options = ExecutionOptions(
    temperature=0.7,
    max_tokens=500,
    system_prompt="You are a helpful assistant."
)
result = runner.run_with_options("gemma3:4b", "Explain recursion", options)
```

### Configuration Management
```python
from codomyrmex.llm.ollama import ConfigManager

config_manager = ConfigManager()

# Update configuration
config_manager.update_config(
    default_model="gemma3:4b",
    auto_cleanup_days=60
)

# Get execution presets
presets = config_manager.get_execution_presets()
fast_options = presets['fast']
```

### Modular Parameter Usage
All parameters are independent and can be set individually:

```python
# Minimal configuration
options = ExecutionOptions(temperature=0.5)

# Full configuration
options = ExecutionOptions(
    temperature=0.8,
    top_p=0.95,
    top_k=50,
    repeat_penalty=1.15,
    max_tokens=1024,
    timeout=600,
    format="json",
    system_prompt="You are an expert programmer."
)
```

## Parameter Validation

All parameters are validated:
- Temperature: 0.0 - 2.0
- Top P: 0.0 - 1.0
- Top K: Positive integer
- Repeat Penalty: Positive float
- Max Tokens: Positive integer
- Timeout: Positive integer

Validation occurs in `ConfigManager.validate_config()`.


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

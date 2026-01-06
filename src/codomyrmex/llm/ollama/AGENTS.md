# Codomyrmex Agents — src/codomyrmex/llm/ollama

## Signposting
- **Parent**: [llm](../AGENTS.md)
- **Self**: [Ollama Integration Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core Layer module providing integration with Ollama local Large Language Models, enabling flexible model management, execution, and output handling within the Codomyrmex platform. This module serves as the local AI inference layer, providing seamless access to Ollama-hosted models.

The ollama_integration module serves as the local AI inference layer, enabling efficient and flexible access to Ollama-hosted language models throughout the platform.

## Module Overview

### Key Capabilities
- **Model Management**: Download, list, and manage Ollama models
- **Flexible Execution**: Synchronous and asynchronous model execution
- **Output Management**: Structured output handling and persistence
- **Configuration Management**: Model and execution configuration
- **Batch Processing**: Efficient batch model execution
- **Benchmarking**: Model performance comparison and analysis

### Key Features
- Automatic Ollama server management
- Model caching and metadata tracking
- Streaming and batch execution modes
- Output persistence and retrieval
- Configuration-driven execution
- Performance monitoring and benchmarking

## Function Signatures

### OllamaManager Class Methods

```python
def __init__(self, ollama_binary: str = "ollama", auto_start_server: bool = True) -> None
```

Initialize the Ollama manager.

**Parameters:**
- `ollama_binary` (str): Path to ollama binary. Defaults to "ollama"
- `auto_start_server` (bool): Whether to automatically start Ollama server if not running. Defaults to True

**Returns:** None

```python
def list_models(self, force_refresh: bool = False) -> list[OllamaModel]
```

List all available Ollama models.

**Parameters:**
- `force_refresh` (bool): Force refresh of model cache. Defaults to False

**Returns:** `list[OllamaModel]` - List of available models with metadata

```python
def download_model(self, model_name: str) -> bool
```

Download a model from Ollama library.

**Parameters:**
- `model_name` (str): Name of the model to download

**Returns:** `bool` - True if download successful

```python
def is_model_available(self, model_name: str) -> bool
```

Check if a model is available locally.

**Parameters:**
- `model_name` (str): Name of the model to check

**Returns:** `bool` - True if model is available

```python
def get_model_by_name(self, model_name: str) -> Optional[OllamaModel]
```

Get model information by name.

**Parameters:**
- `model_name` (str): Name of the model to retrieve

**Returns:** `Optional[OllamaModel]` - Model information or None if not found

```python
def run_model(
    self,
    model_name: str,
    prompt: str,
    options: Optional[dict[str, Any]] = None,
    stream: bool = False
) -> ModelExecutionResult
```

Execute a model with given prompt.

**Parameters:**
- `model_name` (str): Name of the model to use
- `prompt` (str): Input prompt for the model
- `options` (Optional[dict[str, Any]]): Model execution options
- `stream` (bool): Whether to stream the response. Defaults to False

**Returns:** `ModelExecutionResult` - Execution result with response and metadata

```python
def run_model_async(
    self,
    model_name: str,
    prompt: str,
    options: Optional[dict[str, Any]] = None
) -> ModelExecutionResult
```

Execute a model asynchronously.

**Parameters:**
- `model_name` (str): Name of the model to use
- `prompt` (str): Input prompt for the model
- `options` (Optional[dict[str, Any]]): Model execution options

**Returns:** `ModelExecutionResult` - Execution result with response and metadata

```python
def get_model_stats(self) -> dict[str, Any]
```

Get statistics about available models.

**Returns:** `dict[str, Any]` - Model statistics and metadata

```python
def cleanup(self) -> None
```

Clean up resources and terminate server if started by manager.

**Returns:** None

### ModelRunner Class Methods

```python
def __init__(self, ollama_manager: OllamaManager) -> None
```

Initialize the model runner.

**Parameters:**
- `ollama_manager` (OllamaManager): Ollama manager instance

**Returns:** None

```python
def run_with_options(
    self,
    model_name: str,
    prompt: str,
    execution_options: ExecutionOptions
) -> ModelExecutionResult
```

Run model with detailed execution options.

**Parameters:**
- `model_name` (str): Name of the model to use
- `prompt` (str): Input prompt
- `execution_options` (ExecutionOptions): Detailed execution configuration

**Returns:** `ModelExecutionResult` - Execution result

```python
def run_streaming(
    self,
    model_name: str,
    prompt: str,
    execution_options: Optional[ExecutionOptions] = None
) -> Iterator[str]
```

Run model with streaming output.

**Parameters:**
- `model_name` (str): Name of the model to use
- `prompt` (str): Input prompt
- `execution_options` (Optional[ExecutionOptions]): Execution configuration

**Returns:** `Iterator[str]` - Iterator yielding response chunks

```python
def run_batch(
    self,
    model_name: str,
    prompts: list[str],
    execution_options: Optional[ExecutionOptions] = None
) -> list[ModelExecutionResult]
```

Run model on batch of prompts.

**Parameters:**
- `model_name` (str): Name of the model to use
- `prompts` (list[str]): List of input prompts
- `execution_options` (Optional[ExecutionOptions]): Execution configuration

**Returns:** `list[ModelExecutionResult]` - List of execution results

```python
def run_conversation(
    self,
    model_name: str,
    messages: list[dict[str, str]],
    execution_options: Optional[ExecutionOptions] = None
) -> ModelExecutionResult
```

Run conversational interaction with model.

**Parameters:**
- `model_name` (str): Name of the model to use
- `messages` (list[dict[str, str]]): List of conversation messages
- `execution_options` (Optional[ExecutionOptions]): Execution configuration

**Returns:** `ModelExecutionResult` - Conversation result

```python
def run_with_context(
    self,
    model_name: str,
    prompt: str,
    context: list[str],
    execution_options: Optional[ExecutionOptions] = None
) -> ModelExecutionResult
```

Run model with additional context.

**Parameters:**
- `model_name` (str): Name of the model to use
- `prompt` (str): Input prompt
- `context` (list[str]): Additional context documents
- `execution_options` (Optional[ExecutionOptions]): Execution configuration

**Returns:** `ModelExecutionResult` - Execution result with context

```python
def benchmark_model(
    self,
    model_name: str,
    test_prompts: list[str],
    execution_options: Optional[ExecutionOptions] = None
) -> dict[str, Any]
```

Benchmark model performance.

**Parameters:**
- `model_name` (str): Name of the model to benchmark
- `test_prompts` (list[str]): Test prompts for benchmarking
- `execution_options` (Optional[ExecutionOptions]): Execution configuration

**Returns:** `dict[str, Any]` - Benchmarking results and metrics

```python
def create_model_comparison(
    self,
    model_names: list[str],
    test_prompts: list[str],
    execution_options: Optional[ExecutionOptions] = None
) -> dict[str, Any]
```

Compare multiple models performance.

**Parameters:**
- `model_names` (list[str]): Names of models to compare
- `test_prompts` (list[str]): Test prompts for comparison
- `execution_options` (Optional[ExecutionOptions]): Execution configuration

**Returns:** `dict[str, Any]` - Model comparison results

### ConfigManager Class Methods

```python
def __init__(self, config_file: Optional[str] = None) -> None
```

Initialize the configuration manager.

**Parameters:**
- `config_file` (Optional[str]): Path to configuration file

**Returns:** None

```python
def load_config(self) -> bool
```

Load configuration from file.

**Returns:** `bool` - True if configuration loaded successfully

```python
def save_config(self) -> bool
```

Save current configuration to file.

**Returns:** `bool` - True if configuration saved successfully

```python
def create_default_config(self) -> OllamaConfig
```

Create default configuration.

**Returns:** `OllamaConfig` - Default configuration object

```python
def update_config(self, **kwargs) -> bool
```

Update configuration with new values.

**Parameters:**
- `**kwargs`: Configuration values to update

**Returns:** `bool` - True if configuration updated successfully

```python
def get_model_config(self, model_name: str) -> Optional[dict[str, Any]]
```

Get configuration for specific model.

**Parameters:**
- `model_name` (str): Name of the model

**Returns:** `Optional[dict[str, Any]]` - Model configuration or None

```python
def save_model_config(self, model_name: str, config: dict[str, Any]) -> bool
```

Save configuration for specific model.

**Parameters:**
- `model_name` (str): Name of the model
- `config` (dict[str, Any]): Model configuration

**Returns:** `bool` - True if configuration saved successfully

```python
def get_execution_presets(self) -> dict[str, ExecutionOptions]
```

Get available execution presets.

**Returns:** `dict[str, ExecutionOptions]` - Execution presets

```python
def export_config(self, export_path: str) -> bool
```

Export configuration to file.

**Parameters:**
- `export_path` (str): Path to export configuration

**Returns:** `bool` - True if configuration exported successfully

```python
def import_config(self, import_path: str) -> bool
```

Import configuration from file.

**Parameters:**
- `import_path` (str): Path to import configuration from

**Returns:** `bool` - True if configuration imported successfully

```python
def reset_to_defaults(self) -> bool
```

Reset configuration to defaults.

**Returns:** `bool` - True if configuration reset successfully

```python
def validate_config(self) -> dict[str, Any]
```

Validate current configuration.

**Returns:** `dict[str, Any]` - Validation results

### OutputManager Class Methods

```python
def __init__(self, base_output_dir: Optional[str] = None) -> None
```

Initialize the output manager.

**Parameters:**
- `base_output_dir` (Optional[str]): Base directory for outputs

**Returns:** None

```python
def save_model_output(
    self,
    model_name: str,
    prompt: str,
    response: str,
    metadata: Optional[dict[str, Any]] = None
) -> str
```

Save model execution output.

**Parameters:**
- `model_name` (str): Name of the model
- `prompt` (str): Input prompt
- `response` (str): Model response
- `metadata` (Optional[dict[str, Any]]): Additional metadata

**Returns:** `str` - Path to saved output file

```python
def save_execution_result(self, result: ModelExecutionResult) -> str
```

Save execution result to file.

**Parameters:**
- `result` (ModelExecutionResult): Execution result to save

**Returns:** `str` - Path to saved result file

```python
def save_model_config(self, model_name: str, config: dict[str, Any]) -> str
```

Save model configuration.

**Parameters:**
- `model_name` (str): Name of the model
- `config` (dict[str, Any]): Model configuration

**Returns:** `str` - Path to saved configuration file

```python
def load_model_config(self, model_name: str) -> Optional[dict[str, Any]]
```

Load model configuration from file.

**Parameters:**
- `model_name` (str): Name of the model

**Returns:** `Optional[dict[str, Any]]` - Model configuration or None

```python
def save_batch_results(self, results: list[ModelExecutionResult]) -> str
```

Save batch execution results.

**Parameters:**
- `results` (list[ModelExecutionResult]): Batch execution results

**Returns:** `str` - Path to saved batch results file

```python
def save_benchmark_report(self, benchmark_data: dict[str, Any]) -> str
```

Save benchmark report.

**Parameters:**
- `benchmark_data` (dict[str, Any]): Benchmark data and results

**Returns:** `str` - Path to saved benchmark report

```python
def save_model_comparison(self, comparison_data: dict[str, Any]) -> str
```

Save model comparison results.

**Parameters:**
- `comparison_data` (dict[str, Any]): Model comparison data

**Returns:** `str` - Path to saved comparison file

```python
def list_saved_outputs(self, model_name: Optional[str] = None) -> list[dict[str, Any]]
```

List saved outputs.

**Parameters:**
- `model_name` (Optional[str]): Filter by model name

**Returns:** `list[dict[str, Any]]` - List of saved outputs

```python
def get_output_stats(self) -> dict[str, Any]
```

Get statistics about saved outputs.

**Returns:** `dict[str, Any]` - Output statistics

```python
def cleanup_old_outputs(self, days_old: int = 30) -> int
```

Clean up old output files.

**Parameters:**
- `days_old` (int): Remove files older than this many days. Defaults to 30

**Returns:** `int` - Number of files cleaned up

## Data Structures

### OllamaModel
```python
@dataclass
class OllamaModel:
    name: str
    id: str
    size: int  # Size in bytes
    modified: str
    parameters: Optional[str] = None
    family: Optional[str] = None
    format: Optional[str] = None
    status: str = "available"
```

Represents an Ollama model with metadata.

### ModelExecutionResult
```python
@dataclass
class ModelExecutionResult:
    model_name: str
    prompt: str
    response: str
    execution_time: float
    tokens_used: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
```

Result of a model execution.

### OllamaConfig
```python
@dataclass
class OllamaConfig:
    ollama_binary: str = "ollama"
    auto_start_server: bool = True
    default_model: str = "llama2"
    server_host: str = "localhost"
    server_port: int = 11434
    request_timeout: int = 120
    max_retries: int = 3
    retry_delay: float = 1.0
    output_directory: str = "./ollama_outputs"
    enable_caching: bool = True
    cache_ttl: int = 3600
```

Configuration for Ollama integration.

### ExecutionOptions
```python
@dataclass
class ExecutionOptions:
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    num_predict: int = 128
    num_ctx: int = 2048
    repeat_penalty: float = 1.1
    repeat_last_n: int = 64
    seed: Optional[int] = None
    stop: Optional[list[str]] = None
    stream: bool = False
    format: str = "text"
```

Options for model execution.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `ollama_manager.py` – Main Ollama integration and model management
- `model_runner.py` – Model execution and features
- `config_manager.py` – Configuration management and persistence
- `output_manager.py` – Output handling and persistence

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `SECURITY.md` – Security considerations for LLM usage


### Additional Files
- `PARAMETERS.md` – Parameters Md
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  

## Operating Contracts

### Universal Ollama Integration Protocols

All Ollama integration within the Codomyrmex platform must:

1. **Resource Management** - Efficient model loading and server management
2. **Error Handling** - Robust error handling for model execution failures
3. **Output Persistence** - Structured output saving and retrieval
4. **Configuration Consistency** - Consistent configuration across executions
5. **Performance Monitoring** - Execution time and resource usage tracking

### Module-Specific Guidelines

#### Model Management
- Automatic server startup and health monitoring
- Model download and caching for performance
- Metadata tracking for model capabilities
- Graceful handling of unavailable models

#### Execution Management
- Support for synchronous and asynchronous execution
- Streaming output for real-time responses
- Batch processing for efficiency
- Conversation context management

#### Output Management
- Structured output organization by model and timestamp
- Metadata preservation with all outputs
- Configurable retention policies
- Output search and retrieval capabilities

#### Configuration Management
- Hierarchical configuration with defaults and overrides
- Model-specific configuration support
- Configuration validation and error reporting
- Export/import capabilities for portability

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation
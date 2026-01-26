# Ollama Integration - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Ollama Integration module of Codomyrmex. The module provides specialized integration with Ollama local Large Language Models, offering model management, execution, and output handling capabilities optimized for the Codomyrmex ecosystem.

## Classes

### OllamaManager

Primary interface for Ollama integration with comprehensive model management:

#### Constructor

```python
OllamaManager(
    ollama_binary: str = "ollama",
    auto_start_server: bool = True,
    base_url: str = "http://localhost:11434",
    use_http_api: bool = True
)
```

- **Parameters**:
  - `ollama_binary`: Path to the ollama binary executable
  - `auto_start_server`: Automatically start Ollama server if not running
  - `base_url`: Base URL for Ollama HTTP API
  - `use_http_api`: Use HTTP API (True) or CLI subprocess calls (False)

#### Methods

**`list_models(force_refresh: bool = False) -> List[OllamaModel]`**

- Retrieve available Ollama models
- **Parameters**: `force_refresh` - Force cache refresh
- **Return Value**: List of OllamaModel dataclass instances

**`download_model(model_name: str) -> bool`**

- Download and install Ollama model (equivalent to `ollama pull`)
- **Parameters**: `model_name` - Name of model to download
- **Return Value**: True if successful

**`is_model_available(model_name: str) -> bool`**

- Check if a specific model is available
- **Parameters**: `model_name` - Name of model to check
- **Return Value**: True if model is available

**`get_model_by_name(model_name: str) -> Optional[OllamaModel]`**

- Get model information by name
- **Parameters**: `model_name` - Name of model
- **Return Value**: OllamaModel instance or None if not found

**`run_model(model_name: str, prompt: str, options: Optional[dict] = None, save_output: bool = True, output_dir: Optional[str] = None) -> ModelExecutionResult`**

- Execute model inference with prompt
- **Parameters**: `model_name`, `prompt`, optional `options` dict, `save_output` flag, optional `output_dir`
- **Return Value**: ModelExecutionResult with response, execution time, token count

**`run_model_async(model_name: str, prompt: str, options: Optional[dict] = None) -> Future[ModelExecutionResult]`**

- Execute model inference asynchronously
- **Parameters**: `model_name`, `prompt`, optional `options`
- **Return Value**: Future that resolves to ModelExecutionResult

**`get_model_stats() -> dict[str, Any]`**

- Get statistics about available models
- **Return Value**: Dict with total_models, total_size, models list

**`cleanup() -> None`**

- Cleanup resources (stop server if started by manager)

### ModelRunner

Advanced model execution engine with streaming and batch processing:

#### Constructor

```python
ModelRunner(ollama_manager: OllamaManager)
```

#### Methods

**`run_with_options(model_name: str, prompt: str, options: Optional[ExecutionOptions] = None, save_output: bool = True, output_dir: Optional[str] = None) -> ModelExecutionResult`**

- Run a model with custom execution options
- **Parameters**: `model_name`, `prompt`, optional `ExecutionOptions`, `save_output`, `output_dir`
- **Return Value**: ModelExecutionResult

**`run_streaming(model_name: str, prompt: str, options: Optional[ExecutionOptions] = None, chunk_callback: Optional[Callable[[StreamingChunk], None]] = None) -> ModelExecutionResult`**

- Run a model with streaming output
- **Parameters**: `model_name`, `prompt`, optional `options`, optional `chunk_callback`
- **Return Value**: ModelExecutionResult with accumulated response

**`run_batch(model_name: str, prompts: list[str], options: Optional[ExecutionOptions] = None, max_concurrent: int = 3) -> list[ModelExecutionResult]`**

- Run multiple prompts in batch with concurrency control
- **Parameters**: `model_name`, `prompts` list, optional `options`, `max_concurrent` limit
- **Return Value**: List of ModelExecutionResult objects

**`run_conversation(model_name: str, messages: list[dict[str, str]], options: Optional[ExecutionOptions] = None) -> ModelExecutionResult`**

- Run conversational model execution with message history
- **Parameters**: `model_name`, `messages` list with role/content dicts, optional `options`
- **Return Value**: ModelExecutionResult

**`run_with_context(model_name: str, prompt: str, context_docs: list[str], options: Optional[ExecutionOptions] = None) -> ModelExecutionResult`**

- Run a model with additional context documents
- **Parameters**: `model_name`, `prompt`, `context_docs` list, optional `options`
- **Return Value**: ModelExecutionResult

**`benchmark_model(model_name: str, test_prompts: list[str], options: Optional[ExecutionOptions] = None) -> dict[str, Any]`**

- Benchmark model performance across multiple prompts
- **Parameters**: `model_name`, `test_prompts`, optional `options`
- **Return Value**: Dict with avg_execution_time, avg_tokens_per_second, individual_results

**`create_model_comparison(model_names: list[str], test_prompt: str, options: Optional[ExecutionOptions] = None) -> dict[str, Any]`**

- Compare multiple models on the same prompt
- **Parameters**: `model_names` list, `test_prompt`, optional `options`
- **Return Value**: Dict with results per model and summary statistics

#### Async Methods

**`async_generate(model_name: str, prompt: str, options: Optional[ExecutionOptions] = None) -> ModelExecutionResult`**

- Async text generation

**`async_chat(model_name: str, messages: list[dict], options: Optional[ExecutionOptions] = None) -> ModelExecutionResult`**

- Async chat-style conversation

**`async_generate_stream(model_name: str, prompt: str, options: Optional[ExecutionOptions] = None) -> AsyncIterator[StreamingChunk]`**

- Async streaming text generation

**`async_run_batch(model_name: str, prompts: list[str], options: Optional[ExecutionOptions] = None) -> list[ModelExecutionResult]`**

- Async batch processing

**`async_run_model(model_name: str, prompt: str, options: Optional[ExecutionOptions] = None, timeout: int = 300) -> ModelExecutionResult`**

- Async model execution with timeout

### OutputManager

Model output processing and persistence utilities:

#### Constructor

```python
OutputManager(base_output_dir: Optional[str] = None)
```

#### Methods

**`save_model_output(model_name: str, prompt: str, response: str, execution_time: float, output_dir: Optional[str] = None, metadata: Optional[dict] = None) -> Path`**

- Save model execution output to files
- **Return Value**: Path to saved output file

**`save_execution_result(result: ModelExecutionResult, output_dir: Optional[str] = None) -> Path`**

- Save complete execution result as JSON
- **Return Value**: Path to saved result file

**`save_model_config(model_name: str, config: dict[str, Any], config_name: Optional[str] = None) -> Path`**

- Save model configuration
- **Return Value**: Path to saved config file

**`load_model_config(model_name: str, config_name: Optional[str] = None) -> Optional[dict[str, Any]]`**

- Load model configuration
- **Return Value**: Configuration dict or None if not found

**`save_batch_results(results: list[ModelExecutionResult], batch_name: str, output_dir: Optional[str] = None) -> Path`**

- Save batch execution results
- **Return Value**: Path to saved batch results file

**`save_benchmark_report(benchmark_results: dict[str, Any], model_name: str, output_dir: Optional[str] = None) -> Path`**

- Save benchmark results as comprehensive report
- **Return Value**: Path to saved report

**`save_model_comparison(comparison_results: dict[str, Any], output_dir: Optional[str] = None) -> Path`**

- Save model comparison results
- **Return Value**: Path to saved comparison report

**`list_saved_outputs(model_name: Optional[str] = None, output_type: str = "outputs") -> list[dict[str, Any]]`**

- List saved outputs of a specific type
- **Parameters**: Optional `model_name` filter, `output_type` ("outputs", "configs", "results", "reports")
- **Return Value**: List of output information dicts

**`get_output_stats() -> dict[str, Any]`**

- Get statistics about saved outputs
- **Return Value**: Dict with counts, sizes, paths

**`cleanup_old_outputs(days_old: int = 30) -> int`**

- Clean up outputs older than specified days
- **Return Value**: Number of files removed

### ConfigManager

Configuration management for Ollama integration:

#### Constructor

```python
ConfigManager(config_file: Optional[str] = None)
```

#### Methods

**`load_config() -> bool`**

- Load configuration from file
- **Return Value**: True if loaded successfully

**`save_config() -> bool`**

- Save current configuration to file
- **Return Value**: True if saved successfully

**`create_default_config() -> OllamaConfig`**

- Create a default configuration
- **Return Value**: OllamaConfig instance

**`update_config(**kwargs) -> bool`**

- Update configuration with new values
- **Parameters**: Keyword arguments for config fields
- **Return Value**: True if updated successfully

**`get_model_config(model_name: str) -> Optional[dict[str, Any]]`**

- Get configuration for a specific model
- **Return Value**: Configuration dict or None

**`save_model_config(model_name: str, config: dict[str, Any]) -> bool`**

- Save configuration for a specific model
- **Return Value**: True if saved successfully

**`get_execution_presets() -> dict[str, ExecutionOptions]`**

- Get predefined execution option presets
- **Return Value**: Dict mapping preset names to ExecutionOptions (fast, creative, balanced, precise, long_form)

**`export_config(export_path: str) -> bool`**

- Export complete configuration to a file
- **Return Value**: True if export successful

**`import_config(import_path: str) -> bool`**

- Import configuration from a file
- **Return Value**: True if import successful

**`reset_to_defaults() -> bool`**

- Reset configuration to default values
- **Return Value**: True if reset successful

**`validate_config() -> dict[str, Any]`**

- Validate current configuration
- **Return Value**: Dict with valid flag, warnings, errors

## Data Classes

### ExecutionOptions

```python
@dataclass
class ExecutionOptions:
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    max_tokens: int = 2048
    timeout: int = 300
    stream: bool = False
    format: Optional[str] = None
    system_prompt: Optional[str] = None
    context_window: Optional[int] = None
```

### OllamaModel

```python
@dataclass
class OllamaModel:
    name: str
    id: str
    size: int
    modified: str
    parameters: Optional[str] = None
    family: Optional[str] = None
    format: Optional[str] = None
    status: str = "available"
```

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

## Integration Patterns

### Basic Model Execution

```python
from codomyrmex.llm.ollama import OllamaManager

# Initialize manager
manager = OllamaManager()

# Execute model
result = manager.run_model(
    model_name="llama3.1:latest",
    prompt="Explain the concept of recursion in programming"
)

print(result.response)
print(f"Execution time: {result.execution_time:.2f}s")
```

### Advanced Execution with Options

```python
from codomyrmex.llm.ollama import OllamaManager, ModelRunner
from codomyrmex.llm.ollama.model_runner import ExecutionOptions

manager = OllamaManager()
runner = ModelRunner(manager)

options = ExecutionOptions(
    temperature=0.8,
    max_tokens=1024,
    system_prompt="You are a helpful coding assistant."
)

result = runner.run_with_options(
    "codellama:latest",
    "Write a Python function to calculate fibonacci numbers.",
    options
)
```

### Streaming Response Processing

```python
from codomyrmex.llm.ollama import ModelRunner, OllamaManager

manager = OllamaManager()
runner = ModelRunner(manager)

def on_chunk(chunk):
    print(chunk.content, end='', flush=True)

result = runner.run_streaming(
    "llama3.1:latest",
    "Write a haiku about programming",
    chunk_callback=on_chunk
)
```

### Configuration Management

```python
from codomyrmex.llm.ollama import ConfigManager

config_mgr = ConfigManager()
config_mgr.load_config()

# Update settings
config_mgr.update_config(
    default_model="llama3.1:latest",
    auto_start_server=False
)

# Get execution presets
presets = config_mgr.get_execution_presets()
creative_options = presets["creative"]  # Temperature 0.9, max_tokens 1024

config_mgr.save_config()
```

## Security Considerations

- **Local Execution**: All processing occurs locally, ensuring data privacy
- **Network Security**: Communication with Ollama server on localhost only by default
- **Input Validation**: All inputs are validated before processing
- **Output Sanitization**: Generated content is handled as untrusted data
- **Access Control**: Model access is controlled through configuration
- **Audit Logging**: All operations are logged through Codomyrmex logging system

## Performance Characteristics

- **Local Processing**: No external API calls, low latency
- **Resource Management**: Configurable timeouts and memory management
- **Model Caching**: Ollama provides efficient model loading and caching
- **Streaming Support**: Real-time response streaming via `run_streaming`
- **Concurrent Execution**: Support for batch processing with `run_batch`
- **Async Support**: Full async API for non-blocking operations

## Navigation Links

- **Parent**: [llm README](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../docs/README.md)
- **Home**: [Root README](../../../../README.md)

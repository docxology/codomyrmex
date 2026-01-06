# Ollama Integration - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Ollama Integration module of Codomyrmex. The module provides specialized integration with Ollama local Large Language Models, offering model management, execution, and output handling capabilities optimized for the Codomyrmex ecosystem.

## Classes

### OllamaManager

Primary interface for Ollama integration with comprehensive model management:

#### Methods

**`__init__(host: str = "localhost", port: int = 11434, **kwargs)`**
- Initialize Ollama manager with connection parameters
- **Parameters**: `host`, `port`, connection options
- **Errors**: `OllamaConnectionError` for connection failures

**`list_models() -> List[Dict]`**
- Retrieve available Ollama models
- **Return Value**: List of model information dictionaries
- **Errors**: `OllamaError` for API failures

**`pull_model(model_name: str, **kwargs) -> Dict`**
- Download and install Ollama model
- **Parameters**: `model_name`, download options
- **Return Value**: Model installation status and metadata
- **Errors**: `OllamaModelError` for model installation failures

**`run_model(model_name: str, prompt: str, **kwargs) -> Dict`**
- Execute model inference with prompt
- **Parameters**: `model_name`, `prompt`, generation parameters
- **Return Value**: Model response with metadata
- **Errors**: `OllamaModelError` for inference failures

**`get_model_info(model_name: str) -> Dict`**
- Retrieve detailed model information
- **Parameters**: `model_name`
- **Return Value**: Model metadata and capabilities
- **Errors**: `OllamaModelError` for model not found

### ModelRunner

Specialized model execution with performance optimization:

#### Methods

**`execute(prompt: str, model: str, **kwargs) -> Dict`**
- Execute model inference with optimized performance
- **Parameters**: `prompt`, `model`, execution options
- **Return Value**: Execution results with performance metrics
- **Errors**: `ModelExecutionError` for execution failures

**`stream_execute(prompt: str, model: str, **kwargs) -> Iterator[Dict]`**
- Stream model inference results for real-time processing
- **Parameters**: `prompt`, `model`, streaming options
- **Return Value**: Iterator of response chunks
- **Errors**: `ModelExecutionError` for streaming failures

**`benchmark_model(model: str, test_prompts: List[str], **kwargs) -> Dict`**
- Benchmark model performance across multiple prompts
- **Parameters**: `model`, `test_prompts`, benchmark options
- **Return Value**: Performance metrics and statistics
- **Errors**: `BenchmarkError` for benchmarking failures

### OutputManager

Model output processing and formatting utilities:

#### Methods

**`process_output(raw_output: Dict, format_type: str = "text", **kwargs) -> Dict`**
- Process and format model output
- **Parameters**: `raw_output`, `format_type`, formatting options
- **Return Value**: Processed output in specified format
- **Errors**: `OutputProcessingError` for processing failures

**`validate_output(output: Dict, schema: Optional[Dict] = None, **kwargs) -> Dict`**
- Validate model output against schema
- **Parameters**: `output`, `schema`, validation options
- **Return Value**: Validation results and compliance status
- **Errors**: `ValidationError` for validation failures

**`export_output(output: Dict, format: str, destination: str, **kwargs) -> Dict`**
- Export processed output to various formats
- **Parameters**: `output`, `format`, `destination`, export options
- **Return Value**: Export status and metadata
- **Errors**: `ExportError` for export failures

### ConfigManager

Configuration management for Ollama integration:

#### Methods

**`load_config(config_path: Optional[str] = None) -> Dict`**
- Load Ollama configuration from file or defaults
- **Parameters**: `config_path`, optional configuration file path
- **Return Value**: Loaded configuration dictionary
- **Errors**: `ConfigError` for configuration loading failures

**`validate_config(config: Dict) -> Dict`**
- Validate Ollama configuration parameters
- **Parameters**: `config`, configuration dictionary
- **Return Value**: Validation results and corrected configuration
- **Errors**: `ConfigError` for invalid configurations

**`save_config(config: Dict, config_path: str) -> None`**
- Save configuration to file
- **Parameters**: `config`, `config_path`
- **Errors**: `ConfigError` for configuration saving failures

## Error Handling

All classes follow consistent error handling patterns:

- **Connection Errors**: `OllamaConnectionError` for network and connectivity issues
- **Model Errors**: `OllamaModelError` for model loading, availability, or compatibility issues
- **Execution Errors**: `ModelExecutionError` for inference and execution failures
- **Processing Errors**: `OutputProcessingError` for output handling failures
- **Validation Errors**: `ValidationError` for output and configuration validation failures
- **Export Errors**: `ExportError` for output export failures
- **Configuration Errors**: `ConfigError` for configuration management issues
- **Benchmark Errors**: `BenchmarkError` for performance benchmarking issues

## Integration Patterns

### Basic Model Execution
```python
from codomyrmex.llm.ollama import OllamaManager

# Initialize manager
manager = OllamaManager(host="localhost", port=11434)

# Execute model
result = manager.run_model(
    model_name="llama2",
    prompt="Explain the concept of recursion in programming"
)

print(result['response'])
```

### Streaming Response Processing
```python
from codomyrmex.llm.ollama import ModelRunner

# Initialize runner
runner = ModelRunner()

# Stream execution
for chunk in runner.stream_execute(
    prompt="Write a Python function to calculate fibonacci numbers",
    model="codellama"
):
    if 'response' in chunk:
        print(chunk['response'], end='', flush=True)
    elif chunk.get('done', False):
        print(f"\
\
Tokens used: {chunk.get('total_tokens', 0)}")
```

### Output Processing Pipeline
```python
from codomyrmex.llm.ollama import OutputManager, OllamaManager

# Generate output
manager = OllamaManager()
raw_result = manager.run_model("llama2", "Generate JSON data about programming languages")

# Process output
processor = OutputManager()
processed = processor.process_output(raw_result, format_type="json")

# Validate output
validation = processor.validate_output(processed, schema=my_json_schema)

if validation['valid']:
    # Export to file
    processor.export_output(processed, format="json", destination="output.json")
```

### Configuration Management
```python
from codomyrmex.llm.ollama import ConfigManager

# Load configuration
config_mgr = ConfigManager()
config = config_mgr.load_config("ollama_config.yaml")

# Validate and apply
validated = config_mgr.validate_config(config)

# Save updated configuration
config_mgr.save_config(validated, "ollama_config.yaml")
```

## Security Considerations

- **Local Execution**: All processing occurs locally, ensuring data privacy
- **Network Security**: Secure communication with Ollama server
- **Input Validation**: All inputs are validated before processing
- **Output Sanitization**: Generated content is sanitized for safe consumption
- **Access Control**: Model access is controlled through configuration
- **Audit Logging**: All operations are logged for compliance

## Performance Characteristics

- **Local Processing**: No external API calls, low latency
- **Resource Management**: Configurable resource limits and monitoring
- **Model Caching**: Efficient model loading and caching
- **Streaming Support**: Real-time response streaming
- **Concurrent Execution**: Support for multiple simultaneous model runs
- **Memory Optimization**: Intelligent model unloading and memory management


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)

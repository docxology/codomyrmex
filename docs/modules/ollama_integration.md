# 🐙 Ollama Integration Module

Comprehensive integration with Ollama local LLMs, providing model management, execution, configuration, and output handling within the Codomyrmex ecosystem.

## 🌟 Overview

The Ollama Integration module enables seamless interaction with local Large Language Models through the Ollama framework. It provides:

- **Model Management**: List, download, and manage Ollama models
- **Flexible Execution**: Run models with custom parameters and options
- **Output Management**: Save responses, configurations, and execution results
- **Configuration Management**: Persistent settings and model preferences
- **Integration**: Seamless integration with Codomyrmex logging and data visualization

## 📋 Prerequisites

- **Ollama Installation**: `ollama` binary must be available in PATH
- **Ollama Server**: Server must be running (`ollama serve`)
- **Models**: At least one model downloaded (`ollama run model_name`)
- **Python Dependencies**: Standard Codomyrmex dependencies

## 🚀 Quick Start

### Basic Usage

```python
from codomyrmex.llm.ollama import OllamaManager, ModelRunner

# Initialize managers
manager = OllamaManager()
runner = ModelRunner(manager)

# List available models
models = manager.list_models()
print(f"Available models: {len(models)}")

# Run a model
result = runner.run_with_options(
    "llama3.1:latest",
    "Explain quantum computing in simple terms.",
    save_output=True
)

print(f"Response: {result.response}")
print(f"Execution time: {result.execution_time:.2f}s")
```

### Configuration Management

```python
from codomyrmex.llm.ollama import ConfigManager

# Initialize configuration manager
config = ConfigManager()

# Update settings
config.update_config(
    default_model="llama3.1:latest",
    base_output_dir="custom/output/path"
)

# Save configuration
config.save_config()
```

## 🏗️ Architecture

### Core Components

#### `OllamaManager`
Main integration class providing:
- Model discovery and listing
- Server management and connectivity
- Basic model execution
- Statistics and analytics

#### `ModelRunner`
Advanced execution engine offering:
- Custom execution options
- Batch processing
- Model comparison
- Benchmarking capabilities
- Conversation support

#### `OutputManager`
Output and configuration management:
- Response saving and organization
- Configuration persistence
- Batch result handling
- Statistics and cleanup

#### `ConfigManager`
System configuration management:
- Global settings management
- Model-specific configurations
- Execution presets
- Import/export functionality

## 🔧 API Reference

### OllamaManager

#### Model Management

```python
# List all available models
models = manager.list_models(force_refresh=True)

# Check model availability
available = manager.is_model_available("llama3.1:latest")

# Get model by name
model = manager.get_model_by_name("llama3.1:latest")

# Get model statistics
stats = manager.get_model_stats()
```

#### Model Execution

```python
# Basic execution
result = manager.run_model(
    model_name="llama3.1:latest",
    prompt="Your prompt here",
    save_output=True,
    output_dir="/custom/path"
)
```

### ModelRunner

#### Flexible Execution

```python
from codomyrmex.llm.ollama.model_runner import ExecutionOptions

# Custom execution options
options = ExecutionOptions(
    temperature=0.7,
    max_tokens=512,
    timeout=120
)

result = runner.run_with_options(
    "llama3.1:latest",
    "Your prompt",
    options,
    save_output=True
)
```

#### Batch Processing

```python
# Process multiple prompts
prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
results = runner.run_batch(
    "llama3.1:latest",
    prompts,
    max_concurrent=3
)
```

#### Model Comparison

```python
# Compare multiple models
comparison = runner.create_model_comparison(
    ["llama2:latest", "llama3.1:latest"],
    "Which model is better?"
)
```

#### Benchmarking

```python
# Benchmark model performance
benchmark = runner.benchmark_model(
    "llama3.1:latest",
    ["Test prompt 1", "Test prompt 2"]
)
```

### OutputManager

#### Saving Outputs

```python
# Save model response
output_path = output_manager.save_model_output(
    model_name="llama3.1:latest",
    prompt="User prompt",
    response="Model response",
    execution_time=2.5
)

# Save execution result
result_path = output_manager.save_execution_result(result)

# Save model configuration
config_path = output_manager.save_model_config(
    "llama3.1:latest",
    {"temperature": 0.7, "max_tokens": 512}
)
```

#### Loading and Statistics

```python
# Load model configuration
config = output_manager.load_model_config("llama3.1:latest")

# Get output statistics
stats = output_manager.get_output_stats()

# List saved outputs
outputs = output_manager.list_saved_outputs(output_type="outputs")
```

### ConfigManager

#### Configuration Management

```python
# Load configuration
config_manager.load_config()

# Update settings
config_manager.update_config(
    default_model="llama3.1:latest",
    auto_start_server=False
)

# Save configuration
config_manager.save_config()

# Validate configuration
validation = config_manager.validate_config()
```

#### Execution Presets

```python
# Get available presets
presets = config_manager.get_execution_presets()

# Use a preset
options = presets["creative"]  # Temperature 0.9, max_tokens 1024
```

#### Import/Export

```python
# Export configuration
config_manager.export_config("backup_config.json")

# Import configuration
config_manager.import_config("backup_config.json")
```

## 📊 Configuration Options

### Global Configuration

```json
{
  "ollama_binary": "ollama",
  "auto_start_server": true,
  "server_host": "localhost",
  "server_port": 11434,
  "base_output_dir": "scripts/output/examples/ollama",
  "save_all_outputs": true,
  "save_configs": true,
  "auto_cleanup_days": 30,
  "default_model": "llama3.1:latest",
  "preferred_models": ["llama3.1:latest", "codellama:latest"],
  "enable_logging": true,
  "enable_visualization": true,
  "enable_benchmarks": true
}
```

### Model-Specific Configuration

```json
{
  "temperature": 0.7,
  "max_tokens": 512,
  "timeout": 120,
  "top_p": 0.9,
  "top_k": 40,
  "repeat_penalty": 1.1
}
```

### Execution Presets

| Preset | Temperature | Max Tokens | Use Case |
|--------|-------------|------------|----------|
| `fast` | 0.1 | 512 | Quick responses, factual |
| `creative` | 0.9 | 1024 | Creative writing, brainstorming |
| `balanced` | 0.7 | 1024 | General purpose |
| `precise` | 0.3 | 2048 | Technical, detailed |
| `long_form` | 0.7 | 4096 | Long-form content |

## 🎯 Usage Examples

### Basic Model Execution

```python
from codomyrmex.llm.ollama import OllamaManager, ModelRunner

# Initialize
manager = OllamaManager()
runner = ModelRunner(manager)

# Simple execution
result = manager.run_model(
    "llama3.1:latest",
    "What is machine learning?",
    save_output=True
)

print(f"Answer: {result.response}")
```

### Advanced Execution with Options

```python
from codomyrmex.llm.ollama.model_runner import ExecutionOptions

# Custom options
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

### Batch Processing

```python
# Process multiple prompts
prompts = [
    "Explain recursion.",
    "What is object-oriented programming?",
    "How does garbage collection work?"
]

results = runner.run_batch(
    "llama3.1:latest",
    prompts,
    max_concurrent=2
)

for i, result in enumerate(results):
    print(f"Prompt {i+1}: {result.response[:100]}...")
```

### Model Comparison

```python
# Compare different models
comparison = runner.create_model_comparison(
    ["llama2:latest", "llama3.1:latest", "gemma2:2b"],
    "Which programming language is best for beginners?"
)

for model, data in comparison['results'].items():
    print(f"{model}: {data['response_preview']}")
```

### Configuration Management

```python
from codomyrmex.llm.ollama import ConfigManager, OutputManager

# Setup configuration
config = ConfigManager()
config.update_config(
    default_model="llama3.1:latest",
    base_output_dir="my_ollama_outputs"
)

# Setup output management
output_manager = OutputManager("my_ollama_outputs")

# Run and save
result = manager.run_model(
    config.config.default_model,
    "Your prompt here",
    save_output=True,
    output_dir=output_manager.outputs_dir
)
```

## 🔍 Advanced Features

### Conversation Support

```python
# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there! How can I help?"},
    {"role": "user", "content": "What's the weather like?"}
]

result = runner.run_conversation("llama3.1:latest", messages)
```

### Context Integration

```python
# Include additional context
context_docs = [
    "Context: Machine learning is AI that learns from data.",
    "Context: Neural networks mimic brain structure."
]

result = runner.run_with_context(
    "llama3.1:latest",
    "Explain how neural networks work.",
    context_docs
)
```

### Benchmarking

```python
# Performance benchmarking
test_prompts = [
    "What is 2+2?",
    "Explain quantum physics.",
    "Write a haiku about coding."
]

benchmark = runner.benchmark_model("llama3.1:latest", test_prompts)
print(f"Average execution time: {benchmark['avg_execution_time']:.2f}s")
print(f"Average tokens/sec: {benchmark['avg_tokens_per_second']:.1f}")
```

## 📁 Output Structure

```
scripts/output/examples/ollama/
├── outputs/           # Model execution outputs
│   ├── llama3.1:latest/
│   │   ├── response_001.txt
│   │   └── response_002.txt
│   └── codellama:latest/
│       └── response_001.txt
├── configs/           # Configuration files
│   ├── ollama_config.json
│   └── llama3.1:latest/
│       └── model_config.json
├── logs/             # Execution logs
└── reports/          # Benchmark and comparison reports
    ├── benchmarks/
    └── comparisons/
```

## 🔧 Integration with Codomyrmex

### Logging Integration

All Ollama operations are automatically logged through Codomyrmex logging:

```python
# Logging is automatic - no additional setup needed
result = manager.run_model("llama3.1:latest", "test prompt")
# This will be logged with timestamps, execution time, etc.
```

### Data Visualization Integration

```python
# Visualize model comparison results
from codomyrmex.data_visualization import create_bar_chart

comparison = runner.create_model_comparison(models, prompt)
categories = list(comparison['results'].keys())
execution_times = [r['execution_time'] for r in comparison['results'].values()]

create_bar_chart(
    categories=categories,
    values=execution_times,
    title="Model Execution Time Comparison",
    output_path="model_comparison.png"
)
```

## 🧪 Testing

Comprehensive test suite validates all functionality:

```bash
# Run all Ollama integration tests
python -m pytest src/codomyrmex/tests/unit/test_ollama_integration.py -v

# Run specific test categories
python -m pytest src/codomyrmex/tests/unit/test_ollama_integration.py::TestOllamaIntegration -v
python -m pytest src/codomyrmex/tests/unit/test_ollama_integration.py::TestOllamaIntegrationRealExecution -v
```

### Test Coverage

- ✅ **23 comprehensive tests** covering all functionality
- ✅ **Real model execution** (no mocks)
- ✅ **Configuration management** validation
- ✅ **Output persistence** verification
- ✅ **Error handling** and edge cases
- ✅ **Integration testing** with Codomyrmex modules

## 🚨 Troubleshooting

### Common Issues

#### "Ollama server not responding"
```bash
# Start the Ollama server
ollama serve

# Verify server is running
ollama list
```

#### "Model not available"
```bash
# Download the model
ollama run llama3.1:8b

# Verify it's available
ollama list
```

#### "Permission denied" errors
```bash
# Ensure ollama binary is executable
chmod +x $(which ollama)

# Check if server is already running on different port
ps aux | grep ollama
```

#### Configuration loading errors
```python
# Reset to defaults if config is corrupted
config = ConfigManager()
config.reset_to_defaults()
config.save_config()
```

## 🎓 Best Practices

### Model Selection
- **Start small**: Use smaller models (135M-2B) for testing
- **Match use case**: Choose models based on your needs (code, general, vision)
- **Monitor resources**: Larger models require more RAM and disk space

### Execution Optimization
- **Use appropriate timeouts**: Adjust based on model size and complexity
- **Batch processing**: Use `run_batch()` for multiple prompts
- **Save outputs**: Enable output saving for analysis and debugging

### Configuration Management
- **Regular backups**: Export configurations before major changes
- **Validate settings**: Use `validate_config()` before deployment
- **Organize outputs**: Use descriptive names for saved files

### Performance Tips
- **Model caching**: Ollama caches models for faster subsequent runs
- **Concurrent execution**: Use batch processing for multiple requests
- **Resource monitoring**: Monitor RAM usage with large models

## 🔮 Future Enhancements

- **Streaming responses**: Real-time response streaming
- **Advanced parameter control**: More granular model configuration
- **Model fine-tuning**: Integration with model training capabilities
- **Multi-modal support**: Vision and audio model integration
- **Performance optimization**: GPU acceleration and memory management

## 📞 Support

For issues and questions:
- Check the test suite for examples of proper usage
- Review the example scripts in `examples/`
- Consult the Ollama documentation for model-specific issues
- Use Codomyrmex logging for debugging integration issues

---

**🎯 Result**: Comprehensive Ollama integration providing seamless local LLM management, execution, configuration, and output handling within the Codomyrmex ecosystem.

**Status**: ✅ **FULLY FUNCTIONAL** - All 23 tests passing, real model execution validated, configuration and output management working correctly.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)

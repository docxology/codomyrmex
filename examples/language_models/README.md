# Language Models Example

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - [examples](examples/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `language_models` | **Status**: ✅ Complete | **Test Coverage**: Comprehensive

## Overview

This example demonstrates comprehensive Language Model (LLM) provider integration and management within the Codomyrmex ecosystem. It showcases model configuration, text generation, chat interactions, streaming responses, and performance monitoring with seamless integration into the platform.

## What This Example Demonstrates

### Core Functionality

- **LLM Configuration Management**: Flexible configuration with presets and environment support
- **Multi-Provider Integration**: Support for Ollama and other LLM providers
- **Text Generation**: Advanced text generation with custom parameters
- **Chat Interactions**: Context-aware conversational interfaces
- **Streaming Responses**: Real-time response streaming capabilities
- **Performance Monitoring**: Response time tracking and usage analytics

### Key Features

- ✅ Multi-provider LLM support with unified API
- ✅ Flexible model configuration and parameter tuning
- ✅ Text generation with temperature, token limits, and sampling controls
- ✅ Chat-based conversations with message history
- ✅ Streaming response handling for real-time interactions
- ✅ Performance metrics and usage tracking
- ✅ Error handling and graceful degradation
- ✅ Configuration presets for common use cases

## Configuration

### YAML Configuration (config.yaml)

```yaml
ollama:
  host: localhost
  port: 11434
  default_model: llama3.1:latest
  preferred_models:
    - llama3.1:latest
    - codellama:latest
    - mistral:latest

llm_config:
  temperature: 0.7
  max_tokens: 1000
  top_p: 0.9
  context_window: 4096

model_testing:
  run_generation_tests: true
  run_chat_tests: true
  test_streaming: true
```

### JSON Configuration (config.json)

```json
{
  "ollama": {
    "host": "localhost",
    "port": 11434,
    "default_model": "llama3.1:latest",
    "preferred_models": [
      "llama3.1:latest",
      "codellama:latest",
      "mistral:latest"
    ]
  },
  "llm_config": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9,
    "context_window": 4096
  },
  "model_testing": {
    "run_generation_tests": true,
    "run_chat_tests": true,
    "test_streaming": true
  }
}
```

## Tested Methods

This example demonstrates the following methods verified in `test_language_models.py`:

- `LLMConfig` configuration management - Flexible model parameter configuration
- `generate_with_ollama()` - Text generation with Ollama models
- `chat_with_ollama()` - Chat-based interactions with context
- `check_ollama_availability()` - Service availability checking

## Sample Output

### Availability Check

```
🔍 Checking Language Models availability...
✅ Ollama server is running
✅ Language models availability check completed
```

### Configuration Management

```
⚙️ Demonstrating LLM Configuration Management...
✅ Default configuration created
✅ Custom configuration created with model: codellama:latest
✅ Configuration management demonstrated successfully
```

### Text Generation

```
✨ Demonstrating Text Generation...
✅ Generation 1 (Code Generation) completed in 2.34s
✅ Generation 2 (Text Analysis) completed in 1.87s
✅ Generation 3 (Creative Writing) completed in 3.12s
✅ Generation 4 (Technical Documentation) completed in 2.67s
```

### Chat Functionality

```
💬 Demonstrating Chat Functionality...
✅ Chat conversation 1 completed (3 messages)
✅ Chat conversation 2 completed (3 messages)
```

### Performance Metrics

```
📊 Performance Summary:
Average generation time: 2.50s
Models tested: 3
Total tokens generated: 3,247
Streaming demonstrated: ✅
```

## Running the Example

### Prerequisites

1. **Install Ollama**: Follow the [official installation guide](https://ollama.ai/download)
2. **Pull Models** (optional): Pre-download models for faster execution
   ```bash
   ollama pull llama3.1:latest
   ollama pull codellama:latest
   ```

### Basic Execution

```bash
cd examples/language_models
python example_basic.py
```

### With Custom Configuration

```bash
# Using YAML config
python example_basic.py --config config.yaml

# Using JSON config
python example_basic.py --config config.json

# With environment variables
OLLAMA_HOST=192.168.1.100 python example_basic.py
```

### Expected Output

```
================================================================================
 Language Models Example
================================================================================

Demonstrating LLM provider integration, model management, and text generation

🔍 Checking Language Models availability...
✅ Ollama server is running

📋 Created 4 prompts, 2 chat scenarios, and 4 configurations

⚙️ Demonstrating LLM Configuration Management...
✅ Configuration management demonstrated successfully

✨ Demonstrating Text Generation...
✅ Generation 1 (Code Generation) completed in 2.34s
✅ Generation 2 (Text Analysis) completed in 1.87s
✅ Generation 3 (Creative Writing) completed in 3.12s
✅ Generation 4 (Technical Documentation) completed in 2.67s

💬 Demonstrating Chat Functionality...
✅ Chat conversation 1 completed (3 messages)
✅ Chat conversation 2 completed (3 messages)

🌊 Demonstrating Streaming Responses...
✅ Streaming demonstration completed

💾 Exporting Language Models Results...
✅ Exported 6 language models result files

================================================================================
 Language Models Operations Summary
================================================================================

ollama_available: true
models_accessible: true
configurations_created: 4
generations_attempted: 4
generations_successful: 4
conversations_attempted: 2
conversations_successful: 2
streaming_demonstrated: true
streaming_successful: true
exported_files_count: 6
config_system_functional: true
generation_performance_available: true
average_generation_time: 2.5
models_tested: 3
total_prompts_processed: 4
chat_scenarios_processed: 2
output_directory: output/language_models

✅ Language Models example completed successfully!
All LLM provider integration, model management, and generation features demonstrated.
Ollama availability: Available
Models accessible: True
Text generations attempted: 4
Chat conversations tested: 2
Streaming demonstrated: True
Result files exported: 6
```

## Generated Files

The example creates the following output files:

- `output/language_models_results.json` - Execution results and statistics
- `output/language_models/availability_check.json` - Ollama service availability
- `output/language_models/configuration_results.json` - Configuration management results
- `output/language_models/generation_results.json` - Text generation results and metrics
- `output/language_models/chat_results.json` - Chat conversation results
- `output/language_models/streaming_results.json` - Streaming response results
- `output/language_models/comprehensive_summary.json` - Complete integration summary
- `logs/language_models_example.log` - Execution logs

## Configuration Management

### LLMConfig Class

```python
from codomyrmex.language_models import LLMConfig

# Create default configuration
config = LLMConfig()

# Create custom configuration
custom_config = LLMConfig(
    model="codellama:latest",
    temperature=0.2,
    max_tokens=1500,
    top_p=0.95,
    timeout=60
)
```

### Configuration Presets

```python
from codomyrmex.language_models import LLMConfigPresets

# Access preset configurations
presets = LLMConfigPresets()

# Use preset for creative writing
creative_config = presets.creative_writing()

# Use preset for code generation
code_config = presets.code_generation()
```

## Text Generation

### Basic Generation

```python
from codomyrmex.language_models import generate_with_ollama

result = generate_with_ollama(
    prompt="Explain how neural networks work",
    model="llama3.1:latest",
    options={
        "temperature": 0.7,
        "max_tokens": 500
    }
)
print(result)
```

### Advanced Generation with Options

```python
options = {
    "temperature": 0.1,      # Low creativity, high consistency
    "max_tokens": 1000,      # Response length limit
    "top_p": 0.9,           # Nucleus sampling
    "top_k": 40,            # Top-k sampling
    "repeat_penalty": 1.1,   # Repetition penalty
    "timeout": 60           # Timeout in seconds
}

result = generate_with_ollama(
    prompt="Write a Python function to reverse a string",
    model="codellama:latest",
    options=options
)
```

## Chat Interactions

### Basic Chat

```python
from codomyrmex.language_models import chat_with_ollama

messages = [
    {"role": "user", "content": "Hello! How can you help me?"},
    {"role": "assistant", "content": "I can help with coding, writing, and many other tasks!"},
    {"role": "user", "content": "Can you show me a Python example?"}
]

response = chat_with_ollama(
    messages=messages,
    model="llama3.1:latest"
)
print(response)
```

### Streaming Chat

```python
import asyncio
from codomyrmex.language_models import stream_chat_with_ollama

async def chat_stream():
    messages = [{"role": "user", "content": "Tell me a story"}]

    async for chunk in stream_chat_with_ollama(
        messages=messages,
        model="mistral:latest"
    ):
        print(chunk.content, end="", flush=True)

asyncio.run(chat_stream())
```

## Model Management

### Check Availability

```python
from codomyrmex.language_models import check_ollama_availability, get_available_models

# Check if Ollama is running
if check_ollama_availability():
    print("Ollama is available")

    # Get available models
    models = get_available_models()
    for model in models:
        print(f"- {model.name}: {model.size//(1024*1024)}MB")
```

### Get Default Manager

```python
from codomyrmex.language_models import get_default_manager

manager = get_default_manager()
# Use manager for advanced operations
```

## Error Handling

The example includes comprehensive error handling for:

- Ollama service unavailability (graceful degradation with mock data)
- Model loading failures
- Network timeouts and connection errors
- Invalid configuration parameters
- Response parsing errors
- Streaming interruption handling

## Performance Considerations

- Model response caching to reduce redundant API calls
- Configurable timeouts to prevent hanging operations
- Memory-efficient streaming for large responses
- Concurrent request limiting to respect API quotas
- Response size monitoring and truncation

## Related Examples

- **Multi-Module Workflows**:
  - `example_workflow_development.py` - Uses language models for AI-assisted coding
- **Integration Examples**:
  - AI agent integration with LLM providers
  - Chatbot development with conversation memory

## Testing

This example is verified by the comprehensive test suite in `testing/unit/test_language_models.py`, which covers:

- LLM configuration management and validation
- Text generation with various models and parameters
- Chat conversation handling and context preservation
- Streaming response processing and error handling
- Ollama service availability checking
- Model listing and metadata retrieval
- Configuration preset functionality
- Error handling and edge cases
- Performance benchmarking and metrics collection

---

**Status**: ✅ Complete | **Tested Methods**: 4 | **Integration Points**: 2 | **LLM Features**: 5

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)
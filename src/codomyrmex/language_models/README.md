# Language Models Module

Comprehensive integration with local Large Language Models, primarily focused on Ollama.

## Overview

This module provides a complete interface for interacting with local LLMs through the Ollama API. All components are functional, production-ready implementations that interact with actual Ollama services:

- **Functional network I/O** with proper error handling and retry logic
- **Synchronous and asynchronous** support for all operations
- **Functional streaming** capabilities for actual LLM text generation
- **Connection pooling** and session management
- **Comprehensive error handling** with custom exception types
- **Caching** for model information to reduce API calls
- **Type hints** throughout for better IDE support
- **Configuration management** with environment variable support
- **Organized output structure** for test results and LLM responses
- **Comprehensive testing** using actual Ollama models with verified outputs

## Configuration

The module includes comprehensive configuration management with environment variable support:

### Environment Variables

```bash
# Set default model
export LLM_MODEL="llama3.1:latest"

# Configure generation parameters
export LLM_TEMPERATURE="0.7"
export LLM_MAX_TOKENS="1000"
export LLM_TOP_P="0.9"

# Configure connection
export LLM_BASE_URL="http://localhost:11434"
export LLM_TIMEOUT="30"

# Configure output directories
export LLM_OUTPUT_ROOT="src/codomyrmex/language_models/outputs"
```

### Programmatic Configuration

```python
from codomyrmex.language_models import LLMConfig, LLMConfigPresets

# Use preset configurations
config = LLMConfigPresets.creative()  # High creativity
config = LLMConfigPresets.precise()   # Low temperature, factual
config = LLMConfigPresets.fast()      # Optimized for speed

# Custom configuration
config = LLMConfig(
    model="llama3.1:latest",
    temperature=0.8,
    max_tokens=1500,
    base_url="http://localhost:11434"
)

# Save/load configuration
config.save_config("my_config.json")
loaded_config = LLMConfig.from_file("my_config.json")
```

### Output Structure

The module organizes outputs into clear subdirectories:

```
outputs/
├── config/           # Configuration files
├── integration/      # Integration test outputs
├── llm_outputs/      # LLM response markdown files
├── logs/            # Log files
├── models/          # Model information
├── performance/     # Performance metrics
├── reports/         # Generated reports
└── test_results/    # JSON test results
```

## Quick Start

### Basic Usage

```python
from codomyrmex.language_models import generate_with_ollama, chat_with_ollama

# Simple text generation
response = generate_with_ollama("Explain quantum computing in simple terms")
print(response)

# Chat with conversation history
messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "How do I optimize a Python loop?"}
]
response = chat_with_ollama(messages)
print(response)
```

### Advanced Usage

```python
from codomyrmex.language_models import OllamaClient, OllamaManager

# Create client with custom configuration
client = OllamaClient(
    base_url="http://localhost:11434",
    model="llama3.1",
    timeout=60,
    max_retries=3
)

# Use the client directly
models = client.list_models()
response = client.generate("Your prompt here", options={"temperature": 0.8})

# Or use the high-level manager
manager = OllamaManager(base_url="http://localhost:11434")
manager.set_default_options(temperature=0.7, top_p=0.9)
response = manager.generate("Your prompt here")

# Clean up
client.close()
```

### Async and Streaming

```python
import asyncio
from codomyrmex.language_models import stream_with_ollama, stream_chat_with_ollama

async def main():
    # Streaming text generation
    async for chunk in stream_with_ollama("Tell me a story"):
        print(chunk, end="", flush=True)

    # Streaming chat
    messages = [{"role": "user", "content": "Write a haiku about programming"}]
    async for chunk in stream_chat_with_ollama(messages):
        print(chunk, end="", flush=True)

# Run the async function
asyncio.run(main())
```

## API Reference

### OllamaClient

Core client class with comprehensive functionality.

#### Initialization

```python
OllamaClient(
    base_url: str = "http://localhost:11434",
    model: str = "llama3.1",
    timeout: int = 30,
    max_retries: int = 3,
    backoff_factor: float = 0.3,
    session: Optional[requests.Session] = None,
    verify_ssl: bool = True,
)
```

#### Methods

- `list_models(use_cache: bool = True) -> List[Dict]`: List available models
- `check_model_exists(model: str) -> bool`: Check if model exists
- `generate(prompt, model=None, options=None, stream=False)`: Generate text
- `chat(messages, model=None, options=None, stream=False)`: Chat completion
- `get_model_info(model=None) -> Dict`: Get model details
- `close()`: Close client session

### OllamaManager

High-level manager with convenience features.

#### Methods

- `set_default_options(**options)`: Set default generation options
- `generate(prompt, model=None, options=None, stream=False)`: Generate text
- `chat(messages, model=None, options=None, stream=False)`: Chat completion
- `list_models() -> List[Dict]`: List models
- `check_health() -> bool`: Check server health
- `close()`: Close manager

### Convenience Functions

#### Synchronous

- `generate_with_ollama(prompt, model="llama3.1", options=None, **kwargs) -> str`
- `chat_with_ollama(messages, model="llama3.1", options=None, **kwargs) -> str`

#### Asynchronous

- `stream_with_ollama(prompt, model="llama3.1", options=None, **kwargs) -> AsyncGenerator[str]`
- `stream_chat_with_ollama(messages, model="llama3.1", options=None, **kwargs) -> AsyncGenerator[str]`

#### Utilities

- `check_ollama_availability(base_url="http://localhost:11434", timeout=5) -> bool`
- `get_available_models(base_url="http://localhost:11434", timeout=30) -> List[str]`
- `create_chat_messages(system_prompt=None, user_message="", conversation_history=None) -> List[Dict]`

## Error Handling

The module defines custom exceptions for different error types:

- `OllamaError`: Base exception for all Ollama-related errors
- `OllamaConnectionError`: Network and connection issues
- `OllamaTimeoutError`: Request timeout errors
- `OllamaModelError`: Model-related errors

```python
from codomyrmex.language_models import (
    OllamaClient,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaModelError
)

try:
    response = client.generate("Your prompt")
except OllamaConnectionError as e:
    print(f"Connection failed: {e}")
except OllamaTimeoutError as e:
    print(f"Request timed out: {e}")
except OllamaModelError as e:
    print(f"Model error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration Options

Common generation options you can pass:

- `temperature`: Controls randomness (0.0-2.0)
- `top_p`: Nucleus sampling parameter (0.0-1.0)
- `top_k`: Top-k sampling parameter (0-100)
- `repeat_penalty`: Penalty for repetition (0.0-2.0)
- `tfs_z`: Tail-free sampling parameter (0.0-1.0)
- `typical_p`: Typical sampling parameter (0.0-1.0)
- `repeat_last_n`: Number of previous tokens to consider for repetition
- `frequency_penalty`: Frequency penalty (0.0-2.0)
- `presence_penalty`: Presence penalty (0.0-2.0)
- `mirostat`: Enable Mirostat sampling (0, 1, or 2)
- `mirostat_eta`: Mirostat learning rate (0.0-1.0)
- `mirostat_tau`: Mirostat target entropy (0.0-10.0)
- `num_ctx`: Context window size
- `num_gqa`: Grouped query attention layers
- `num_gpu`: GPU layers (-1 for all)
- `num_thread`: Number of threads
- `num_predict`: Maximum tokens to generate
- `tfs_z`: Tail-free sampling parameter
- `top_k`: Top-k sampling parameter
- `typical_p`: Typical sampling parameter

## Examples

See the `examples/` directory for comprehensive usage examples.

### Basic Generation

```python
from codomyrmex.language_models import generate_with_ollama

# Simple generation with custom options
response = generate_with_ollama(
    "Write a Python function to calculate fibonacci numbers",
    options={"temperature": 0.3, "num_predict": 200}
)
print(response)
```

### Chat Interface

```python
from codomyrmex.language_models import chat_with_ollama, create_chat_messages

# Create conversation
messages = create_chat_messages(
    system_prompt="You are a Python expert.",
    user_message="How do I handle exceptions in Python?"
)

response = chat_with_ollama(messages)
print(response)
```

### Streaming

```python
import asyncio
from codomyrmex.language_models import stream_with_ollama

async def stream_example():
    prompt = "Write a short story about AI"
    async for chunk in stream_with_ollama(prompt):
        print(chunk, end="", flush=True)
    print()  # New line at end

asyncio.run(stream_example())
```

### Error Handling

```python
from codomyrmex.language_models import (
    OllamaClient, check_ollama_availability,
    OllamaConnectionError
)

# Check if Ollama is available first
if check_ollama_availability():
    client = OllamaClient()

    try:
        response = client.generate("Your prompt")
        print(f"Success: {response}")
    except OllamaConnectionError:
        print("Failed to connect to Ollama server")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
else:
    print("Ollama server is not available")
```

## Testing

The module includes comprehensive tests:

```bash
# Run all tests
pytest src/codomyrmex/language_models/tests/

# Run specific test file
pytest src/codomyrmex/language_models/tests/test_ollama_client.py

# Run with verbose output
pytest -v src/codomyrmex/language_models/tests/

# Run async tests
pytest -v src/codomyrmex/language_models/tests/test_ollama_integration.py::TestConvenienceFunctions::test_stream_with_ollama
```

## Performance Considerations

- **Connection pooling**: The client reuses HTTP connections for better performance
- **Model caching**: Model information is cached to reduce API calls
- **Async support**: Use async functions for better performance with I/O operations
- **Streaming**: Use streaming for real-time applications to reduce memory usage
- **Timeout configuration**: Set appropriate timeouts based on your use case

## Troubleshooting

### Common Issues

1. **Connection refused**: Make sure Ollama is running and accessible
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/version
   ```

2. **Model not found**: Verify the model is installed in Ollama
   ```bash
   ollama list
   ```

3. **Timeout errors**: Increase timeout values for slow models
   ```python
   client = OllamaClient(timeout=120)  # 2 minutes
   ```

4. **SSL errors**: Disable SSL verification if using self-signed certificates
   ```python
   client = OllamaClient(verify_ssl=False)
   ```

### Debug Logging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your code here
response = generate_with_ollama("Test prompt")
```

## Contributing

When contributing to this module:

1. Add comprehensive tests for new features
2. Update type hints as needed
3. Follow the existing error handling patterns
4. Update documentation for API changes
5. Ensure backward compatibility when possible

## License

This module is part of the Codomyrmex project and follows the same license terms.

# Language Models - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Language Models module of Codomyrmex. The module provides comprehensive integration with local Large Language Models (LLMs), primarily through Ollama, offering both low-level client access and high-level integration utilities for AI-powered workflows.

## Functions

### Function: `generate_with_ollama(prompt: str, model: str = "llama2", **kwargs) -> Dict`

- **Description**: Generate text completions using Ollama models with configurable parameters.
- **Parameters**:
    - `prompt`: Input text prompt for generation.
    - `model`: Ollama model name (default: "llama2").
    - `**kwargs`: Generation parameters (temperature, max_tokens, top_p, etc.).
- **Return Value**:
    ```python
    {
        "response": <str>,
        "model": <str>,
        "prompt_tokens": <int>,
        "response_tokens": <int>,
        "total_tokens": <int>,
        "generation_time": <float>,
        "parameters": {<generation_parameters>},
        "metadata": {
            "ollama_version": <str>,
            "model_digest": <str>,
            "created_at": <timestamp>
        }
    }
    ```
- **Errors**: Raises `OllamaError` for connection, model, or generation failures.

### Function: `stream_with_ollama(prompt: str, model: str = "llama2", **kwargs) -> Iterator[Dict]`

- **Description**: Stream text generation results for real-time processing and large outputs.
- **Parameters**:
    - `prompt`: Input text prompt for generation.
    - `model`: Ollama model name (default: "llama2").
    - `**kwargs`: Streaming parameters (chunk_size, timeout, etc.).
- **Return Value**: Iterator yielding generation chunks with metadata.
- **Errors**: Raises `OllamaError` for connection or streaming failures.

### Function: `chat_with_ollama(messages: List[Dict], model: str = "llama2", **kwargs) -> Dict`

- **Description**: Conduct conversational interactions with Ollama models using chat format.
- **Parameters**:
    - `messages`: List of chat messages with role/content format.
    - `model`: Ollama model name (default: "llama2").
    - `**kwargs`: Chat parameters (system_prompt, temperature, etc.).
- **Return Value**:
    ```python
    {
        "response": <str>,
        "conversation": [<full_message_history>],
        "model": <str>,
        "usage": {
            "prompt_tokens": <int>,
            "response_tokens": <int>,
            "total_tokens": <int>
        },
        "metadata": {<model_and_timing_info>}
    }
    ```
- **Errors**: Raises `OllamaError` for chat processing failures.

### Function: `stream_chat_with_ollama(messages: List[Dict], model: str = "llama2", **kwargs) -> Iterator[Dict]`

- **Description**: Stream conversational responses for interactive chat applications.
- **Parameters**:
    - `messages`: List of chat messages.
    - `model`: Ollama model name (default: "llama2").
    - `**kwargs`: Streaming chat parameters.
- **Return Value**: Iterator yielding chat response chunks.
- **Errors**: Raises `OllamaError` for streaming chat failures.

### Function: `check_ollama_availability(host: str = "localhost", port: int = 11434, **kwargs) -> Dict`

- **Description**: Verify Ollama service availability and retrieve system information.
- **Parameters**:
    - `host`: Ollama server hostname (default: "localhost").
    - `port`: Ollama server port (default: 11434).
    - `**kwargs`: Connection parameters (timeout, retries, etc.).
- **Return Value**:
    ```python
    {
        "available": <bool>,
        "version": <str>,
        "host": <str>,
        "port": <int>,
        "models": [<list_of_available_models>],
        "system_info": {<ollama_system_information>},
        "response_time_ms": <float>
    }
    ```
- **Errors**: Raises `OllamaConnectionError` for connectivity issues.

### Function: `get_available_models(host: str = "localhost", port: int = 11434, **kwargs) -> List[Dict]`

- **Description**: Retrieve detailed information about available Ollama models.
- **Parameters**:
    - `host`: Ollama server hostname (default: "localhost").
    - `port`: Ollama server port (default: 11434).
    - `**kwargs`: Query parameters (detailed_info, cached, etc.).
- **Return Value**: List of model information dictionaries.
- **Errors**: Raises `OllamaError` for model enumeration failures.

### Function: `create_chat_messages(system_prompt: Optional[str] = None, user_message: str = "", **kwargs) -> List[Dict]`

- **Description**: Create properly formatted chat message structures for Ollama conversations.
- **Parameters**:
    - `system_prompt`: Optional system prompt for conversation context.
    - `user_message`: Initial user message.
    - `**kwargs`: Additional message formatting options.
- **Return Value**: List of properly formatted chat messages.
- **Errors**: Raises `ValueError` for invalid message formats.

### Function: `get_default_manager(**kwargs) -> OllamaManager`

- **Description**: Get the default Ollama manager instance with configuration.
- **Parameters**:
    - `**kwargs`: Manager configuration options.
- **Return Value**: Configured OllamaManager instance.
- **Errors**: Raises `OllamaError` for configuration or initialization issues.

## Configuration Functions

### Function: `get_config() -> LLMConfig`

- **Description**: Retrieve current LLM configuration.
- **Return Value**: Current LLMConfig object.
- **Errors**: Raises `ConfigError` for configuration access issues.

### Function: `set_config(config: LLMConfig) -> None`

- **Description**: Update LLM configuration.
- **Parameters**:
    - `config`: New LLMConfig object.
- **Errors**: Raises `ConfigError` for invalid configuration.

### Function: `reset_config() -> None`

- **Description**: Reset LLM configuration to defaults.
- **Errors**: Raises `ConfigError` for reset failures.

## Data Structures

### LLMConfig
Language model configuration settings:
```python
{
    "default_model": <str>,
    "temperature": <float>,
    "max_tokens": <int>,
    "top_p": <float>,
    "top_k": <int>,
    "repeat_penalty": <float>,
    "timeout_seconds": <int>,
    "max_retries": <int>,
    "ollama_host": <str>,
    "ollama_port": <int>,
    "output_directory": <str>,
    "log_level": <str>,
    "cache_enabled": <bool>,
    "stream_chunk_size": <int>
}
```

### OllamaManager
High-level Ollama management interface:
```python
{
    "client": <OllamaClient>,
    "config": <LLMConfig>,
    "model_cache": {<cached_model_info>},
    "performance_stats": {<usage_statistics>},
    "active_streams": [<list_of_active_streams>],
    "connection_pool": <ConnectionPool>
}
```

### Chat Messages Format
Standard chat message structure:
```python
[
    {
        "role": "system",
        "content": <str>
    },
    {
        "role": "user",
        "content": <str>
    },
    {
        "role": "assistant",
        "content": <str>
    }
]
```

## Error Handling

All functions follow consistent error handling patterns:

- **Connection Errors**: `OllamaConnectionError` for network and connectivity issues
- **Model Errors**: `OllamaModelError` for model loading, availability, or compatibility issues
- **Timeout Errors**: `OllamaTimeoutError` for request timeout situations
- **General Errors**: `OllamaError` for other Ollama-related failures
- **Configuration Errors**: `ConfigError` for configuration validation and access issues

## Integration Patterns

### With AI Code Editing
```python
from codomyrmex.language_models import generate_with_ollama
from codomyrmex.ai_code_editing import generate_code_snippet

# Use Ollama for code generation
code_result = generate_with_ollama(
    prompt="Write a Python function to calculate fibonacci numbers",
    model="codellama",
    temperature=0.1
)

# Process with AI code editing module
refined_code = generate_code_snippet(
    prompt=f"Refactor this code for better performance: {code_result['response']}",
    language="python"
)
```

### With Streaming Applications
```python
from codomyrmex.language_models import stream_chat_with_ollama, create_chat_messages

# Create conversation
messages = create_chat_messages(
    system_prompt="You are a helpful coding assistant.",
    user_message="Explain async/await in Python"
)

# Stream the response
for chunk in stream_chat_with_ollama(messages, model="llama2"):
    if chunk.get("done", False):
        print(f"\\n\\nTotal tokens: {chunk.get('total_tokens', 0)}")
    else:
        print(chunk.get("response", ""), end="", flush=True)
```

### With Configuration Management
```python
from codomyrmex.language_models import get_config, set_config, LLMConfig
from codomyrmex.config_management import load_configuration

# Load LLM configuration from external config
app_config = load_configuration(["config/llm.yaml"])
llm_config = LLMConfig(**app_config.get("llm", {}))

# Apply configuration
set_config(llm_config)

# Verify configuration
current_config = get_config()
print(f"Using model: {current_config.default_model}")
```

## Security Considerations

- **Local Execution**: All LLM processing occurs locally, ensuring data privacy
- **Network Security**: HTTPS/TLS encryption for Ollama server communication
- **Input Validation**: All prompts and messages are validated before processing
- **Output Sanitization**: Generated content is sanitized for safe consumption
- **Rate Limiting**: Built-in rate limiting to prevent resource exhaustion
- **Audit Logging**: All LLM interactions are logged for compliance and debugging

## Performance Characteristics

- **Local Processing**: No cloud API latency, faster response times
- **Resource Management**: Configurable resource limits and connection pooling
- **Caching**: Model and response caching for improved performance
- **Streaming**: Real-time streaming for large outputs and interactive applications
- **Concurrent Requests**: Support for multiple simultaneous LLM interactions
- **Memory Optimization**: Efficient memory usage with model unloading when idle


# Codomyrmex Agents — src/codomyrmex/language_models

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing language model infrastructure and management capabilities for the Codomyrmex platform. This module enables integration with multiple Large Language Model providers, handles API management, and provides benchmarking and performance analysis tools.

The language_models module serves as the AI foundation, enabling intelligent capabilities throughout the platform through standardized model interactions.

## Module Overview

### Key Capabilities
- **Multi-Provider Support**: Integration with OpenAI, Anthropic, Google AI, and other providers
- **Model Management**: Model selection, configuration, and performance optimization
- **API Abstraction**: Unified interface across different LLM providers
- **Benchmarking Tools**: Performance analysis and model comparison
- **Cost Tracking**: Usage monitoring and cost optimization
- **Fallback Mechanisms**: Automatic provider switching for reliability

### Key Features
- Provider-agnostic API design for easy switching
- Configurable model parameters and settings
- Response caching and optimization
- Rate limiting and quota management
- Comprehensive error handling and retry logic
- Performance metrics and analytics

## Function Signatures

### Ollama Integration Functions

```python
def get_default_manager(**client_kwargs) -> OllamaManager
```

Get or create default Ollama manager instance.

**Parameters:**
- `**client_kwargs`: Arguments for OllamaClient if creating new instance

**Returns:** `OllamaManager` - Default OllamaManager instance

```python
def generate_with_ollama(
    prompt: str,
    model: Optional[str] = None,
    options: Optional[dict] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> str
```

Convenience function for simple text generation with Ollama.

**Parameters:**
- `prompt` (str): Input prompt for text generation
- `model` (Optional[str]): Model to use. If None, uses config default
- `options` (Optional[dict]): Generation options (temperature, top_p, etc.)
- `base_url` (Optional[str]): Ollama server URL. If None, uses config default
- `timeout` (Optional[int]): Request timeout. If None, uses config default

**Returns:** `str` - Generated text response

```python
def chat_with_ollama(
    messages: list[dict[str, str]],
    model: Optional[str] = None,
    options: Optional[dict] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> dict[str, Any]
```

Convenience function for chat-style interactions with Ollama.

**Parameters:**
- `messages` (list[dict[str, str]]): List of chat messages with 'role' and 'content'
- `model` (Optional[str]): Model to use. If None, uses config default
- `options` (Optional[dict]): Generation options
- `base_url` (Optional[str]): Ollama server URL. If None, uses config default
- `timeout` (Optional[int]): Request timeout. If None, uses config default

**Returns:** `dict[str, Any]` - Chat response with message and metadata

```python
def stream_with_ollama(
    prompt: str,
    model: Optional[str] = None,
    options: Optional[dict] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> Iterator[str]
```

Streaming text generation with Ollama.

**Parameters:**
- `prompt` (str): Input prompt for text generation
- `model` (Optional[str]): Model to use. If None, uses config default
- `options` (Optional[dict]): Generation options
- `base_url` (Optional[str]): Ollama server URL. If None, uses config default
- `timeout` (Optional[int]): Request timeout. If None, uses config default

**Returns:** `Iterator[str]` - Iterator yielding text chunks as they are generated

```python
def stream_chat_with_ollama(
    messages: list[dict[str, str]],
    model: Optional[str] = None,
    options: Optional[dict] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> Iterator[dict[str, Any]]
```

Streaming chat interactions with Ollama.

**Parameters:**
- `messages` (list[dict[str, str]]): List of chat messages
- `model` (Optional[str]): Model to use. If None, uses config default
- `options` (Optional[dict]): Generation options
- `base_url` (Optional[str]): Ollama server URL. If None, uses config default
- `timeout` (Optional[int]): Request timeout. If None, uses config default

**Returns:** `Iterator[dict[str, Any]]` - Iterator yielding response chunks

```python
def check_ollama_availability(
    base_url: Optional[str] = None,
    timeout: int = 5,
) -> dict[str, Any]
```

Check if Ollama service is available and responsive.

**Parameters:**
- `base_url` (Optional[str]): Ollama server URL. If None, uses config default
- `timeout` (int): Connection timeout in seconds. Defaults to 5

**Returns:** `dict[str, Any]` - Availability status with version and model information

```python
def get_available_models(
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> list[dict[str, Any]]
```

Get list of available models from Ollama server.

**Parameters:**
- `base_url` (Optional[str]): Ollama server URL. If None, uses config default
- `timeout` (Optional[int]): Request timeout. If None, uses config default

**Returns:** `list[dict[str, Any]]` - List of available models with metadata

```python
def create_chat_messages(
    system_message: Optional[str] = None,
    user_message: str = "",
    assistant_message: Optional[str] = None,
) -> list[dict[str, str]]
```

Create properly formatted chat messages for Ollama.

**Parameters:**
- `system_message` (Optional[str]): System/instruction message
- `user_message` (str): User message content. Defaults to ""
- `assistant_message` (Optional[str]): Assistant message content

**Returns:** `list[dict[str, str]]` - Formatted message list for chat API

### Configuration Functions

```python
def get_config() -> LLMConfig
```

Get current LLM configuration.

**Returns:** `LLMConfig` - Current configuration object

```python
def set_config(config: LLMConfig) -> None
```

Set LLM configuration.

**Parameters:**
- `config` (LLMConfig): New configuration object

**Returns:** None

```python
def reset_config() -> None
```

Reset LLM configuration to defaults.

**Returns:** None

## Data Structures

### OllamaManager
```python
class OllamaManager:
    def __init__(self, model: str = None, base_url: str = None, timeout: int = None)

    def generate(self, prompt: str, **kwargs) -> str
    def chat(self, messages: list[dict[str, str]], **kwargs) -> dict[str, Any]
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]
    def stream_chat(self, messages: list[dict[str, str]], **kwargs) -> Iterator[dict[str, Any]]
    def list_models(self) -> list[dict[str, Any]]
    def check_health(self) -> dict[str, Any]
    def pull_model(self, model_name: str) -> bool
    def delete_model(self, model_name: str) -> bool
```

Main manager class for Ollama interactions.

### OllamaClient
```python
class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 120)

    def generate(self, model: str, prompt: str, **kwargs) -> dict[str, Any]
    def chat(self, model: str, messages: list[dict[str, str]], **kwargs) -> dict[str, Any]
    def list_models(self) -> dict[str, Any]
    def pull_model(self, model_name: str) -> dict[str, Any]
    def delete_model(self, model_name: str) -> dict[str, Any]
    def show_model(self, model_name: str) -> dict[str, Any]
```

Low-level client for Ollama API interactions.

### LLMConfig
```python
class LLMConfig:
    model: str = "llama2"
    base_url: str = "http://localhost:11434"
    timeout: int = 120
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    stream: bool = False
```

Configuration class for LLM settings.

### Exception Classes

```python
class OllamaError(Exception):
    """Base exception for Ollama-related errors."""

class OllamaConnectionError(OllamaError):
    """Exception raised when connection to Ollama fails."""

class OllamaModelError(OllamaError):
    """Exception raised when model operations fail."""

class OllamaTimeoutError(OllamaError):
    """Exception raised when requests timeout."""
```

Custom exception classes for error handling.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `ollama_integration.py` – Ollama local LLM integration
- `ollama_client.py` – Ollama client utilities
- `config.py` – Configuration management

### Configuration
- `config.example.json` – Example configuration file
- `COMPREHENSIVE_REPORT.md` – Comprehensive usage and performance reports

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `SECURITY.md` – Security considerations for LLM usage

### Outputs and Data
- `outputs/` – Generated outputs and analysis results

### Supporting Files
- `requirements.txt` – Module dependencies (ollama, openai, etc.)
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Language Model Protocols

All language model interactions within the Codomyrmex platform must:

1. **Provider Agnostic** - Code works with any supported LLM provider
2. **Cost Aware** - Track and optimize API usage costs
3. **Security Conscious** - Never expose API keys or sensitive prompts
4. **Error Resilient** - Handle API failures and rate limits gracefully
5. **Performance Optimized** - Cache responses and minimize redundant calls

### Module-Specific Guidelines

#### Provider Management
- Support multiple providers with unified configuration
- Implement automatic fallback to alternative providers
- Handle provider-specific authentication and rate limits
- Monitor provider performance and reliability

#### Model Selection
- Provide clear guidelines for model selection based on use case
- Support model versioning and updates
- Include model performance benchmarking
- Document model capabilities and limitations

#### API Usage
- Implement proper error handling for API failures
- Support streaming responses for interactions
- Include usage logging and cost tracking
- Handle rate limiting and quota management

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations
- **Comprehensive Report**: [COMPREHENSIVE_REPORT.md](COMPREHENSIVE_REPORT.md) - Detailed analysis reports

### Related Modules

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Model Requirements** - Coordinate model capabilities with module needs
2. **Cost Management** - Share API usage costs across platform components
3. **Performance Optimization** - Optimize model calls for overall platform performance
4. **Fallback Coordination** - Ensure consistent fallback behavior across modules

### Quality Gates

Before language model changes are accepted:

1. **Multi-Provider Tested** - Works with all supported LLM providers
2. **Cost Tracking Verified** - Accurate usage and cost reporting
3. **Security Validated** - No credential exposure or prompt leakage
4. **Error Handling Complete** - Robust handling of API failures and edge cases
5. **Performance Optimized** - Efficient API usage and response caching

## Version History

- **v0.1.0** (December 2025) - Initial language model infrastructure with multi-provider support and benchmarking

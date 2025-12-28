# Codomyrmex Agents — src/codomyrmex/ai_code_editing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing AI-powered code assistance and generation capabilities for the Codomyrmex platform. This module enables intelligent code creation, refactoring, and enhancement through integration with multiple Large Language Models (LLMs) including OpenAI, Anthropic, and Google AI.

The ai_code_editing module serves as the primary interface for AI-driven development workflows, supporting both programmatic usage and interactive development assistance.

## Module Overview

### Key Capabilities
- **Code Generation**: Create code snippets from natural language descriptions
- **Code Refactoring**: Improve and optimize existing code with AI assistance
- **Multi-Provider Support**: Integration with OpenAI, Anthropic (Claude), and Google AI
- **Prompt Engineering**: Sophisticated prompt composition and template management
- **Context-Aware Generation**: Support for additional context and constraints
- **Performance Monitoring**: Execution time and token usage tracking

### Key Features
- Multiple LLM provider support with unified interface
- Configurable model selection and parameters
- Prompt templates for consistent code generation
- Error handling and fallback mechanisms
- Structured response format with metadata
- Integration with droid task management system

## Function Signatures

### Core Code Generation Functions

```python
def get_llm_client(provider: str, model_name: Optional[str] = None) -> tuple[Any, str]
```

Initialize and return an LLM client based on the specified provider.

**Parameters:**
- `provider` (str): The LLM provider to use (e.g., "openai", "anthropic", "google")
- `model_name` (Optional[str]): Optional specific model to use

**Returns:** `tuple[Any, str]` - Tuple of (client, model_name) ready for requests

**Raises:**
- `ImportError`: If the required client library is not installed
- `ValueError`: If the provider is not supported or configuration is invalid

```python
def generate_code_snippet(
    prompt: str,
    language: str,
    provider: str = "openai",
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    max_length: Optional[int] = None,
    temperature: float = 0.7,
    **kwargs
) -> dict[str, Any]
```

Generate a code snippet using an LLM.

**Parameters:**
- `prompt` (str): The prompt describing what code to generate
- `language` (str): Programming language for the generated code
- `provider` (str): LLM provider to use ("openai", "anthropic", "google")
- `model_name` (Optional[str]): Specific model to use (optional)
- `context` (Optional[str]): Additional context for the generation
- `max_length` (Optional[int]): Maximum length of generated code
- `temperature` (float): Sampling temperature (0.0 to 1.0)
- `**kwargs`: Additional parameters for the LLM

**Returns:** `dict[str, Any]` - Dictionary containing generated code and metadata

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If code generation fails

```python
def refactor_code_snippet(
    code: str,
    refactoring_type: str,
    language: str,
    provider: str = "openai",
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    preserve_functionality: bool = True,
    **kwargs
) -> dict[str, Any]
```

Refactor existing code using an LLM.

**Parameters:**
- `code` (str): The code to refactor
- `refactoring_type` (str): Type of refactoring ("optimize", "simplify", "add_error_handling")
- `language` (str): Programming language of the code
- `provider` (str): LLM provider to use
- `model_name` (Optional[str]): Specific model to use (optional)
- `context` (Optional[str]): Additional context for refactoring
- `preserve_functionality` (bool): Whether to preserve original functionality
- `**kwargs`: Additional parameters for the LLM

**Returns:** `dict[str, Any]` - Dictionary containing refactored code and metadata

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If refactoring fails

```python
def analyze_code_quality(
    code: str,
    language: str,
    analysis_type: str = "comprehensive",
    provider: str = "openai",
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    **kwargs
) -> dict[str, Any]
```

Analyze code quality using an LLM.

**Parameters:**
- `code` (str): The code to analyze
- `language` (str): Programming language of the code
- `analysis_type` (str): Type of analysis ("comprehensive", "security", "performance", "maintainability")
- `provider` (str): LLM provider to use
- `model_name` (Optional[str]): Specific model to use (optional)
- `context` (Optional[str]): Additional context for analysis
- `**kwargs`: Additional parameters for the LLM

**Returns:** `dict[str, Any]` - Dictionary containing analysis results and suggestions

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If analysis fails

### Batch and Comparison Functions

```python
def generate_code_batch(
    requests: list[CodeGenerationRequest],
    provider: str = "openai",
    model_name: Optional[str] = None,
    parallel: bool = False,
    max_workers: int = 4,
    **kwargs
) -> list[CodeGenerationResult]
```

Generate multiple code snippets in batch.

**Parameters:**
- `requests` (list[CodeGenerationRequest]): List of code generation requests
- `provider` (str): LLM provider to use
- `model_name` (Optional[str]): Specific model to use (optional)
- `parallel` (bool): Whether to process requests in parallel
- `max_workers` (int): Maximum number of parallel workers (default: 4)
- `**kwargs`: Additional parameters for the LLM

**Returns:** `list[CodeGenerationResult]` - List of code generation results

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If batch generation fails

```python
def compare_code_versions(
    code1: str,
    code2: str,
    language: str,
    provider: str = "openai",
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    **kwargs
) -> dict[str, Any]
```

Compare two versions of code and provide analysis.

**Parameters:**
- `code1` (str): First version of code
- `code2` (str): Second version of code
- `language` (str): Programming language of the code
- `provider` (str): LLM provider to use
- `model_name` (Optional[str]): Specific model to use (optional)
- `context` (Optional[str]): Additional context for comparison
- `**kwargs`: Additional parameters for the LLM

**Returns:** `dict[str, Any]` - Dictionary containing comparison analysis

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If comparison fails

```python
def generate_code_documentation(
    code: str,
    language: str,
    doc_type: str = "comprehensive",
    provider: str = "openai",
    model_name: Optional[str] = None,
    context: Optional[str] = None,
    **kwargs
) -> dict[str, Any]
```

Generate documentation for code using an LLM.

**Parameters:**
- `code` (str): The code to document
- `language` (str): Programming language of the code
- `doc_type` (str): Type of documentation ("comprehensive", "api", "inline", "readme")
- `provider` (str): LLM provider to use
- `model_name` (Optional[str]): Specific model to use (optional)
- `context` (Optional[str]): Additional context for documentation
- `**kwargs`: Additional parameters for the LLM

**Returns:** `dict[str, Any]` - Dictionary containing generated documentation

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If documentation generation fails

### Utility Functions

```python
def get_supported_languages() -> list[CodeLanguage]
```

Get list of supported programming languages.

**Returns:** `list[CodeLanguage]` - List of supported programming languages

```python
def get_supported_providers() -> list[str]
```

Get list of supported LLM providers.

**Returns:** `list[str]` - List of supported LLM provider names ("openai", "anthropic", "google")

```python
def get_available_models(provider: str) -> list[str]
```

Get list of available models for a provider.

**Parameters:**
- `provider` (str): Provider name

**Returns:** `list[str]` - List of available model names for the provider

```python
def validate_api_keys() -> dict[str, bool]
```

Validate API keys for all supported providers.

**Returns:** `dict[str, bool]` - Dictionary mapping provider names to API key availability status

```python
def setup_environment() -> bool
```

Setup environment variables and check dependencies.

**Returns:** `bool` - True if setup successful and at least one provider is available, False otherwise

### Data Structures

```python
class CodeLanguage(Enum)
```

Supported programming languages.

**Members:**
- `PYTHON`, `JAVASCRIPT`, `TYPESCRIPT`, `JAVA`, `CPP`, `CSHARP`, `GO`, `RUST`, `PHP`, `RUBY`, `SWIFT`, `KOTLIN`, `SCALA`, `R`, `MATLAB`, `SHELL`, `SQL`, `HTML`, `CSS`, `XML`, `YAML`, `JSON`, `MARKDOWN`

```python
class CodeComplexity(Enum)
```

Code complexity levels.

**Members:**
- `SIMPLE`, `INTERMEDIATE`, `COMPLEX`, `EXPERT`

```python
class CodeStyle(Enum)
```

Code style preferences.

**Members:**
- `CLEAN`, `VERBOSE`, `CONCISE`, `FUNCTIONAL`, `OBJECT_ORIENTED`, `PROCEDURAL`

```python
@dataclass
class CodeGenerationRequest
```

Request structure for code generation.

**Fields:**
- `prompt` (str): Natural language description
- `language` (CodeLanguage): Target programming language
- `complexity` (CodeComplexity): Code complexity level (default: INTERMEDIATE)
- `style` (CodeStyle): Code style preference (default: CLEAN)
- `context` (Optional[str]): Additional context
- `requirements` (Optional[list[str]]): Specific requirements
- `examples` (Optional[list[str]]): Example code patterns
- `max_length` (Optional[int]): Maximum code length
- `temperature` (float): Sampling temperature (default: 0.7)

```python
@dataclass
class CodeRefactoringRequest
```

Request structure for code refactoring.

**Fields:**
- `code` (str): Source code to refactor
- `language` (CodeLanguage): Programming language
- `refactoring_type` (str): Refactoring instruction
- `context` (Optional[str]): Additional context
- `preserve_functionality` (bool): Whether to preserve behavior (default: True)
- `add_tests` (bool): Whether to add tests (default: False)
- `add_documentation` (bool): Whether to add documentation (default: False)

```python
@dataclass
class CodeAnalysisRequest
```

Request structure for code analysis.

**Fields:**
- `code` (str): Code to analyze
- `language` (CodeLanguage): Programming language
- `analysis_type` (str): Analysis type ("quality", "security", "performance", "maintainability")
- `context` (Optional[str]): Additional context
- `include_suggestions` (bool): Whether to include improvement suggestions (default: True)

```python
@dataclass
class CodeGenerationResult
```

Result structure for code generation.

**Fields:**
- `generated_code` (str): The generated code
- `language` (CodeLanguage): Programming language
- `metadata` (dict[str, Any]): Additional metadata
- `execution_time` (float): Time taken for generation
- `tokens_used` (Optional[int]): Tokens consumed
- `confidence_score` (Optional[float]): Confidence in generation quality

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `ai_code_helpers.py` – Core AI code assistance utilities
- `prompt_composition.py` – Prompt engineering and composition logic
- `droid_manager.py` – Task management and orchestration

### Provider Integrations
- `openai_codex.py` – OpenAI API integration
- `claude_task_master.py` – Anthropic Claude integration

### Supporting Systems
- `droid/` – Task execution and management system
- `prompt_templates/` – Reusable prompt templates and patterns

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `PROMPT_ENGINEERING.md` – Prompt design and optimization
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for AI usage
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal AI Code Protocols

All AI code assistance within the Codomyrmex platform must:

1. **Provider Agnostic** - Code should work with any supported LLM provider
2. **Secure API Usage** - Never expose API keys or sensitive credentials
3. **Context Preservation** - Maintain code functionality and intent during refactoring
4. **Error Resilience** - Handle API failures and rate limits gracefully
5. **Usage Transparency** - Track and report token usage and costs

### Module-Specific Guidelines

#### Code Generation
- Provide clear, descriptive prompts for better results
- Specify programming language explicitly
- Include context when available to improve accuracy
- Validate generated code for syntax and logic errors

#### Code Refactoring
- Preserve existing functionality unless explicitly requested otherwise
- Provide specific refactoring goals (optimize, simplify, add error handling)
- Include sufficient context about the codebase
- Review AI suggestions for correctness and best practices

#### Provider Management
- Support fallback to alternative providers on failure
- Implement rate limiting and usage monitoring
- Cache responses when appropriate for performance
- Handle provider-specific parameter differences

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations
- **Prompt Engineering**: [PROMPT_ENGINEERING.md](PROMPT_ENGINEERING.md) - Prompt design guide

### Related Modules

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Model Management** - Coordinate with language_models module for provider management
2. **Context Sharing** - Exchange codebase context for improved AI assistance
3. **Code Review Integration** - Combine AI generation with automated code review
4. **Security Validation** - Ensure AI-generated code meets security standards

### Quality Gates

Before AI code changes are accepted:

1. **API Integration Tested** - All supported providers properly tested
2. **Prompt Quality Verified** - Prompts produce consistent, high-quality results
3. **Security Validated** - No security vulnerabilities in generated code
4. **Performance Optimized** - API calls and response processing efficient
5. **Error Handling Complete** - Robust handling of API failures and edge cases

## Version History

- **v0.1.0** (December 2025) - Initial AI code editing system with multi-provider support and prompt engineering

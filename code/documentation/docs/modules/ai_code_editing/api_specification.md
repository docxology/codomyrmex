---
id: ai-code-editing-api-specification
title: AI Code Editing - API Specification
sidebar_label: API Specification
---

# Ai Code Editing - API Specification

## Introduction

This document outlines the Application Programming Interfaces (APIs) provided by the AI Code Editing module. These APIs facilitate interaction with the module's core functionalities, such as requesting code suggestions, explanations, or transformations.

## Core Functions

### `generate_code_snippet(prompt, language, context_code=None, llm_provider="openai", model_name=None)`

Generates code snippets using AI/LLM based on natural language prompts.

#### Parameters
- **`prompt`** (string, required): Natural language description of the code to generate
- **`language`** (string, required): Target programming language ("python", "javascript", "java", etc.)
- **`context_code`** (string, optional): Existing code snippet for context
- **`llm_provider`** (string, optional): LLM provider ("openai", "anthropic", "google") - defaults to "openai"
- **`model_name`** (string, optional): Specific model name to use

#### Returns
```python
{
    "status": "success",  # or "failure"
    "generated_code": "def hello():\n    print('Hello, World!')",
    "error_message": None  # or error description if status is "failure"
}
```

#### Example Usage
```python
from codomyrmex.ai_code_editing import generate_code_snippet

result = generate_code_snippet(
    prompt="Create a function to calculate Fibonacci numbers",
    language="python",
    context_code="def factorial(n):\n    return n * factorial(n-1) if n > 1 else 1"
)

if result["status"] == "success":
    print(result["generated_code"])
```

#### Error Handling
- **ValueError**: If required parameters are missing or invalid
- **ImportError**: If specified LLM provider is not available
- **API Error**: If LLM API request fails (network, rate limit, etc.)

**Related Functions:**
- [`refactor_code_snippet()`](#refactor_code_snippet) - For code refactoring
- [`validate_language()` in code_execution_sandbox](../code_execution_sandbox/api_specification.md) - Language validation

---

### `refactor_code_snippet(code_snippet, refactoring_instruction, language, llm_provider="openai", model_name=None)`

Refactors existing code based on natural language instructions.

#### Parameters
- **`code_snippet`** (string, required): The code to refactor
- **`refactoring_instruction`** (string, required): Description of desired refactoring
- **`language`** (string, required): Programming language of the code
- **`llm_provider`** (string, optional): LLM provider - defaults to "openai"
- **`model_name`** (string, optional): Specific model name to use

#### Returns
```python
{
    "status": "success",        # "success", "no_change_needed", or "failure"
    "refactored_code": "def calculate_sum(numbers: list) -> int:\n    return sum(numbers)",
    "explanation": "Added type hints for better code quality",
    "error_message": None       # or error description if status is "failure"
}
```

#### Example Usage
```python
from codomyrmex.ai_code_editing import refactor_code_snippet

original_code = "def calculate_sum(numbers):\n    return sum(numbers)"
result = refactor_code_snippet(
    code_snippet=original_code,
    refactoring_instruction="Add type hints and improve readability",
    language="python"
)

if result["status"] == "success":
    print("Refactored code:")
    print(result["refactored_code"])
    print(f"Explanation: {result['explanation']}")
```

#### Status Values
- **`"success"`**: Code was successfully refactored
- **`"no_change_needed"`**: Code is already optimal, no changes made
- **`"failure"`**: Refactoring failed (see `error_message`)

**Related Functions:**
- [`generate_code_snippet()`](#generate_code_snippet) - For code generation
- [`execute_code()` in code_execution_sandbox](../code_execution_sandbox/api_specification.md) - Test refactored code

---

## Integration Points

### Model Context Protocol (MCP) Tools

The AI Code Editing module exposes the following MCP tools:

#### `ai_code_editing.generate_code_snippet`
- **Description**: MCP-compatible version of `generate_code_snippet()`
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "prompt": {"type": "string", "description": "Code generation prompt"},
      "language": {"type": "string", "description": "Programming language"},
      "context_code": {"type": "string", "description": "Optional context code"},
      "llm_provider": {"type": "string", "description": "LLM provider"},
      "model_name": {"type": "string", "description": "Specific model name"}
    },
    "required": ["prompt", "language"]
  }
  ```

#### `ai_code_editing.refactor_code_snippet`
- **Description**: MCP-compatible version of `refactor_code_snippet()`
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "code_snippet": {"type": "string", "description": "Code to refactor"},
      "refactoring_instruction": {"type": "string", "description": "Refactoring instructions"},
      "language": {"type": "string", "description": "Programming language"},
      "llm_provider": {"type": "string", "description": "LLM provider"},
      "model_name": {"type": "string", "description": "Specific model name"}
    },
    "required": ["code_snippet", "refactoring_instruction", "language"]
  }
  ```

### Dependencies

#### Required
- **`cased/kit`**: For advanced LLM interactions and code analysis
- **`openai`**: OpenAI API client
- **`anthropic`**: Anthropic API client (optional)
- **`python-dotenv`**: Environment variable management

#### Related Modules
- [**`environment_setup`**](../environment_setup/api_specification.md): API key management
- [**`logging_monitoring`**](../logging_monitoring/api_specification.md): Logging infrastructure
- [**`model_context_protocol`**](../model_context_protocol/api_specification.md): MCP protocol
- [**`code_execution_sandbox`**](../code_execution_sandbox/api_specification.md): Code testing

---

## Configuration

### Environment Variables
```bash
# Required for OpenAI
OPENAI_API_KEY="sk-your-openai-key"

# Optional for Anthropic
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"

# Optional for Google
GOOGLE_API_KEY="your-google-api-key"

# Module configuration
AI_CODE_EDITING_DEFAULT_PROVIDER="openai"
AI_CODE_EDITING_GENERATION_MODEL="gpt-3.5-turbo"
AI_CODE_EDITING_REFACTOR_MODEL="gpt-4"
```

### Default Models
- **Code Generation**: `gpt-3.5-turbo` (faster, cost-effective)
- **Code Refactoring**: `gpt-4` (higher quality for complex refactoring)

---

## Error Handling

### Common Error Scenarios

#### LLM API Errors
```python
try:
    result = generate_code_snippet("Create a function", "python")
except ValueError as e:
    # Invalid input parameters
    print(f"Input error: {e}")
except ImportError as e:
    # Missing LLM library
    print(f"Missing dependency: {e}")
except Exception as e:
    # API errors, network issues, etc.
    print(f"API error: {e}")
```

#### Rate Limiting
```python
import time
from codomyrmex.ai_code_editing import generate_code_snippet

def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return generate_code_snippet(prompt, "python")
        except Exception as e:
            if "rate limit" in str(e).lower():
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

---

## Best Practices

### 1. Prompt Engineering
```python
# Good prompt
good_prompt = """
Create a Python function that validates email addresses.

Requirements:
- Use regular expressions
- Handle edge cases (empty string, invalid formats)
- Return boolean result
- Include type hints
- Add docstring with examples
"""

# Less effective prompt
bad_prompt = "Make an email checker"
```

### 2. Context Provision
```python
# Provide relevant context for better results
context_code = """
def validate_username(username: str) -> bool:
    return len(username) >= 3 and username.isalnum()
"""

result = generate_code_snippet(
    prompt="Create a similar validation function for email addresses",
    language="python",
    context_code=context_code  # Helps LLM understand coding patterns
)
```

### 3. Error Handling
```python
def safe_generate_code(prompt, language, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = generate_code_snippet(prompt, language)
            if result["status"] == "success":
                return result["generated_code"]
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)

    raise RuntimeError("Failed to generate code after all retries")
```

### 4. Model Selection
```python
# Use GPT-3.5 for simple tasks
simple_result = generate_code_snippet(
    "Create a hello world function",
    "python",
    model_name="gpt-3.5-turbo"
)

# Use GPT-4 for complex tasks
complex_result = generate_code_snippet(
    "Implement a complex algorithm with optimizations",
    "python",
    model_name="gpt-4"
)
```

---

## Performance Considerations

### Response Times
- **GPT-3.5-turbo**: ~5-15 seconds for typical code generation
- **GPT-4**: ~10-30 seconds for complex tasks
- **Anthropic Claude**: ~10-25 seconds depending on model

### Cost Optimization
```python
# Cache similar requests
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generate_code(prompt_hash, language):
    # Implement caching logic
    pass

# Use smaller models for simple tasks
def smart_generate_code(prompt, language):
    if len(prompt.split()) < 10:
        model = "gpt-3.5-turbo"  # Cheaper for simple tasks
    else:
        model = "gpt-4"  # Better for complex tasks

    return generate_code_snippet(prompt, language, model_name=model)
```

---

## See Also

- [**Module Relationship Guide**](../../../../../MODULE_RELATIONSHIPS.md) - How AI Code Editing integrates with other modules
- [**Environment Setup Guide**](../environment_setup/docs/technical_overview.md) - API key configuration
- [**MCP Protocol Guide**](../model_context_protocol/docs/technical_overview.md) - Model Context Protocol details
- [**Testing Strategy**](../../project/TESTING_STRATEGY.md) - Module testing approach
- [**Troubleshooting Guide**](../../../../../TROUBLESHOOTING.md) - Common issues and solutions 
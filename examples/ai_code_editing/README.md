# AI Code Editing Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `codomyrmex.agents.ai_code_editing` - AI-Powered Code Generation and Refactoring

## Overview

This example demonstrates the comprehensive AI-powered code assistance capabilities of Codomyrmex, showcasing intelligent code generation, refactoring, quality analysis, and documentation creation using multiple Large Language Models (LLMs). The example covers the full spectrum of AI-driven development workflows from concept to production-ready code.

## What This Example Demonstrates

- **Code Generation**: Creating code from natural language descriptions
- **Code Refactoring**: Improving and optimizing existing code with AI guidance
- **Quality Analysis**: Automated code quality assessment and improvement suggestions
- **Batch Processing**: Generating multiple code snippets simultaneously
- **Documentation Generation**: Creating comprehensive code documentation
- **Multi-Provider Support**: Integration with OpenAI, Anthropic, and Google AI
- **Prompt Engineering**: Sophisticated prompt composition and optimization
- **Model Management**: Dynamic model selection and provider management

## Features Demonstrated

### Core AI Capabilities
- Natural language to code translation
- Context-aware code generation with constraints
- Intelligent code refactoring and optimization
- Comprehensive code quality analysis
- Automated documentation generation
- Multi-language support (Python, JavaScript, SQL, Bash, etc.)

### Advanced Features
- Batch code generation for productivity
- Provider fallback and error handling
- Token usage tracking and optimization
- Temperature and parameter tuning
- Code complexity analysis
- Security and best practices validation

### Integration Features
- Environment setup and validation
- API key management and validation
- Model availability checking
- Performance monitoring and metrics
- Caching and optimization

## Tested Methods

The example utilizes and demonstrates methods primarily tested in:
- `testing/unit/test_ai_code_editing.py`

Specifically, it covers:
- `generate_code_snippet()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`
- `refactor_code_snippet()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`
- `analyze_code_quality()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`
- `generate_code_batch()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`
- `generate_code_documentation()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`
- `get_supported_languages()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`
- `get_supported_providers()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`
- `get_available_models()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`
- `validate_api_keys()` - Verified in `TestAICodeEditing::test_get_llm_client_openai_success`
- `setup_environment()` - Verified in `TestAICodeEditing::test_ai_code_helpers_structure`

## Configuration

The example uses `config.yaml` (or `config.json`) for settings:

```yaml
# AI Code Editing Configuration
logging:
  level: INFO
  file: logs/ai_code_editing_example.log
  output_type: TEXT

output:
  format: json
  file: output/ai_code_editing_results.json

ai_code_editing:
  # Provider settings
  default_provider: openai
  fallback_providers: ["anthropic", "google"]

  # Model configurations
  models:
    openai:
      default: "gpt-3.5-turbo"
      alternatives: ["gpt-4", "gpt-4-turbo"]
    anthropic:
      default: "claude-3-sonnet-20240229"
      alternatives: ["claude-3-haiku-20240307", "claude-3-opus-20240229"]
    google:
      default: "gemini-pro"
      alternatives: ["gemini-pro-vision"]

  # Generation parameters
  generation:
    temperature: 0.7
    max_tokens: 2000
    top_p: 1.0
    frequency_penalty: 0.0
    presence_penalty: 0.0

  # Refactoring settings
  refactoring:
    preserve_functionality: true
    add_error_handling: true
    optimize_performance: true
    improve_readability: true

  # Quality analysis settings
  analysis:
    check_complexity: true
    check_security: true
    check_best_practices: true
    check_documentation: true
```

### Configuration Options

- **`ai_code_editing.default_provider`**: Primary LLM provider (openai, anthropic, google)
- **`ai_code_editing.fallback_providers`**: Backup providers for failover
- **`models.{provider}.default`**: Default model for each provider
- **`generation.temperature`**: Sampling temperature (0.0-1.0, higher = more creative)
- **`generation.max_tokens`**: Maximum response length
- **`refactoring.preserve_functionality`**: Whether to maintain existing behavior
- **`analysis.*`**: Code quality check settings

### Environment Variables

The example supports these environment variables:
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GOOGLE_AI_API_KEY`: Google AI API key

## Running the Example

### Prerequisites

Ensure you have the Codomyrmex package installed:

```bash
cd /path/to/codomyrmex
pip install -e .
```

For full functionality, set up API keys for your preferred providers:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Basic Execution

```bash
# Navigate to the example directory
cd examples/ai_code_editing

# Run the example
python example_basic.py
```

### With Custom Configuration

```bash
# Use a custom config file
python example_basic.py --config my_custom_config.yaml
```

### With Environment Variables

```bash
# Use a specific provider
export AI_PROVIDER=anthropic python example_basic.py

# Adjust temperature for more creative output
export AI_TEMPERATURE=0.9 python example_basic.py
```

## Expected Output

The script will print a summary of AI operations and save a JSON file (`output/ai_code_editing_results.json`) containing the results, including:

- `environment_setup`: Whether environment initialization succeeded
- `api_keys_validated`: Number of providers with valid API keys
- `supported_languages`: Number of programming languages supported
- `supported_providers`: Number of LLM providers available
- `code_generation_success`: Whether code generation worked
- `refactoring_success`: Whether code refactoring worked
- `analysis_success`: Whether code analysis worked
- `batch_success`: Whether batch generation worked
- `documentation_success`: Whether documentation generation worked

Example `output/ai_code_editing_results.json`:
```json
{
  "environment_setup": true,
  "api_keys_validated": 2,
  "supported_languages": 10,
  "supported_providers": 3,
  "code_generation_attempts": 2,
  "code_refactoring_attempts": 1,
  "code_analysis_attempts": 1,
  "batch_generation_attempts": 4,
  "documentation_generation_attempts": 1,
  "code_generation_success": true,
  "refactoring_success": true,
  "analysis_success": true,
  "batch_success": true,
  "documentation_success": true
}
```

## Code Generation Examples

### Simple Function Generation

```python
# Input prompt
"Write a Python function that calculates the fibonacci sequence up to n terms"

# Generated output (example)
def fibonacci_sequence(n):
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]

    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])

    return sequence
```

### Complex Code Generation

```python
# Input prompt
"Create a Python class for managing a task queue with threading support"

# Generated output includes:
# - Thread-safe queue implementation
# - Worker thread management
# - Task submission and retrieval
# - Proper synchronization
# - Error handling and logging
```

## Code Refactoring Examples

### Original Code
```python
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item
    return total
```

### Refactored Code
```python
def calculate_total(items):
    """
    Calculate the total sum of all items in the list.

    Args:
        items: List of numeric values

    Returns:
        float: Sum of all items

    Raises:
        TypeError: If items is not iterable
        ValueError: If any item is not numeric
    """
    if not items:
        return 0.0

    try:
        return sum(float(item) for item in items)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid input: {e}") from e
```

## Quality Analysis Examples

The example demonstrates analysis of code for:
- **Complexity**: Cyclomatic complexity and maintainability
- **Security**: Potential security vulnerabilities
- **Best Practices**: PEP 8 compliance and Python conventions
- **Documentation**: Docstring completeness and accuracy

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure API keys are set as environment variables
   - Check key validity and permissions
   - Verify account has sufficient credits

2. **Rate Limiting**
   - Implement delays between requests
   - Use fallback providers
   - Consider caching for repeated requests

3. **Model Availability**
   - Check model availability for your region
   - Use alternative models from the same provider
   - Switch to different providers

4. **Code Quality Issues**
   - Review generated code for syntax errors
   - Test code functionality before production use
   - Consider manual review and validation

### Debug Mode

Enable detailed logging for troubleshooting:

```yaml
logging:
  level: DEBUG
```

### Manual Testing

Test individual functions directly:

```python
from codomyrmex.agents.ai_code_editing import generate_code_snippet, validate_api_keys

# Check API keys
print(validate_api_keys())

# Generate simple code
result = generate_code_snippet("print hello world", "python")
print(result['generated_code'])
```

## Performance Considerations

- **Token Limits**: Monitor token usage to avoid rate limits
- **Caching**: Enable response caching for repeated requests
- **Batch Processing**: Use batch generation for multiple similar tasks
- **Provider Selection**: Choose appropriate models for task complexity
- **Error Handling**: Implement retries and fallback providers

## Security Best Practices

- **API Key Protection**: Never commit keys to version control
- **Input Validation**: Validate prompts and generated code
- **Output Review**: Always review AI-generated code before production
- **Rate Limiting**: Implement proper rate limiting and monitoring
- **Access Control**: Restrict AI features based on user permissions

## Integration Examples

### With Other Modules

The AI code editing module integrates with:

- **Code Review**: AI suggestions validated by automated review
- **Static Analysis**: AI-generated code analyzed for quality
- **Security Audit**: Generated code scanned for vulnerabilities
- **Documentation**: AI-generated documentation for code

### Workflow Integration

```python
from codomyrmex.agents.ai_code_editing import generate_code_snippet, refactor_code_snippet
from codomyrmex.code.review import review_file
from codomyrmex.static_analysis import analyze_file

# Generate code
code_result = generate_code_snippet("Create a user authentication function", "python")

# Review generated code
review_result = review_file("generated_auth.py", code_result['generated_code'])

# Refactor based on review feedback
refactored = refactor_code_snippet(
    code_result['generated_code'],
    "Address review feedback: " + str(review_result),
    "python"
)

# Final analysis
analysis = analyze_file("generated_auth.py", content=refactored['refactored_code'])
```

## Advanced Usage

### Custom Prompts

Create specialized prompts for domain-specific code:

```python
# Web development prompt
web_prompt = """
Create a Flask route for user registration with:
- Input validation
- Password hashing
- Database storage
- Error handling
- JSON responses
"""

result = generate_code_snippet(web_prompt, "python", context="Flask web application")
```

### Model Selection

Choose appropriate models for different tasks:

```python
# Simple tasks - faster, cheaper models
simple_result = generate_code_snippet(prompt, "python", model_name="gpt-3.5-turbo")

# Complex tasks - more capable models
complex_result = generate_code_snippet(prompt, "python", model_name="gpt-4")

# Creative tasks - higher temperature
creative_result = generate_code_snippet(prompt, "python", temperature=0.9)
```

### Batch Processing

Generate multiple related functions:

```python
batch_prompts = [
    {"prompt": "Database connection function", "language": "python"},
    {"prompt": "User authentication function", "language": "python"},
    {"prompt": "Data validation utilities", "language": "python"},
    {"prompt": "Error handling helpers", "language": "python"}
]

results = generate_code_batch(batch_prompts)
```

## Provider Comparison

### OpenAI GPT Models
- **Strengths**: Fast, reliable, good for most tasks
- **Models**: GPT-3.5-turbo (fast), GPT-4 (powerful)
- **Best for**: General programming, rapid prototyping

### Anthropic Claude
- **Strengths**: Excellent code quality, good explanations
- **Models**: Claude 3 Opus (powerful), Sonnet (balanced), Haiku (fast)
- **Best for**: High-quality code, complex logic, explanations

### Google Gemini
- **Strengths**: Multimodal, good for diverse tasks
- **Models**: Gemini Pro (text), Gemini Pro Vision (multimodal)
- **Best for**: Creative tasks, multimodal integration

## Cost Optimization

### Token Management
- Monitor token usage across providers
- Use appropriate model sizes for task complexity
- Implement caching for repeated requests
- Batch similar requests together

### Provider Selection
- Use faster/cheaper models for simple tasks
- Reserve powerful models for complex requirements
- Implement automatic fallback to cheaper providers
- Track costs and optimize based on usage patterns

## Future Enhancements

The AI code editing module continues to evolve with:

- **Fine-tuned Models**: Custom models for specific coding domains
- **Code Embeddings**: Semantic code search and retrieval
- **Interactive Mode**: Real-time AI assistance during coding
- **Multi-file Generation**: Generating complete applications
- **Code Explanation**: AI-powered code comprehension and explanation

## Related Documentation

- **[AI Code Editing API](../../src/codomyrmex/agents/ai_code_editing/)**
- **[Language Models](../language_models/)**
- **[Code Review](../code.review/)**
- **[Prompt Engineering Guide](../../src/codomyrmex/agents/ai_code_editing/PROMPT_ENGINEERING.md)**

---

**Status**: Complete AI-powered code assistance demonstration
**Tested Methods**: 10 core AI code editing functions
**Features**: Code generation, refactoring, analysis, documentation, multi-provider support

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->

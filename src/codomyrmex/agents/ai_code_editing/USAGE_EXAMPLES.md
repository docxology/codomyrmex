# AI Code Editing - Usage Examples

This document provides examples of how to use the AI Code Editing module within the Codomyrmex project.

## Prerequisites

1. Ensure you have set up the required environment variables. The module needs API keys for the LLM providers:
   - `OPENAI_API_KEY` for using OpenAI models
   - `ANTHROPIC_API_KEY` for using Anthropic models

2. Install the required dependencies:
   ```bash
   uv sync --extra ai_code_editing
   ```

## Basic Code Generation

### Generate a Simple Python Function

```python
from ai_code_editing import generate_code_snippet

# Generate a simple Python function
result = generate_code_snippet(
    prompt="Create a function that checks if a string is a palindrome",
    language="python"
)

if result["status"] == "success":
    print("Generated code:")
    print(result["generated_code"])
else:
    print(f"Error: {result['error_message']}")
```

### Generate JavaScript Code with Context

```python
from ai_code_editing import generate_code_snippet

# Provide context for more targeted generation
context = """
class DataProcessor {
  // Add the validation method here
}
"""

result = generate_code_snippet(
    prompt="Create a method that validates an email address using regex",
    language="javascript",
    context_code=context
)

if result["status"] == "success":
    print("Generated JavaScript code:")
    print(result["generated_code"])
else:
    print(f"Error: {result['error_message']}")
```

### Generate Code Using a Specific Model

```python
from ai_code_editing import generate_code_snippet

# Using a specific model from Anthropic
result = generate_code_snippet(
    prompt="Write a function to calculate the Fibonacci sequence up to n terms",
    language="python",
    llm_provider="anthropic",
    model_name="claude-2"
)

if result["status"] == "success":
    print("Generated with Claude:")
    print(result["generated_code"])
else:
    print(f"Error: {result['error_message']}")
```

## Code Refactoring

### Refactor for Readability

```python
from ai_code_editing import refactor_code_snippet

# Original code that needs refactoring
original_code = """
def f(x,y):
    z = x+y
    if z>10:return "Big"
    else:return "Small"
"""

result = refactor_code_snippet(
    code_snippet=original_code,
    refactoring_instruction="Improve the readability with better naming and add docstring",
    language="python"
)

if result["status"] == "success":
    print("Original code:")
    print(original_code)
    print("
Refactored code:")
    print(result["refactored_code"])
    print("
Explanation:")
    print(result["explanation"])
else:
    print(f"Error: {result['error_message']}")
```

### Add Type Hints 

```python
from ai_code_editing import refactor_code_snippet

# Original code without type hints
original_code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

result = refactor_code_snippet(
    code_snippet=original_code,
    refactoring_instruction="Add Python type hints and improve error handling",
    language="python"
)

if result["status"] in ["success", "no_change_needed"]:
    print("Refactored with type hints:")
    print(result["refactored_code"])
else:
    print(f"Error: {result['error_message']}")
```

### Convert to Modern JavaScript

```python
from ai_code_editing import refactor_code_snippet

# Legacy JavaScript code
legacy_code = """
function fetchData(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            callback(null, JSON.parse(xhr.responseText));
        } else if (xhr.readyState == 4) {
            callback(new Error('Request failed'), null);
        }
    };
    xhr.send();
}
"""

result = refactor_code_snippet(
    code_snippet=legacy_code,
    refactoring_instruction="Convert to modern JavaScript using async/await and fetch API",
    language="javascript"
)

print("Modernized JavaScript:")
print(result["refactored_code"])
```

## Advanced Usage - Integration in a Workflow

```python
from ai_code_editing import generate_code_snippet, refactor_code_snippet

def complete_coding_task(task_description, language):
    """Generates, refactors, and outputs code for a task."""
    print(f"Task: {task_description}")
    
    # Step 1: Generate initial code
    gen_result = generate_code_snippet(
        prompt=task_description,
        language=language
    )
    
    if gen_result["status"] != "success":
        return f"Failed to generate code: {gen_result['error_message']}"
    
    initial_code = gen_result["generated_code"]
    print("
Initial code generated:")
    print(initial_code)
    
    # Step 2: Refactor for best practices
    refactor_result = refactor_code_snippet(
        code_snippet=initial_code,
        refactoring_instruction=f"Optimize this {language} code following best practices, ensure error handling, and add detailed comments",
        language=language
    )
    
    if refactor_result["status"] not in ["success", "no_change_needed"]:
        return f"Failed to refactor code: {refactor_result['error_message']}"
    
    final_code = refactor_result["refactored_code"]
    print("
Final optimized code:")
    print(final_code)
    
    return final_code

# Example usage
complete_coding_task(
    "Create a function that sorts an array of objects by a specific property",
    "javascript"
)
```

## Common Pitfalls & Troubleshooting

### API Key Configuration Issues

**Issue**: Getting "API key not found" or "Authentication failed" errors.

**Solution**:
```bash
# 1. Check environment variables are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# 2. Verify .env file exists and contains correct keys
cat .env | grep API_KEY

# 3. Restart your Python session after setting environment variables
# 4. Check API key format (should start with 'sk-' for OpenAI)
```

### LLM Response Errors

**Issue**: Getting "LLM service unavailable" or "Rate limit exceeded" errors.

**Solution**:
```python
# Check LLM service status
from ai_code_editing import check_llm_availability

status = check_llm_availability("openai", "gpt-3.5-turbo")
if not status["available"]:
    print(f"Service unavailable: {status['error']}")

# For rate limits, implement exponential backoff
import time
from ai_code_editing import generate_code_snippet

def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = generate_code_snippet(prompt=prompt, language="python")
            if result["status"] == "success":
                return result
        except Exception as e:
            if "rate limit" in str(e).lower():
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    return None
```

### Unexpected Code Generation Results

**Issue**: Generated code doesn't meet requirements or contains errors.

**Solution**:
```python
# 1. Improve prompt specificity
detailed_prompt = """
Create a Python function that:
- Takes a list of integers as input
- Returns only the even numbers
- Includes proper error handling for non-integer inputs
- Has comprehensive docstring with examples
- Follows PEP 8 style guidelines

Function signature: filter_even_numbers(numbers: List[int]) -> List[int]
"""

result = generate_code_snippet(
    prompt=detailed_prompt,
    language="python",
    context_code="from typing import List"
)

# 2. Use refactoring to improve generated code
if result["status"] == "success":
    refactor_result = refactor_code_snippet(
        code_snippet=result["generated_code"],
        refactoring_instruction="Add comprehensive error handling and type hints",
        language="python"
    )
```

### Context Code Issues

**Issue**: Code generation doesn't properly integrate with existing codebase.

**Solution**:
```python
# Provide comprehensive context
context = """
# Existing codebase structure
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, config: Dict[str, any]):
        self.config = config

    def validate_input(self, data: List[Dict]) -> bool:
        '''Validate input data structure'''
        # Implementation here
        pass
"""

result = generate_code_snippet(
    prompt="Add a process_batch method to DataProcessor class that handles multiple data items",
    language="python",
    context_code=context
)
```

### Performance and Timeout Issues

**Issue**: Code generation takes too long or times out.

**Solution**:
```python
# Use simpler prompts for complex tasks
# Break down complex requirements into smaller, focused prompts

# Example: Instead of one complex prompt
complex_prompt = "Create a full web application with authentication, database, and API"

# Use multiple focused prompts
step1 = generate_code_snippet("Create User model class with authentication methods")
step2 = generate_code_snippet("Create database connection and CRUD operations")
step3 = generate_code_snippet("Create REST API endpoints for user management")

# Combine results manually
```

### Language-Specific Issues

**Issue**: Code generation doesn't follow language-specific conventions.

**Solution**:
```python
# Be explicit about language requirements
python_requirements = """
Requirements:
- Use type hints for all function parameters and return values
- Include comprehensive docstrings with Args/Returns/Raises sections
- Follow PEP 8 style guidelines
- Use list/dict comprehensions where appropriate
- Include proper exception handling
- Add logging statements for debugging
"""

result = generate_code_snippet(
    prompt=f"Create a data validation function

{python_requirements}",
    language="python"
)
```

## Integration Examples

### CI/CD Pipeline Integration

```python
# .github/workflows/code-review.yml
name: AI Code Review

on: [pull_request]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run AI Code Review
        run: |
          python -c "
          from ai_code_editing import analyze_code_quality
          import subprocess

          # Get changed files
          result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'],
                                capture_output=True, text=True)
          changed_files = result.stdout.strip().split('
')

          for file_path in changed_files:
              if file_path.endswith('.py'):
                  with open(file_path, 'r') as f:
                      code = f.read()

                  analysis = analyze_code_quality(code, 'python')
                  print(f'Quality score for {file_path}: {analysis.get(\"score\", 0)}/10')
          "
```

### IDE Integration

```python
# VS Code extension integration
import vscode

def provide_ai_completion():
    """Provide AI-powered code completion."""
    # Get current context
    editor = vscode.window.activeTextEditor
    document = editor.document
    position = editor.selection.active

    # Get surrounding code context
    context_start = max(0, position.line - 10)
    context_end = min(document.lineCount, position.line + 10)
    context_lines = []

    for i in range(context_start, context_end):
        context_lines.append(document.lineAt(i).text)

    context = '
'.join(context_lines)

    # Generate completion
    from ai_code_editing import generate_code_snippet

    result = generate_code_snippet(
        prompt=f"Complete this code intelligently: {context}",
        language="python"
    )

    if result["status"] == "success":
        # Insert completion
        editor.edit(edit => {
            edit.insert(position, result["generated_code"])
        })
```

## Best Practices

### Prompt Engineering

1. **Be Specific**: Include exact function signatures, parameter types, and return values
2. **Provide Context**: Include relevant imports, class definitions, and existing patterns
3. **Define Constraints**: Specify language version, framework requirements, and style guidelines
4. **Include Examples**: Show expected input/output formats

### Error Handling

```python
from ai_code_editing import generate_code_snippet, refactor_code_snippet

def safe_code_generation(prompt, language, max_retries=3):
    """Safely generate code with proper error handling."""

    for attempt in range(max_retries):
        try:
            # Generate code
            result = generate_code_snippet(
                prompt=prompt,
                language=language,
                timeout=30  # 30 second timeout
            )

            if result["status"] != "success":
                logger.warning(f"Generation failed: {result.get('error_message', 'Unknown error')}")
                continue

            # Validate generated code
            validation = validate_generated_code(result["generated_code"], language)
            if not validation["valid"]:
                logger.warning(f"Generated code validation failed: {validation['issues']}")
                continue

            # Refactor for quality
            refactor_result = refactor_code_snippet(
                code_snippet=result["generated_code"],
                refactoring_instruction="Add error handling and improve code quality",
                language=language
            )

            if refactor_result["status"] == "success":
                return refactor_result["refactored_code"]

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            continue

    raise Exception(f"Failed to generate code after {max_retries} attempts")
```

### Performance Optimization

1. **Use Appropriate Models**: GPT-4 for complex tasks, GPT-3.5-turbo for simple tasks
2. **Batch Operations**: Generate multiple related functions together
3. **Cache Results**: Store successful generations for similar prompts
4. **Incremental Generation**: Build complex code in stages 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)

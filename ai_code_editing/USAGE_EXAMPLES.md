# AI Code Editing - Usage Examples

This document provides examples of how to use the AI Code Editing module within the Codomyrmex project.

## Prerequisites

1. Ensure you have set up the required environment variables. The module needs API keys for the LLM providers:
   - `OPENAI_API_KEY` for using OpenAI models
   - `ANTHROPIC_API_KEY` for using Anthropic models

2. Install the required dependencies:
   ```bash
   pip install -r ai_code_editing/requirements.txt
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
    print("\nRefactored code:")
    print(result["refactored_code"])
    print("\nExplanation:")
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
    print("\nInitial code generated:")
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
    print("\nFinal optimized code:")
    print(final_code)
    
    return final_code

# Example usage
complete_coding_task(
    "Create a function that sorts an array of objects by a specific property",
    "javascript"
)
```

## Common Pitfalls & Troubleshooting

- **Issue**: <!-- TODO: Describe a common problem users might encounter (e.g., API key not set, LLM error, unexpected output). -->
  - **Solution**: <!-- TODO: Explain how to resolve it (e.g., check .env file, review prompt, consult LLM provider documentation). -->

- **Issue**: <!-- TODO: Add another common issue. -->
  - **Solution**: <!-- TODO: Add solution. --> 
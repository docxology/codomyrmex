---
id: ai-code-editing-usage-examples
title: AI Code Editing - Usage Examples
sidebar_label: Usage Examples
---

# Ai Code Editing - Usage Examples

## Example 1: Generating a Python Function Docstring

(Assuming an MCP tool `ai_code_editing.generate_docstring` or similar API)

**Scenario**: You have a Python function and want to use the AI to generate its docstring.

**Input Code (`example.py`):**
```python
def calculate_sum(a, b):
    return a + b
```

**Invocation (conceptual MCP call):**
```json
{
  "tool_name": "ai_code_editing.generate_docstring",
  "arguments": {
    "file_path": "example.py",
    "function_name": "calculate_sum", // or provide line numbers
    "language": "python"
  }
}
```

### Expected Outcome

The module would analyze the function `calculate_sum` and might return a suggested docstring. The `edit_file` tool could then be used to insert this docstring.

**Suggested Docstring (example):**
```python
"""Calculates the sum of two numbers.

Args:
    a: The first number.
    b: The second number.

Returns:
    The sum of a and b.
"""
```

## Example 2: Refactoring a Code Snippet for Readability

**Scenario**: You have a complex line of code and want the AI to suggest a more readable version.

**Input Code (JavaScript):**
```javascript
const result = data.filter(item => item.active && item.value > 100).map(item => ({ id: item.id, processedValue: item.value * 0.8 })).sort((a, b) => b.processedValue - a.processedValue);
```

**Invocation (conceptual MCP call using `ai_code_editing.edit_file` or a specific refactoring tool):**
```json
{
  "tool_name": "ai_code_editing.edit_file",
  "arguments": {
    "target_file": "src/processing.js",
    "start_line": 5, // Line where the complex code exists
    "end_line": 5,
    "edit_instruction": "Refactor this line for better readability. Break it down into multiple steps if necessary.",
    "language": "javascript"
  }
}
```

### Configuration (if any)

- The AI model might be configured to prioritize readability or conciseness based on project settings.

### Expected Outcome

The AI suggests a refactored version of the code, which is then applied to the file.

**Example Refactored Code:**
```javascript
const activeItemsOverThreshold = data.filter(item => item.active && item.value > 100);
const processedItems = activeItemsOverThreshold.map(item => ({
  id: item.id,
  processedValue: item.value * 0.8
}));
const result = processedItems.sort((a, b) => b.processedValue - a.processedValue);
```

## Common Pitfalls & Troubleshooting

- **Issue**: AI suggestions are irrelevant or incorrect.
  - **Solution**: 
    - Ensure sufficient context is provided to the AI (e.g., surrounding code, project dependencies).
    - Refine the prompt or instruction to be more specific.
    - Check if the correct language model or settings are configured for the task.
- **Issue**: Edits applied by AI introduce errors.
  - **Solution**:
    - Always review AI-generated code edits before committing.
    - Utilize testing and static analysis tools to catch regressions.
    - Provide feedback to the AI system if it supports learning from corrections. 
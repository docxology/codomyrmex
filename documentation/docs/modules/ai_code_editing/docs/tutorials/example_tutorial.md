---
id: ai-code-editing-example-tutorial
title: Example Tutorial - Getting Started with Code Generation
sidebar_label: Code Generation Tutorial
---

# Ai Code Editing - Example Tutorial: Getting Started with Code Generation (Feature X)

This tutorial will guide you through the process of using a hypothetical code generation feature of the Ai Code Editing module.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Ai Code Editing module installed and configured (see main [module overview](../../index.md)).
- An LLM service configured and API key set up (refer to [Environment Setup](../../../../../docs/development/environment-setup.md)).
- A sample Python project or file to work with.
- Familiarity with basic Python and how your editor integrates with Codomyrmex tools.

## 2. Goal

By the end of this tutorial, you will be able to:

- Use the AI Code Editing module to generate a simple Python function based on a natural language prompt.
- Understand the basic workflow of invoking an AI code generation tool.

## 3. Steps

### Step 1: Prepare Your Python File

Create a Python file, for example `my_utils.py`, with the following content:

```python
# my_utils.py

# We will ask the AI to generate a function here


def main():
    # We will call the generated function here
    pass

if __name__ == "__main__":
    main()

```

### Step 2: Invoke Code Generation (Conceptual)

Imagine you are in your editor, with `my_utils.py` open. You want to generate a function that adds two numbers, right before the `main` function definition.

You would trigger the AI Code Editing tool (e.g., via a command palette, right-click menu, or an MCP call if you are an agent).

**Conceptual MCP Call (using `ai_code_editing.edit_file`):**

```json
{
  "tool_name": "ai_code_editing.edit_file",
  "arguments": {
    "target_file": "my_utils.py",
    "edit_instruction": "Insert a Python function called 'add_numbers' that takes two arguments, 'x' and 'y', and returns their sum. Place it before the 'main' function.",
    "language": "python",
    "edit_type": "insert",
    // Line number might be specified or inferred to be before 'main'
  }
}
```

*(Note: A more specialized tool like `ai_code_editing.generate_function` might also exist, simplifying the arguments.)*

### Step 3: Verify the Output

The AI Code Editing module should process this request, interact with an LLM, and then modify `my_utils.py`.

**Expected `my_utils.py` after modification:**
```python
# my_utils.py

# We will ask the AI to generate a function here

def add_numbers(x, y):
    """Adds two numbers.

    Args:
        x: The first number.
        y: The second number.

    Returns:
        The sum of x and y.
    """
    return x + y

def main():
    # We will call the generated function here
    result = add_numbers(5, 3)
    print(f"The sum is: {result}")
    pass

if __name__ == "__main__":
    main()

```
(You might need to manually add the call to `add_numbers` in `main` as a subsequent step, or include it in a more complex prompt.)

## 4. Understanding the Results

The AI Code Editing module successfully interpreted your request, generated the Python function `add_numbers` along with a docstring, and inserted it into your file at the appropriate location.

## 5. Troubleshooting

- **Error: `LLM API key not found` or `Authentication error`**
  - **Cause**: The API key for your selected LLM service is missing or incorrect.
  - **Solution**: Ensure your API keys are correctly set up as environment variables or in your `.env` file, as described in the [Environment Setup Guide](../../../../../docs/development/environment-setup.md).
- **Output is not as expected (e.g., function placed incorrectly, wrong logic)**:
  - **Solution**: 
    - Refine your `edit_instruction` to be more precise about placement and logic.
    - Check the `LLMInterface` or MCP tool logs for any errors from the LLM service.
    - If the LLM consistently produces poor results for a type of task, the underlying prompts in `PromptManager` may need adjustment.

## 6. Next Steps

Congratulations on completing this tutorial!

Now you can try:
- Generating more complex functions or code snippets.
- Using the AI to refactor existing code (see [Usage Examples](../../usage_examples.md)).
- Exploring other capabilities of the AI Code Editing module. 
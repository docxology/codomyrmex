# Ai Code Editing - Tutorial: Refactoring Python Code with `refactor_code_snippet`

This tutorial will guide you through the process of using the `refactor_code_snippet` tool of the Ai Code Editing module to improve existing Python code.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Ai Code Editing module installed and configured (see main [README.md](../../README.md) and `environment_setup` module for API keys).
- Access to a configured LLM provider (like OpenAI or Anthropic) with a valid API key set up as an environment variable (e.g., `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).
- A sample Python file named `sample_to_refactor.py` in your working directory with some initial code (see Step 1).
- Familiarity with basic Python syntax and how to execute MCP tool calls.

## 2. Goal

By the end of this tutorial, you will be able to:

- Successfully refactor a Python function to be more concise and Pythonic using the `refactor_code_snippet` tool.
- Understand how to provide a code snippet, refactoring instruction, and language to `refactor_code_snippet` and interpret its output.

## 3. Steps

### Step 1: Prepare Your Input Code

Create a Python file named `sample_to_refactor.py` in your current directory with the following content. This function is intentionally a bit verbose and can be improved.

```python
# sample_to_refactor.py
def get_even_doubled(numbers):
    """Takes a list of numbers, filters even ones, and doubles them."""
    result = []
    for num in numbers:
        if num % 2 == 0: # Check if the number is even
            doubled_num = num * 2
            result.append(doubled_num)
    return result

# Example usage (optional, not part of refactoring input)
# my_numbers = [1, 2, 3, 4, 5, 6]
# print(get_even_doubled(my_numbers)) # Expected: [4, 8, 12]
```

### Step 2: Invoke `refactor_code_snippet`

We will use a hypothetical MCP client. You'll need to pass the content of `sample_to_refactor.py` as the `code_snippet`.

**Using a hypothetical MCP client:**

```bash
# Ensure your shell environment has the necessary LLM API key (e.g., OPENAI_API_KEY)
# Read the file content into a variable or use command substitution
FILE_CONTENT=$(cat sample_to_refactor.py)

# Example using a fictional codomyrmex_mcp_client:
codomyrmex_mcp_client call ai_code_editing refactor_code_snippet \
  --code_snippet "${FILE_CONTENT}" \
  --refactoring_instruction "Make this Python function more concise and Pythonic using a list comprehension. Keep the docstring." \
  --language "python" \
  # Optional: --llm_provider "openai" --model_name "gpt-4"
```

**Parameters used:**
- `code_snippet`: The actual source code string to be refactored.
- `refactoring_instruction`: A clear instruction to the LLM on how the code should be changed.
- `language`: The programming language of the snippet (here, "python").
- `llm_provider` (optional): Specify an LLM provider. Defaults to module configuration.
- `model_name` (optional): Specify a particular model. Defaults to module configuration for refactoring (often a more capable model is better for refactoring).

### Step 3: Verify the Output

Check the JSON response from the MCP tool.

- Look for `"status": "success"`.
- The refactored code will be in the `"refactored_code"` field.

**Expected `refactored_code` (example, actual output may vary slightly):**

```python
# sample_to_refactor.py
def get_even_doubled(numbers):
    """Takes a list of numbers, filters even ones, and doubles them."""
    return [num * 2 for num in numbers if num % 2 == 0]

# Example usage (optional, not part of refactoring input)
# my_numbers = [1, 2, 3, 4, 5, 6]
# print(get_even_doubled(my_numbers)) # Expected: [4, 8, 12]
```

## 4. Understanding the Results

The `refactor_code_snippet` tool used the LLM to understand your refactoring instruction and apply it to the provided Python code. The resulting code should be functionally equivalent but more concise by using a list comprehension, as requested.

## 5. Troubleshooting

- **Error: `LLM API request failed.` / `"status": "error"` with an API error message**
  - **Cause**: Similar to `generate_code_snippet` - API key issues, network problems, provider outages, or problematic input code/instructions.
  - **Solution**: 
    1. Verify your LLM API key and its status.
    2. Check internet connectivity and LLM provider status.
    3. Ensure the `code_snippet` is valid for the specified `language`.
- **Refactored code is incorrect, doesn't work, or introduces bugs**:
  - **Cause**: The `refactoring_instruction` might be ambiguous. The LLM might misunderstand complex code or the desired transformation. Refactoring can be harder than generation for LLMs.
  - **Solution**: 
    1. **Clarify Instruction**: Make the `refactoring_instruction` highly specific. Mention exact patterns to use or avoid. For example, instead of "improve this code," say "convert the for-loop to a list comprehension."
    2. **Simplify Input**: If refactoring a large or complex piece of code, try with a smaller, isolated part first.
    3. **Break Down Task**: For very complex refactoring, consider multiple `refactor_code_snippet` calls with sequential instructions.
    4. **Try a Different Model**: More advanced models (e.g., GPT-4, Claude 3 Opus) are generally better at understanding code and refactoring accurately. Specify one if your setup allows.
    5. **Review Carefully**: Always thoroughly review and test LLM-refactored code before committing it.
- **Minor stylistic changes not applied or unwanted changes made**:
  - **Cause**: LLMs have their own implicit style biases.
  - **Solution**: Be explicit in your `refactoring_instruction` about preserving specific formatting or applying certain style conventions. You might need to run a code formatter (like Black or Prettier) on the output as a separate step.

## 6. Next Steps

Congratulations on using `refactor_code_snippet`!

Now you can try:
- Refactoring your own Python code or code in other supported languages.
- Providing more complex `refactoring_instruction` like "add error handling for X condition" or "optimize this function for readability."
- Using `refactor_code_snippet` to translate code from one style to another (e.g., functional to object-oriented, though this is a very advanced use case).
- Reviewing the `ai_code_editing/MCP_TOOL_SPECIFICATION.md` for all parameters of `refactor_code_snippet`. 
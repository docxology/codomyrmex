# Ai Code Editing - Example Tutorial: Getting Started with [Feature X]

<!-- TODO: Replace '[Feature X]' in the title and throughout this tutorial with a specific, key feature of the Ai Code Editing module. 
    Examples: 
    - "Generating a Python Function with `generate_code_snippet`"
    - "Refactoring JavaScript Code with `refactor_code_snippet`"
    - "Understanding a Code Block via AI Summarization (if summarization tool exists)" 
-->

This tutorial will guide you through the process of using [Feature X] of the Ai Code Editing module.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Ai Code Editing module installed and configured (see main [README.md](../../README.md) and `environment_setup` module for API keys).
- <!-- TODO: List any specific tools, accounts, or data needed for *this specific tutorial*. 
    E.g., For `generate_code_snippet`: "Access to a configured LLM provider (like OpenAI or Anthropic)." 
    E.g., For `refactor_code_snippet`: "A sample Python file named `sample_code.py` with some initial code." -->
- Familiarity with <!-- TODO: Basic concepts related to the module or feature. E.g., "basic Python syntax", "understanding of MCP tool invocation if using a client". -->

## 2. Goal

By the end of this tutorial, you will be able to:

- <!-- TODO: State the primary learning objective. E.g., "Successfully generate a Python function to calculate Fibonacci numbers using the `generate_code_snippet` tool." -->
- <!-- TODO: Understand the basic workflow of [Feature X]. E.g., "Understand how to provide a prompt and language to `generate_code_snippet` and interpret its output." -->

## 3. Steps

### Step 1: Prepare Your Input

<!-- TODO: Describe how to prepare any necessary input data or environment for the tutorial. 
    This could be creating a small script, defining a prompt, or ensuring an API key is set. -->

```bash
# Example: If [Feature X] is `generate_code_snippet` for a Python function
# No specific file input needed, but ensure your OPENAI_API_KEY (or other provider) is set in your .env file.
# Your prompt will be the primary input.
```

```python
# Example: If [Feature X] is `refactor_code_snippet` for a Python function
# Create a file named `my_script_to_refactor.py` with the following content:
# def inefficient_function(my_list):
#     new_list = []
#     for item in my_list:
#         if item % 2 == 0:
#             new_list.append(item * 2)
#     return new_list
```

### Step 2: Invoke [Feature X]

<!-- TODO: Provide clear, step-by-step instructions on how to use the feature. Include code snippets or commands. 
    Show how to call the relevant MCP tool or API function. -->

**Using a hypothetical MCP client (example for `generate_code_snippet`):**

```bash
# <!-- TODO: Replace with actual command or illustrate client library usage -->
# codomyrmex_mcp_client call ai_code_editing generate_code_snippet \
#   --prompt "Create a Python function that takes a list of integers and returns a new list containing only even numbers, where each even number is multiplied by 2." \
#   --language "python"
```

**Using a hypothetical MCP client (example for `refactor_code_snippet`):**

```bash
# <!-- TODO: Replace with actual command or illustrate client library usage -->
# Assuming my_script_to_refactor.py exists from Step 1
# codomyrmex_mcp_client call ai_code_editing refactor_code_snippet \
#   --code_snippet "$(cat my_script_to_refactor.py)" \
#   --refactoring_instruction "Make this Python code more concise using a list comprehension." \
#   --language "python"
```

### Step 3: Verify the Output

<!-- TODO: Explain how to check if the feature worked correctly. What should the output look like? 
    For code generation/refactoring, this means inspecting the `generated_code` or `refactored_code` field from the MCP tool's JSON response. -->

- Check the JSON response from the MCP client.
- For `generate_code_snippet` or `refactor_code_snippet`, look for `"status": "success"`.
- Inspect the `"generated_code"` or `"refactored_code"` field for the AI's output.
  <!-- TODO: Provide an example of what the expected code output might look like for your chosen [Feature X]. -->

## 4. Understanding the Results

<!-- TODO: Briefly explain the output or outcome of the tutorial steps. 
    What does the generated/refactored code do? How does it meet the prompt/instruction? -->

## 5. Troubleshooting

- **Error: `LLM API request failed.` (or similar from MCP tool output)**
  - **Cause**: Could be an invalid/missing API key, network issues, LLM provider outage, or issues with the prompt/code sent (e.g., content policy violation).
  - **Solution**: 
    1. Verify your LLM API key is correctly set in your environment (e.g., `.env` file) and is valid.
    2. Check your internet connection.
    3. Check the LLM provider's status page.
    4. Simplify your prompt or code snippet to see if a more basic request works.
- **Output is not as expected (e.g., code doesn't work, refactoring is incorrect)**:
  - **Cause**: Prompt engineering is key. The LLM might have misinterpreted the request.
  - **Solution**: 
    1. Rephrase your `prompt` or `refactoring_instruction` to be more specific and clear.
    2. Provide more `context_code` if using `generate_code_snippet`.
    3. Try a different LLM model or provider if available (via `llm_provider` and `model_name` parameters).
    4. Remember that LLM outputs can be non-deterministic and may require review and iteration.

<!-- TODO: Add other common issues specific to [Feature X] -->

## 6. Next Steps

Congratulations on completing this tutorial on [Feature X]!

Now you can try:
- <!-- TODO: Suggest next steps relevant to [Feature X] and the Ai Code Editing module. -->
- Exploring other parameters of the `generate_code_snippet` or `refactor_code_snippet` tools (see `MCP_TOOL_SPECIFICATION.md`).
- Using the tools with your own code projects.
- Combining these tools with other Codomyrmex modules. 
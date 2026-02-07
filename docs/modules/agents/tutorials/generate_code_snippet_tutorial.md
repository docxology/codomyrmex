# Ai Code Editing - Tutorial: Generating a Python Function with `generate_code_snippet`

This tutorial will guide you through the process of using the `generate_code_snippet` tool of the Ai Code Editing module.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Ai Code Editing module installed and configured (see main [README.md](../../README.md) and `environment_setup` module for API keys).
- Access to a configured LLM provider (like OpenAI or Anthropic) with a valid API key set up as an environment variable (e.g., `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).
- Familiarity with basic Python syntax and how to execute MCP tool calls (e.g., using a hypothetical `codomyrmex_mcp_client` or direct API interaction if applicable).

## 2. Goal

By the end of this tutorial, you will be able to:

- Successfully generate a Python function to calculate Fibonacci numbers using the `generate_code_snippet` tool.
- Understand how to provide a prompt, language, and optional context code to `generate_code_snippet` and interpret its output.

## 3. Steps

### Step 1: Prepare Your Input

For this tutorial, the primary input is the textual prompt describing the function you want to generate. No specific files are needed beforehand, but ensure your LLM API key is correctly configured.

Your prompt will be: "Create a Python function that takes an integer `n` and returns the `n`-th Fibonacci number. The function should handle non-negative `n`. Include a docstring."

### Step 2: Invoke `generate_code_snippet`

We will use a hypothetical MCP client to call the tool. The actual method of calling MCP tools might vary based on the client implementation used in your Codomyrmex setup.

**Using a hypothetical MCP client:**

```bash
# Ensure your shell environment has the necessary LLM API key (e.g., OPENAI_API_KEY)
# Example using a fictional codomyrmex_mcp_client:
codomyrmex_mcp_client call agents generate_code_snippet \
  --prompt "Create a Python function that takes an integer n and returns the n-th Fibonacci number. The function should handle non-negative n. Include a docstring." \
  --language "python" \
  # Optional: --llm_provider "openai" --model_name "gpt-3.5-turbo"
```

**Parameters used:**
- `prompt`: The detailed description of the code to be generated.
- `language`: Specifies the programming language of the desired snippet (here, "python").
- `llm_provider` (optional): Specify an LLM provider like "openai" or "anthropic". Defaults to module configuration.
- `model_name` (optional): Specify a particular model. Defaults to module configuration for generation.

### Step 3: Verify the Output

After executing the command, you should receive a JSON response from the MCP tool.

- Look for `"status": "success"` in the response.
- The generated code will be in the `"generated_code"` field.

**Expected `generated_code` (example, actual output may vary slightly):**

```python
def fibonacci(n):
    """Calculate the n-th Fibonacci number.

    Args:
        n (int): A non-negative integer.

    Returns:
        int: The n-th Fibonacci number.
        None: If n is negative.
    """
    if n < 0:
        print("Input must be a non-negative integer")
        return None
    elif n <= 1:
        return n
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

```

## 4. Understanding the Results

The `generate_code_snippet` tool, guided by your prompt, instructed the configured LLM to create a Python function. The output should be a complete, runnable Python function that calculates Fibonacci numbers as requested, including basic error handling for negative input and a docstring.

## 5. Troubleshooting

- **Error: `LLM API request failed.` / `"status": "error"` with an API error message**
  - **Cause**: Invalid/missing API key, network issues, LLM provider outage, insufficient credits, or a prompt that violates content policies.
  - **Solution**: 
    1. Verify your LLM API key (e.g., `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) is correctly set in your environment and is active with available funds/quota.
    2. Check your internet connectivity.
    3. Check the status page of your LLM provider (e.g., OpenAI Status).
    4. Try a simpler prompt to isolate the issue.
- **Output code is incorrect, incomplete, or doesn't meet requirements**:
  - **Cause**: The prompt might lack clarity or specificity. LLMs can also produce suboptimal results.
  - **Solution**: 
    1. **Refine the Prompt**: Make your `prompt` more detailed. Specify constraints, edge cases, or desired coding style.
    2. **Provide `context_code`**: If the function should interact with existing code, provide that code via the `context_code` parameter. This helps the LLM understand the surrounding environment.
    3. **Try a Different Model**: If your setup allows, try specifying a more capable `model_name` (e.g., "gpt-4" if you were using "gpt-3.5-turbo").
    4. **Iterate**: LLM-based code generation often requires a few iterations. Use the output as a starting point and refine it or try a modified prompt.
- **Tool reports `unsupported language`**:
  - **Cause**: The `language` parameter specified is not recognized or supported by the current LLM or the tool's internal mapping.
  - **Solution**: Check the `MCP_TOOL_SPECIFICATION.md` for supported languages or try common language identifiers (e.g., "python", "javascript", "java").

## 6. Next Steps

Congratulations on completing this tutorial on `generate_code_snippet`!

Now you can try:
- Generating code in different programming languages.
- Using the `context_code` parameter to generate code that fits into an existing script or class.
- Exploring more complex prompts, like asking for classes or functions with specific error handling.
- Reviewing the `agents/MCP_TOOL_SPECIFICATION.md` for all available parameters and options for `generate_code_snippet`. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Root README](../../README.md)

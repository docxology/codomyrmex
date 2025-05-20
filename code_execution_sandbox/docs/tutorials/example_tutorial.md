# Code Execution Sandbox - Example Tutorial: Getting Started with [Feature X]

<!-- TODO: Replace '[Feature X]' in the title and throughout this tutorial with a specific, key feature/scenario of the Code Execution Sandbox. 
    The primary feature is code execution via the `execute_code` MCP tool. So, the title should reflect a specific scenario for that.
    Examples: 
    - "Executing a Simple Python Script in the Sandbox"
    - "Running JavaScript with Input and Resource Limits"
    - "Handling Timeouts and Errors from Sandboxed Code" 
-->

This tutorial will guide you through the process of using [Feature X] of the Code Execution Sandbox module.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Code Execution Sandbox module installed and configured (see main [README.md](../../README.md)).
- The chosen sandboxing technology (e.g., Docker) must be running and correctly configured.
- <!-- TODO: List any specific setup for *this specific tutorial scenario*. 
    E.g., "Ensured Python 3.9 is a supported language in the sandbox configuration." -->
- Familiarity with <!-- TODO: Basic concepts. E.g., "JSON format for MCP requests", "the concept of stdin/stdout/stderr". -->

## 2. Goal

By the end of this tutorial, you will be able to:

- <!-- TODO: State the primary learning objective. E.g., "Successfully execute a Python script that prints to stdout using the `execute_code` MCP tool." -->
- <!-- TODO: Understand the basic workflow of [Feature X]. E.g., "Understand how to structure an `execute_code` request with language, code, and timeout, and how to interpret the JSON response containing stdout, stderr, exit_code, and status." -->

## 3. Steps

### Step 1: Prepare Your Code Snippet and Request

<!-- TODO: Describe how to prepare the code snippet and the MCP request for the tutorial's scenario. -->

**Code Snippet (e.g., Python):**
```python
# my_code.py
name = input("What is your name? ")
print(f"Hello, {name} from the Python sandbox!")
for i in range(3):
    print(f"Python iteration {i}")
```

**MCP Request (prepare this as a JSON structure):**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "python", // <!-- TODO: Ensure this language is supported by your sandbox setup -->
    "code": "name = input(\"What is your name? \")\nprint(f\"Hello, {name} from the Python sandbox!\")\nfor i in range(3):\n    print(f\"Python iteration {i}\")",
    "stdin": "CodomyrmexUser",
    "timeout": 15 // seconds
  }
}
```

### Step 2: Invoke `execute_code` MCP Tool

<!-- TODO: Provide clear, step-by-step instructions on how to send this MCP request. 
    This depends on how MCP tools are invoked in the project (e.g., via a test client, a specific CLI, or another module). -->

**Using a hypothetical MCP client command:**

```bash
# codomyrmex_mcp_client send_request '{ "tool_name": "execute_code", "arguments": { "language": "python", "code": "name = input(\"What is your name? \")\nprint(f\"Hello, {name} from the Python sandbox!\")\nfor i in range(3):\n    print(f\"Python iteration {i}\")", "stdin": "CodomyrmexUser", "timeout": 15 } }'
# Save the JSON output from this command.
```

### Step 3: Verify the Output

<!-- TODO: Explain how to check if the execution worked correctly by examining the JSON response from the MCP tool. -->

- Examine the JSON response from the `execute_code` tool.
- Look for `"status": "success"`.
- Check `"stdout"` for the expected output from your script.
- `"stderr"` should ideally be empty for a successful run of this example.
- `"exit_code"` should be `0`.

**Example Expected JSON Response:**
```json
{
  "stdout": "Hello, CodomyrmexUser from the Python sandbox!\nPython iteration 0\nPython iteration 1\nPython iteration 2\n",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.123, // This will vary
  "status": "success",
  "error_message": null
}
```

## 4. Understanding the Results

<!-- TODO: Briefly explain the output. How stdin was used, what stdout/stderr/exit_code signify in this context. -->
- The `stdin` ("CodomyrmexUser") was passed to the Python script's `input()` function.
- The script's `print()` statements were captured in `stdout`.
- An `exit_code` of `0` and empty `stderr` indicate successful execution of the user's code.
- `status: "success"` indicates the sandbox itself ran the code without system-level issues (like timeout or setup failure).

## 5. Troubleshooting

- **Error: `"status": "setup_error"` with `"error_message": "Language [language] not supported."`**
  - **Cause**: The requested language (e.g., "python" in the example) is not configured or enabled in the sandbox environment.
  - **Solution**: Verify the sandbox's language support. This might involve checking Docker images or sandbox configuration files. Refer to `docs/technical_overview.md` for details on language support.
- **Error: `"status": "timeout"`**
  - **Cause**: The code took longer to execute than the specified `timeout` (15 seconds in this example).
  - **Solution**: Optimize the code if possible, or increase the `timeout` value in the request (up to the globally configured maximum for the sandbox).
- **Script Error in `stderr` (e.g., `NameError`, `SyntaxError`) and non-zero `exit_code`**: 
  - **Cause**: The provided `code` itself has bugs.
  - **Solution**: Debug the code snippet. The sandbox correctly executed it, but the code failed on its own.

<!-- TODO: Add other common issues specific to this tutorial's scenario or the `execute_code` tool. -->

## 6. Next Steps

Congratulations on completing this tutorial on [Feature X]!

Now you can try:
- <!-- TODO: Suggest next steps relevant to the Code Execution Sandbox. -->
- Executing code in other supported languages.
- Experimenting with different `timeout` values.
- Testing code that produces errors to see how `stderr` and `exit_code` are reported.
- Reviewing the `SECURITY.md` and `MCP_TOOL_SPECIFICATION.md` for the `execute_code` tool to understand its security implications and full capabilities. 
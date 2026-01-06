# Code Execution Sandbox - Tutorial: Using `execute_code`

This tutorial will guide you through using the `execute_code` MCP tool from the Code Execution Sandbox module to run code snippets in different languages, handle inputs/outputs, and understand resource limits and error reporting.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Code Execution Sandbox module installed and configured (see main [README.md](../../README.md)).
- The chosen sandboxing technology (e.g., Docker) must be running and correctly configured on your system.
- The sandbox must be configured to support the languages used in this tutorial (e.g., Python, JavaScript). Check the `code_execution_sandbox/docs/technical_overview.md` or specific sandbox configuration for supported languages and versions.
- Familiarity with JSON format for MCP requests and the concept of stdin/stdout/stderr.
- Access to a client or mechanism to send MCP tool requests (e.g., a hypothetical `codomyrmex_mcp_client` CLI tool).

## 2. Goal

By the end of this tutorial, you will be able to:

- Successfully execute Python and JavaScript code snippets using the `execute_code` MCP tool.
- Provide standard input (`stdin`) to sandboxed code.
- Understand how resource limits (specifically `timeout`) are applied.
- Interpret the JSON response from `execute_code`, including `stdout`, `stderr`, `exit_code`, `status`, and `error_message` for various scenarios.

## 3. Scenarios

We will cover a few scenarios using MCP requests.

### Scenario 1: Basic Python Execution with Input

**Objective**: Run a Python script that takes input and prints output.

**Code Snippet (Python):**
```python
# Python script to greet a user and count
name = input("Enter your name: ")
print(f"Hello, {name}, from the Python sandbox!")
for i in range(1, 4):
    print(f"Python count: {i}")
```

**MCP Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "python",
    "code": "name = input(\"Enter your name: \")
print(f\"Hello, {name}, from the Python sandbox!\")
for i in range(1, 4):
    print(f\"Python count: {i}\")",
    "stdin": "CodomyrmexDev",
    "timeout": 10 
  }
}
```

**Invocation (using hypothetical client):**
```bash
# Save the above JSON as request1.json
codomyrmex_mcp_client send_request --file request1.json 
```

**Expected Response (example):**
```json
{
  "stdout": "Hello, CodomyrmexDev, from the Python sandbox!
Python count: 1
Python count: 2
Python count: 3
",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.08, 
  "status": "success",
  "error_message": null
}
```

**Understanding**: 
- The `stdin` ("CodomyrmexDev") was passed to `input()`.
- `print()` statements were captured in `stdout`.
- `status: "success"` and `exit_code: 0` indicate successful execution.

### Scenario 2: JavaScript Execution

**Objective**: Run a simple JavaScript snippet.

**Code Snippet (JavaScript):**
```javascript
// Simple JS example
let message = "Hello from JavaScript sandbox!";
let a = 5, b = 10;
console.log(message);
console.log(`Calculation: ${a} * ${b} = ${a * b}`);
```

**MCP Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "javascript", 
    "code": "let message = \"Hello from JavaScript sandbox!\";
let a = 5, b = 10;
console.log(message);
console.log(`Calculation: ${a} * ${b} = ${a * b}`);",
    "timeout": 5
  }
}
```

**Invocation (using hypothetical client):**
```bash
# Save the above JSON as request2.json
codomyrmex_mcp_client send_request --file request2.json
```

**Expected Response (example):**
```json
{
  "stdout": "Hello from JavaScript sandbox!
Calculation: 5 * 10 = 50
",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.15, 
  "status": "success",
  "error_message": null
}
```

### Scenario 3: Handling a Timeout

**Objective**: Observe behavior when code exceeds the specified timeout.

**Code Snippet (Python with a loop):**
```python
import time
print("Starting long task...")
i = 0
while True:
    i += 1
    # print(f"Loop iteration {i}") # Uncomment to see partial output
    time.sleep(0.5)
```

**MCP Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "python",
    "code": "import time
print(\"Starting long task...\")
i = 0
while True:
    i += 1
    time.sleep(0.5)",
    "timeout": 2 
  }
}
```

**Invocation (using hypothetical client):**
```bash
# Save the above JSON as request3.json
codomyrmex_mcp_client send_request --file request3.json
```

**Expected Response (example):**
```json
{
  "stdout": "Starting long task...
", // Might contain some output before timeout
  "stderr": "",
  "exit_code": null, // Or a system-specific code indicating termination due to timeout
  "execution_time": 2.0, // Approximately the timeout value
  "status": "timeout",
  "error_message": "Execution timed out after 2 seconds."
}
```
**Understanding**: The code was terminated because it ran longer than the 2-second `timeout`. `stdout` might contain output produced before termination.

### Scenario 4: Handling Code with an Error

**Objective**: See how errors within the executed code are reported.

**Code Snippet (Python with a ZeroDivisionError):**
```python
print("Preparing to divide...")
x = 10
y = 0
result = x / y 
print(f"Result: {result}") # This won't be reached
```

**MCP Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "python",
    "code": "print(\"Preparing to divide...\")
x = 10
y = 0
result = x / y 
print(f\"Result: {result}\")",
    "timeout": 5
  }
}
```

**Invocation (using hypothetical client):**
```bash
# Save the above JSON as request4.json
codomyrmex_mcp_client send_request --file request4.json
```

**Expected Response (example):**
```json
{
  "stdout": "Preparing to divide...
",
  "stderr": "Traceback (most recent call last):
  File \"/sandbox/code.py\", line 4, in <module>
    result = x / y 
ZeroDivisionError: division by zero
",
  "exit_code": 1,
  "execution_time": 0.06, 
  "status": "execution_error",
  "error_message": "Code execution resulted in an error."
}
```
**Understanding**: The Python script itself failed. `stderr` contains the traceback, `exit_code` is non-zero, and `status` is `"execution_error"`.

## 4. Important Considerations

-   **Supported Languages**: The `language` parameter must match a language explicitly configured and supported by your Code Execution Sandbox instance. Check `code_execution_sandbox/docs/technical_overview.md` or the sandbox's runtime configuration.
-   **Resource Limits**: Beyond the per-request `timeout`, the sandbox enforces global limits on CPU, memory, and PIDs. Code hitting these will also be terminated, likely with a specific `status` and `error_message`.
-   **Security**: 
    -   The code you submit is executed in a highly restricted environment. However, always treat code from untrusted sources with caution.
    -   **Never embed secrets directly in the code strings.**
    -   Refer to `code_execution_sandbox/SECURITY.md` for comprehensive security details.
-   **Idempotency**: Unless your sandbox implementation explicitly supports and guarantees session persistence via the `session_id` parameter (see `MCP_TOOL_SPECIFICATION.md`), treat each `execute_code` call as independent and ephemeral.

## 5. Next Steps

Congratulations on completing this tutorial!

Now you can try to:
- Execute code in other languages supported by your sandbox setup (e.g., bash).
- Experiment with different `timeout` values to understand the limits.
- Test more complex scripts that might interact with `stdin` or produce varied `stdout`/`stderr`.
- Review the `code_execution_sandbox/MCP_TOOL_SPECIFICATION.md` for the `execute_code` tool to understand its full capabilities and constraints.
- Consider how the `ai_code_editing` module might use this tool to validate or run AI-generated code snippets. 
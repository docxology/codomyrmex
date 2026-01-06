# Code Execution Sandbox - Usage Examples

This document provides examples of how to use the Code Execution Sandbox module within the Codomyrmex project.

## Prerequisites

1. Docker must be installed and running on your system.
2. Install the required dependencies:
   ```bash
   uv sync --extra code_execution_sandbox
   ```

## Basic Usage

### Execute a Simple Python Script

```python
from code_execution_sandbox import execute_code

# Define a simple Python script
python_code = """
print("Hello, World!")
x = 5
y = 7
print(f"Sum: {x + y}")
"""

# Execute the code
result = execute_code(
    language="python",
    code=python_code,
    timeout=10  # Optional: set a custom timeout (default is 30 seconds)
)

# Print the results
print(f"Status: {result['status']}")
print(f"Exit Code: {result['exit_code']}")
print(f"Execution Time: {result['execution_time']} seconds")
print("
Output:")
print(result['stdout'])

if result['stderr']:
    print("
Errors:")
    print(result['stderr'])
```

Expected output:
```
Status: success
Exit Code: 0
Execution Time: 0.834 seconds

Output:
Hello, World!
Sum: 12
```

### Execute JavaScript Code with Input

```python
from code_execution_sandbox import execute_code

# JavaScript code that reads from stdin
js_code = """
const readline = require('readline');
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question('What is your name? ', (name) => {
  console.log(`Hello, ${name}!`);
  rl.close();
});
"""

# Execute with input
result = execute_code(
    language="javascript",
    code=js_code,
    stdin="Alice"
)

print(f"Status: {result['status']}")
print(f"Output:
{result['stdout']}")
```

Expected output:
```
Status: success
Output:
What is your name? Hello, Alice!
```

### Handle Execution Errors

```python
from code_execution_sandbox import execute_code

# Python code with an error
python_code_with_error = """
# Attempt to divide by zero
result = 10 / 0
print(result)  # This line will never execute
"""

# Execute the code
result = execute_code(
    language="python",
    code=python_code_with_error
)

print(f"Status: {result['status']}")
print(f"Exit Code: {result['exit_code']}")
print(f"Execution Time: {result['execution_time']} seconds")

if result['stderr']:
    print("
Errors:")
    print(result['stderr'])
```

Expected output:
```
Status: execution_error
Exit Code: 1
Execution Time: 0.712 seconds

Errors:
Traceback (most recent call last):
  File "/sandbox/code.py", line 2, in <module>
    result = 10 / 0
ZeroDivisionError: division by zero
```

### Handle Timeouts

```python
from code_execution_sandbox import execute_code

# Python code with an infinite loop
infinite_loop_code = """
import time
while True:
    print("Still running...")
    time.sleep(1)
"""

# Execute with a short timeout
result = execute_code(
    language="python",
    code=infinite_loop_code,
    timeout=3  # Set a short timeout of 3 seconds
)

print(f"Status: {result['status']}")
print(f"Error Message: {result['error_message']}")
print(f"Partial Output:
{result['stdout']}")
```

Expected output:
```
Status: timeout
Error Message: Execution timed out after 3 seconds.
Partial Output:
Still running...
Still running...
Still running...
```

## Shell Script Example

```python
from code_execution_sandbox import execute_code

# Shell script
bash_code = """
#!/bin/bash
echo "Current directory:"
pwd
echo "Files:"
ls -la
echo "Environment variables:"
env | grep PATH
"""

# Execute the shell script
result = execute_code(
    language="bash",
    code=bash_code
)

print(f"Status: {result['status']}")
print(f"Output:
{result['stdout']}")
```

## Advanced Usage

### Check Supported Languages

```python
from code_execution_sandbox import get_supported_languages # Assuming such a function exists

# supported_langs = get_supported_languages()
# print("Supported languages:", supported_langs)
# TODO: Implement and document this function if it's part of the module's direct API.
# For MCP, supported languages are typically documented in the MCP_TOOL_SPECIFICATION.md.
```

## Using `execute_code` via Model Context Protocol (MCP)

The `execute_code` tool is designed to be called via the Model Context Protocol. Below are conceptual examples of how an agent or MCP client might invoke it.

### MCP Example: Simple Python Execution

**Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "python",
    "code": "print('Hello from MCP in Python!')
x = 10 + 20
print(f'The result is: {x}')",
    "timeout": 15
  }
}
```

**Expected Response (example):**
```json
{
  "stdout": "Hello from MCP in Python!
The result is: 30
",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.08,
  "status": "success",
  "error_message": null
}
```

### MCP Example: JavaScript with Stdin

**Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "javascript",
    "code": "process.stdin.on('data', function (data) { console.log('JS received: ' + data.toString()); });",
    "stdin": "Test input for JS",
    "timeout": 5
  }
}
```

**Expected Response (example):**
```json
{
  "stdout": "JS received: Test input for JS
",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.15,
  "status": "success",
  "error_message": null
}
```

### MCP Example: Bash Script Execution

**Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "bash",
    "code": "#!/bin/bash
echo \"Hello from Bash via MCP!\"
whoami
date",
    "timeout": 5
  }
}
```

**Expected Response (example):**
```json
{
  "stdout": "Hello from Bash via MCP!
sandbox_user
<current date and time>
",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.05,
  "status": "success",
  "error_message": null
}
```
*(Note: `whoami` output depends on the user configured inside the sandbox container, e.g., `sandbox_user` or `nobody`)*

### MCP Example: Handling a Timeout

**Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "python",
    "code": "import time
while True: time.sleep(0.1)",
    "timeout": 2
  }
}
```

**Expected Response (example):**
```json
{
  "stdout": "", 
  "stderr": "",
  "exit_code": null, // Or a system-specific code for timeout, e.g., 137, 124
  "execution_time": 2.0,
  "status": "timeout",
  "error_message": "Execution timed out after 2 seconds."
}
```

### MCP Example: Code with an Error

**Request:**
```json
{
  "tool_name": "execute_code",
  "arguments": {
    "language": "python",
    "code": "print('About to error...')
result = 1 / 0",
    "timeout": 5
  }
}
```

**Expected Response (example):**
```json
{
  "stdout": "About to error...
",
  "stderr": "Traceback (most recent call last):
  File \"/sandbox/code.py\", line 2, in <module>
    result = 1 / 0
ZeroDivisionError: division by zero
",
  "exit_code": 1,
  "execution_time": 0.07,
  "status": "execution_error",
  "error_message": "Code execution resulted in an error."
}
```

## Resource Limits and Security Notes

-   **Implicit Limits**: The Code Execution Sandbox enforces strict, non-configurable (at runtime via MCP call) limits on resources like CPU, memory, and total execution time (a global maximum applies even if `timeout` parameter is set higher). These are defined in the sandbox module's secure configuration.
-   **Network Access**: By default, sandboxed code has **NO** network access. This is a critical security measure. If specific, trusted use cases require network access for a particular language runtime, this must be explicitly configured by an administrator in the sandbox module's setup, with strict allow-lists for target hosts/ports.
-   **Filesystem Access**: Sandboxed code operates with a very restricted view of the filesystem. It typically has a temporary, ephemeral working directory and cannot access the host filesystem or other parts of the project. Any files needed by the code must be provided within the `code` payload itself (e.g. as string literals) or through future parameters if file passing is supported by the `execute_code` tool (which would involve securely copying data into the sandbox).
-   **Security of Submitted Code**: 
    -   While the sandbox aims to contain execution, always treat the `code` submitted to this tool as potentially untrusted, especially if derived from user input or AI generation.
    -   Avoid including sensitive information (API keys, passwords, PII) directly within the `code` string. If code needs secrets, a more secure pattern (like the sandbox calling a trusted external service that holds the secret) should be used if feasible.
    -   Review the [SECURITY.md](./SECURITY.md) for this module for a comprehensive understanding of its security posture, threat model, and best practices.
-   **Idempotency and Sessions**: The `session_id` parameter is mentioned in the MCP specification. If the specific sandbox implementation supports persistent sessions (e.g., to allow `pip install` in one call and then run code using that package in a subsequent call within the same session), this can affect idempotency. If sessions are not supported or `session_id` is not used, each call is independent. Assume calls are independent unless your specific implementation guarantees session persistence and details its behavior.

Remember to consult the `code_execution_sandbox/MCP_TOOL_SPECIFICATION.md` for the most up-to-date details on the `execute_code` tool's parameters and behavior. 
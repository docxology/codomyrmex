# Code Execution Sandbox - Usage Examples

This document provides examples of how to use the Code Execution Sandbox module within the Codomyrmex project.

## Prerequisites

1. Docker must be installed and running on your system.
2. Install the required dependencies:
   ```bash
   pip install -r code_execution_sandbox/requirements.txt
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
print("\nOutput:")
print(result['stdout'])

if result['stderr']:
    print("\nErrors:")
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
print(f"Output:\n{result['stdout']}")
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
    print("\nErrors:")
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
print(f"Partial Output:\n{result['stdout']}")
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
print(f"Output:\n{result['stdout']}")
```

## Advanced Usage

### Check Supported Languages

```python
from code_execution_sandbox.code_executor import SUPPORTED_LANGUAGES

print("Supported languages:")
for language, config in SUPPORTED_LANGUAGES.items():
    print(f"- {language} (using {config['image']})")
```

### Error Handling Best Practices

```python
from code_execution_sandbox import execute_code

def safely_execute_user_code(language, code):
    """Safely execute user-provided code with proper error handling."""
    try:
        result = execute_code(
            language=language,
            code=code,
            timeout=10
        )
        
        if result["status"] == "success":
            return {
                "success": True,
                "output": result["stdout"],
                "execution_time": result["execution_time"]
            }
        elif result["status"] == "timeout":
            return {
                "success": False,
                "error": "Your code took too long to execute (timeout).",
                "partial_output": result["stdout"]
            }
        elif result["status"] == "execution_error":
            return {
                "success": False,
                "error": "Your code generated an error.",
                "error_details": result["stderr"],
                "partial_output": result["stdout"]
            }
        else:
            return {
                "success": False,
                "error": f"Sandbox error: {result['error_message']}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"System error: {str(e)}"
        }

# Example usage
result = safely_execute_user_code("python", "print('Hello, World!')")
print(result)
```

## Security Considerations

- Always treat all code as untrusted. The sandbox provides isolation but is not 100% secure against determined attackers.
- Avoid running the sandbox as root or with elevated privileges.
- Consider running the Docker daemon with additional security measures.
- Regularly update Docker and the base container images to get security patches.
- Monitor resource usage to detect abuse (e.g., cryptomining attempts). 
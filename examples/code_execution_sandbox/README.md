# Code Execution Sandbox Examples

Demonstrates safe code execution in isolated environments using the Codomyrmex Code Execution Sandbox module.

## Overview

The Code Execution Sandbox provides secure execution of untrusted code with resource limits, timeout protection, and isolated environments to prevent system compromise.

## Examples

### Basic Usage (`example_basic.py`)

- Execute Python code safely with resource limits
- Handle various code samples (calculations, string processing, error handling)
- Test input/output handling with stdin
- Demonstrate timeout protection for infinite loops
- Generate execution reports with timing and results

**Tested Methods:**
- `execute_code()` - Execute code in sandbox (from `test_code_execution_sandbox.py`)

## Configuration

```yaml
execution:
  default_timeout: 10        # Seconds before timeout
  max_memory: 100            # MB memory limit
  max_cpu: 50               # CPU usage limit (%)

  code_samples:
    - description: "Simple arithmetic"
      code: "print(10 + 20)"
      timeout: 5
    - description: "Input processing"
      code: "data = input(); print(data.upper())"
      stdin: "hello world"
      timeout: 5

sandbox:
  allow_network: false       # Block network access
  allow_filesystem: false    # Block file operations
  restricted_modules: [os, sys, subprocess]
  allowed_modules: [math, random, json, datetime]
```

## Running

```bash
cd examples/code_execution_sandbox
python example_basic.py
```

## Expected Output

The example will:
1. Execute multiple code samples safely
2. Show successful executions with output
3. Demonstrate error handling
4. Test timeout protection
5. Generate execution summary with success/failure rates
6. Save detailed results to JSON file

## Security Features

- **Resource Limits**: Memory and CPU restrictions
- **Timeout Protection**: Automatic termination of long-running code
- **Network Isolation**: No external network access
- **Filesystem Protection**: Restricted file operations
- **Module Restrictions**: Limited Python module access

## Use Cases

- **Educational Platforms**: Safe execution of student code
- **API Testing**: Execute user-submitted code samples
- **Code Analysis**: Test code snippets dynamically
- **Plugin Systems**: Run third-party plugins safely

## Integration Patterns

The sandbox integrates with other modules:
- **Security Audit**: Scan executed code for vulnerabilities
- **Logging**: Track execution metrics and errors
- **Performance**: Monitor resource usage
- **Data Visualization**: Graph execution results

## Related Documentation

- [Module README](../../src/codomyrmex/code_execution_sandbox/README.md)
- [Unit Tests](../../testing/unit/test_code_execution_sandbox.py)


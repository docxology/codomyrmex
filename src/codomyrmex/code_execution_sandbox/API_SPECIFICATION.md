# Code Execution Sandbox - API Specification

## Introduction

The Code Execution Sandbox module provides a secure environment for executing untrusted code in various programming languages. This API specification documents the programmatic interfaces available for code execution. The primary interaction is through the Python function API, which is also exposed via the Model Context Protocol (MCP) tool `execute_code`.

## Functions

### Function: `execute_code()`

- **Description**: Executes a code snippet in a specified programming language within a sandboxed Docker container.
- **Method**: N/A (Python function)
- **Path**: N/A
- **Parameters/Arguments**:
    - `language` (string): The programming language of the code (e.g., "python", "javascript", "bash").
    - `code` (string): The source code to be executed.
    - `stdin` (string, optional): Standard input to provide to the program.
    - `timeout` (integer, optional): Maximum execution time in seconds. Default: 30. Min: 1, Max: 300.
    - `session_id` (string, optional): Session identifier for potentially persistent environments.
- **Returns/Response**:
    - **Success**:
        ```python
        {
          "stdout": "Hello, World!
",
          "stderr": "",
          "exit_code": 0,
          "execution_time": 0.834,
          "status": "success",
          "error_message": None
        }
        ```
    - **Error** (e.g., timeout, execution error, setup error):
        ```python
        {
          "stdout": "Partial output if any...",
          "stderr": "Error details if from the code itself...",
          "exit_code": 1,  # Or another non-zero value, or -1 for system errors
          "execution_time": 0.5,
          "status": "timeout",  # Or "execution_error", "setup_error"
          "error_message": "Execution timed out after 10 seconds."  # Descriptive error message
        }
        ```

### Function: `check_docker_available()`

- **Description**: Internal utility function that checks if Docker is available on the system.
- **Method**: N/A (Python function)
- **Path**: N/A
- **Parameters/Arguments**: None
- **Returns/Response**: Boolean (True if Docker is available, False otherwise)

### Function: `execute_with_limits()`

- **Description**: Executes code with configurable resource limits and monitoring, providing detailed resource usage information.
- **Method**: N/A (Python function)
- **Path**: N/A
- **Parameters/Arguments**:
    - `language` (string): The programming language of the code
    - `code` (string): The source code to be executed
    - `limits` (ExecutionLimits): Resource limits configuration
    - `stdin` (string, optional): Standard input to provide to the program
    - `session_id` (string, optional): Session identifier for persistent environments
- **Returns/Response**: Dictionary with execution results plus resource usage:
    ```python
    {
      "stdout": "Hello, World!
",
      "stderr": "",
      "exit_code": 0,
      "execution_time": 0.834,
      "status": "success",
      "error_message": None,
      "resource_usage": {
        "execution_time_seconds": 0.834,
        "memory_start_mb": 45.2,
        "memory_peak_mb": 67.8,
        "cpu_samples": 8,
        "cpu_average_percent": 23.5,
        "cpu_peak_percent": 45.2
      },
      "limits_applied": {
        "time_limit_seconds": 30,
        "memory_limit_mb": 256,
        "cpu_limit_cores": 0.5,
        "max_output_chars": 100000
      }
    }
    ```

### Function: `sandbox_process_isolation()`

- **Description**: Executes code in a completely isolated subprocess environment with strict resource limits, preventing any impact on the main process.
- **Method**: N/A (Python function)
- **Path**: N/A
- **Parameters/Arguments**:
    - `language` (string): The programming language of the code
    - `code` (string): The source code to be executed
    - `limits` (ExecutionLimits): Resource limits configuration
    - `stdin` (string, optional): Standard input to provide to the program
- **Returns/Response**: Dictionary with execution results including isolation status

### Class: `ExecutionLimits`

- **Description**: Dataclass for configuring resource limits for code execution.
- **Parameters/Arguments** (constructor):
    - `time_limit` (int, optional): Maximum execution time in seconds (default: 30)
    - `memory_limit` (int, optional): Memory limit in MB (default: 256)
    - `cpu_limit` (float, optional): CPU cores limit (default: 0.5)
    - `max_output_chars` (int, optional): Maximum output characters (default: 100000)
- **Validation**: Automatically validates limits and raises ValueError for invalid configurations

### Class: `ResourceMonitor`

- **Description**: Monitors resource usage during code execution, tracking memory, CPU, and timing.
- **Methods**:
    - `start_monitoring()`: Begin resource monitoring
    - `update_monitoring()`: Update current resource usage
    - `get_resource_usage()`: Get comprehensive resource usage statistics

## Data Models

### Supported Languages Configuration

The module maintains a dictionary of supported programming languages with their associated Docker images and execution settings:

```python
SUPPORTED_LANGUAGES = {
    "python": {
        "image": "python:3.9-slim",
        "extension": "py",
        "command": ["python", "{filename}"],
        "timeout_factor": 1.2,
    },
    "javascript": {
        "image": "node:14-alpine",
        "extension": "js",
        "command": ["node", "{filename}"],
        "timeout_factor": 1.2,
    },
    "bash": {
        "image": "bash:5.1",
        "extension": "sh",
        "command": ["bash", "{filename}"],
        "timeout_factor": 1.2,
    },
}
```

### Execution Result Dictionary

All executed code returns a dictionary with the following structure:

- `stdout` (string): Standard output from the executed code.
- `stderr` (string): Standard error output from the executed code.
- `exit_code` (integer): Exit code returned by the process (0 typically indicates success).
- `execution_time` (float): Time taken for the code to execute, in seconds.
- `status` (string): Overall status, one of: "success", "timeout", "execution_error", "setup_error".
- `error_message` (string or None): Descriptive error message if status is not "success".

## Authentication & Authorization

This module does not implement authentication directly. Access control should be implemented at the application level when integrating this module. Since the sandbox executes untrusted code, it is critical that access to this API is properly secured in any application using it.

## Resource Limiting

The module applies the following resource limits to all code execution:

- **Memory**: 256MB limit per container
- **CPU**: 0.5 CPU cores per container
- **Processes**: Limited to 50 processes per container
- **Network**: No network access by default
- **File System**: Read-only container with access only to the temporary directory containing the code file

## Error Handling

The API returns descriptive error messages in the following scenarios:

1. **Unsupported Language**: When the requested language is not supported by the sandbox.
2. **Invalid Code**: When the provided code is empty or not a string.
3. **Docker Unavailable**: When Docker is not available on the system.
4. **Execution Timeout**: When the code execution exceeds the specified timeout.
5. **Container Setup Error**: When there is an issue setting up the Docker container.
6. **Code Execution Error**: When the code itself produces an error.

## Security Considerations

This API executes arbitrary code, which is inherently dangerous. The module implements multiple security measures:

1. **Isolation**: All code is executed in a Docker container with strict isolation.
2. **Resource Limits**: Container memory, CPU, and process count are strictly limited.
3. **Network Isolation**: Containers have no network access by default.
4. **File System Isolation**: Containers have read-only access and can only write to a temporary directory.
5. **Privilege Restriction**: All containers run with minimal privileges and cannot gain additional permissions.

Despite these measures, the API should be treated as security-sensitive. Only authorized users should have access to it. 
---
id: code-execution-sandbox-api-specification
title: Code Execution Sandbox - API Specification
sidebar_label: API Specification
---

# Code Execution Sandbox - API Specification

## Introduction

This API provides endpoints to securely execute code snippets or scripts in an isolated sandbox environment.

## Endpoints / Functions / Interfaces

### Endpoint/Function 1: `execute_code()`

- **Description**: Submits code for execution in a sandboxed environment.
- **Method**: POST
- **Path**: `/api/sandbox/execute`
- **Parameters/Arguments**:
    - `language` (string): The programming language of the code (e.g., `python`, `javascript`, `bash`).
    - `code` (string): The actual code snippet or script to execute.
    - `input_data` (string, optional): Standard input to be passed to the code.
    - `files` (object, optional): A dictionary where keys are filenames and values are file contents to be made available in the sandbox execution directory.
    - `timeout_seconds` (integer, optional): Maximum execution time. Defaults to system config.
    - `max_memory_mb` (integer, optional): Maximum memory allocation. Defaults to system config.
- **Request Body**:
    ```json
    {
      "language": "python",
      "code": "print(input())",
      "input_data": "Hello Sandbox!",
      "files": {
        "data.txt": "This is some data for the script."
      }
    }
    ```
- **Returns/Response**:
    - **Success (200 OK)**:
        ```json
        {
          "execution_id": "exec_guid_12345",
          "status": "completed", // or "error", "timeout"
          "stdout": "Hello Sandbox!\n",
          "stderr": "",
          "exit_code": 0,
          "duration_ms": 120,
          "output_files": {
            "result.txt": "Script output content..." // if script wrote files
          }
        }
        ```
    - **Error (e.g., 400 Bad Request for invalid language, 500 for sandbox failure)**:
        ```json
        {
          "error": "Unsupported language: 'cobol'" 
        }
        ```

## Data Models

### Model: `SandboxFile`
- `filename` (string): Name of the file in the sandbox.
- `content` (string): Content of the file (can be base64 encoded for binary).

### Model: `ExecutionResult`
- `execution_id` (string): Unique ID of the execution.
- `status` (string): `completed`, `timeout`, `error_runtime`, `error_setup`.
- `stdout` (string): Standard output from the script.
- `stderr` (string): Standard error output from the script.
- `exit_code` (integer): Exit code of the script.
- `duration_ms` (integer): Execution time in milliseconds.
- `memory_used_mb` (integer, optional): Peak memory used.
- `output_files` (object, optional): Dictionary of filenames and their content created by the script in its output directory.

## Authentication & Authorization

(API access should be secured, potentially with API keys or tokens, especially if exposed externally.)

## Rate Limiting

(Rate limits should be in place to prevent abuse of the execution environment.)

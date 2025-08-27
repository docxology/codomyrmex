---
id: static-analysis-api-specification
title: Static Analysis - API Specification
sidebar_label: API Specification
---

# Static Analysis - API Specification

## Introduction

This API allows programmatic interaction with the Static Analysis module, enabling tasks like initiating scans, retrieving results, and managing configurations.

## Endpoints / Functions / Interfaces

### Endpoint/Function 1: `run_analysis()`

- **Description**: Triggers a static analysis run on specified files or directories.
- **Method**: POST (if HTTP API) or N/A (if library function)
- **Path**: `/api/static_analysis/run` (if HTTP API)
- **Parameters/Arguments**:
    - `target_paths` (array[string]): List of file or directory paths to analyze.
    - `tool_ids` (array[string], optional): Specific static analysis tools to run (e.g., `["pylint", "bandit"]`). If omitted, runs all configured tools for the target file types.
    - `config_profile` (string, optional): Name of a pre-defined configuration profile to use.
- **Request Body** (if HTTP API):
    ```json
    {
      "target_paths": ["src/my_module/", "tests/test_my_module.py"],
      "tool_ids": ["pylint", "flake8"]
    }
    ```
- **Returns/Response**:
    - **Success (e.g., 202 Accepted or direct return for sync execution)**:
        ```json
        {
          "analysis_id": "unique_analysis_job_id_123",
          "status": "pending" // or "completed" if synchronous
        }
        ```
    - **Error (e.g., 4xx/5xx)**:
        ```json
        {
          "error": "Invalid target path specified."
        }
        ```

### Endpoint/Function 2: `get_analysis_results()`

- **Description**: Retrieves the results of a previously initiated static analysis run.
- **Method**: GET (if HTTP API)
- **Path**: `/api/static_analysis/results/{analysis_id}`
- **Parameters/Arguments**:
    - `analysis_id` (string): The ID of the analysis job.
- **Returns/Response**:
    - **Success (e.g., 200 OK)**:
        ```json
        {
          "analysis_id": "unique_analysis_job_id_123",
          "status": "completed",
          "results": [
            {
              "tool_id": "pylint",
              "file_path": "src/my_module/main.py",
              "line": 10,
              "column": 5,
              "message": "Missing docstring",
              "severity": "warning",
              "rule_id": "C0114"
            }
            // ... more issues
          ],
          "summary": {
            "total_issues": 5,
            "errors": 1,
            "warnings": 4
          }
        }
        ```
    - **Error (e.g., 404 Not Found)**:
        ```json
        {
          "error": "Analysis ID not found."
        }
        ```

## Data Models

### Model: `AnalysisIssue`
- `tool_id` (string): Identifier of the tool that reported the issue.
- `file_path` (string): Path to the file containing the issue.
- `line` (integer): Line number of the issue.
- `column` (integer, optional): Column number of the issue.
- `message` (string): Description of the issue.
- `severity` (string): e.g., `error`, `warning`, `info`.
- `rule_id` (string, optional): The specific rule ID that was violated.

## Authentication & Authorization

(If this module exposes HTTP endpoints, specify auth mechanisms. For internal library use, this might not be applicable.)

## Rate Limiting

(Specify any rate limits if the API is public or resource-intensive.)

## Versioning

(Explain the API versioning strategy.) 
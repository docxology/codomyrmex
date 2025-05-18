---
id: build-synthesis-api-specification
title: Build Synthesis - API Specification
sidebar_label: API Specification
---

# Build Synthesis - API Specification

## Introduction

This API allows for programmatic control over the build processes managed by the Build Synthesis module.

## Endpoints / Functions / Interfaces

### Endpoint/Function 1: `trigger_build()`

- **Description**: Initiates a build for a specified module or target.
- **Method**: POST (if HTTP API)
- **Path**: `/api/build_synthesis/trigger`
- **Parameters/Arguments**:
    - `module_name` (string): The name of the Codomyrmex module to build.
    - `build_target` (string, optional): Specific target within the module's build process (e.g., `docker_image`, `python_wheel`, `web_app`). Default: `default`.
    - `clean_build` (boolean, optional): Whether to perform a clean build. Default: `false`.
    - `build_parameters` (object, optional): Key-value pairs for specific build parameters.
- **Request Body**:
    ```json
    {
      "module_name": "data_visualization",
      "build_target": "production_bundle",
      "clean_build": true
    }
    ```
- **Returns/Response**:
    - **Success (e.g., 202 Accepted)**:
        ```json
        {
          "build_id": "build_job_456",
          "status_url": "/api/build_synthesis/status/build_job_456",
          "message": "Build triggered for data_visualization module."
        }
        ```
    - **Error (e.g., 400 Bad Request)**:
        ```json
        {
          "error": "Module 'unknown_module' not found or build target invalid."
        }
        ```

### Endpoint/Function 2: `get_build_status()`

- **Description**: Retrieves the status of an ongoing or completed build.
- **Method**: GET
- **Path**: `/api/build_synthesis/status/{build_id}`
- **Returns/Response**:
    - **Success (200 OK)**:
        ```json
        {
          "build_id": "build_job_456",
          "module_name": "data_visualization",
          "status": "succeeded", // e.g., pending, running, succeeded, failed
          "start_time": "YYYY-MM-DDTHH:MM:SSZ",
          "end_time": "YYYY-MM-DDTHH:MM:SSZ",
          "logs_url": "/api/build_synthesis/logs/build_job_456",
          "artifacts": [
            {"name": "bundle.js", "url": "/artifacts/data_visualization/bundle.js"}
          ]
        }
        ```

## Data Models

### Model: `BuildArtifact`
- `name` (string): Name of the artifact.
- `url` (string): Path or URL to access the artifact.
- `size` (integer, optional): Size in bytes.

## Authentication & Authorization

(Access to trigger builds might be restricted based on user roles or API keys.) 
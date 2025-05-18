---
sidebar_label: 'MCP Tool Specification'
title: 'Git Operations - MCP Tool Specification'
---

# Git Operations - MCP Tool Specification

This document outlines the specification for tools within the Git Operations module that are intended to be integrated with the Model Context Protocol (MCP).

## Tool: `git_clone_repository`

### 1. Tool Purpose and Description

Clones a remote Git repository to a specified local path. This tool allows an AI agent to fetch source code or other version-controlled assets.

### 2. Invocation Name

`git_clone_repository`

### 3. Input Schema (Parameters)

**Format:** Table

| Parameter Name  | Type     | Required | Description                                  | Example Value                                      |
| :-------------- | :------- | :------- | :------------------------------------------- | :------------------------------------------------- |
| `repository_url`| `string` | Yes      | The URL of the remote Git repository (HTTPS or SSH). | `"https://github.com/user/repo.git"`               |
| `local_path`    | `string` | Yes      | The local directory path to clone into.      | `"/path/to/local/clone"`                           |
| `branch_name`   | `string` | No       | Specific branch to clone. Defaults to the repository's default branch. | `"develop"`                                       |

**JSON Schema Example:**

```json
{
  "type": "object",
  "properties": {
    "repository_url": {
      "type": "string",
      "description": "The URL of the remote Git repository (HTTPS or SSH)."
    },
    "local_path": {
      "type": "string",
      "description": "The local directory path to clone into."
    },
    "branch_name": {
      "type": "string",
      "description": "Specific branch to clone. Defaults to the repository's default branch."
    }
  },
  "required": ["repository_url", "local_path"]
}
```

### 4. Output Schema (Return Value)

**Format:** JSON

```json
{
  "status": "success" | "failure",
  "message": "string", // e.g., "Repository cloned successfully to /path/to/local/clone" or "Error: Cloning failed."
  "local_path_created": "string | null" // Path to the cloned repo on success, null on failure
}
```

**JSON Schema Example:**

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "failure"],
      "description": "Indicates the outcome of the clone operation."
    },
    "message": {
      "type": "string",
      "description": "A human-readable message describing the outcome."
    },
    "local_path_created": {
      "type": ["string", "null"],
      "description": "The absolute path where the repository was cloned on success, otherwise null."
    }
  },
  "required": ["status", "message"]
}
```

### 5. Error Handling

- **Failure Status**: If `status` is `"failure"`, the `message` field will contain a description of the error (e.g., "Authentication failed", "Repository not found", "Destination path already exists and is not an empty directory").
- Underlying Git command errors (e.g., from `git clone`) will be caught and translated into a meaningful failure message.

### 6. Idempotency

- Idempotent: No. Attempting to clone to the same `local_path` where a repository (or other files) already exists will typically fail if the directory is not empty.
- Side Effects: Creates a new directory and populates it with the repository content.

### 7. Usage Examples (for MCP context)

**Example 1: Basic Clone**

```json
{
  "tool_name": "git_clone_repository",
  "arguments": {
    "repository_url": "https://github.com/Codomyrmex/codomyrmex.git",
    "local_path": "./temp_codomyrmex_clone"
  }
}
```

**Example 2: Clone a Specific Branch**

```json
{
  "tool_name": "git_clone_repository",
  "arguments": {
    "repository_url": "https://github.com/Codomyrmex/codomyrmex.git",
    "local_path": "./temp_codomyrmex_dev_clone",
    "branch_name": "development"
  }
}
```

### 8. Security Considerations

- **Repository Source**: The tool will attempt to clone from any provided URL. Agents should be vetted or restricted in their ability to specify arbitrary repository URLs if running in a sensitive environment.
- **Filesystem Access**: The tool writes to the local filesystem at the specified `local_path`. Ensure the process running the tool has appropriate permissions and that the `local_path` is within an allowed directory.
- **Git Vulnerabilities**: Relies on the system's Git installation. Ensure Git is kept up-to-date to mitigate known vulnerabilities in Git itself.
- **SSH Keys/Credentials**: If SSH URLs are used, the system must be pre-configured with appropriate SSH keys. For HTTPS, credential helpers or manual input might be required by Git, which this tool does not directly manage.

---

(Other Git operation tools like `git_commit`, `git_push`, `git_pull`, `git_create_branch`, `git_status` would be defined here with similar structures, corresponding to the API specification.) 
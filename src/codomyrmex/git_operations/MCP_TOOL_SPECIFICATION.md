# Git Operations - MCP Tool Specification

This document outlines the specification for tools within the Git Operations module that are integrated with the Model Context Protocol (MCP). These tools are defined in `mcp_tools.py` and exposed via the `@mcp_tool` decorator.

## General Considerations

- **Tool Integration**: This module provides version control automation and Git workflow management.
- **Configuration**: Operations are performed relative to a repository root, which can be specified or auto-detected.
- **Implementation**: All tools are defined in `mcp_tools.py` using the `@mcp_tool` decorator.

---

## Tool: `git_check_availability`

### 1. Tool Purpose and Description

Check if git is available on the current system.

### 2. Invocation Name

`codomyrmex.git_check_availability`

### 3. Input Schema (Parameters)

No parameters required.

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` | `"ok"` |
| `git_available` | `boolean` | Whether git is installed | `true` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_is_repo`

### 1. Tool Purpose and Description

Check if a directory is a git repository.

### 2. Invocation Name

`codomyrmex.git_is_repo`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to check | `"/projects/myapp"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `is_git_repository` | `boolean` | Whether path is a git repo | `true` |
| `path` | `string` | Checked path | `"/projects/myapp"` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_repo_status`

### 1. Tool Purpose and Description

Gets the current status of a Git repository, including staged/unstaged changes, untracked files, and branch information.

### 2. Invocation Name

`codomyrmex.git_repo_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `git_status` | `object` | Status information from `get_status()` | `{...}` |

### 5. Error Handling

- Returns `{"status": "error", "error": "<message>"}` if path is not a Git repository.

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_current_branch`

### 1. Tool Purpose and Description

Get the current branch name of a git repository.

### 2. Invocation Name

`codomyrmex.git_current_branch`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `branch` | `string` | Current branch name | `"main"` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_diff`

### 1. Tool Purpose and Description

Get the diff of uncommitted changes in a git repository.

### 2. Invocation Name

`codomyrmex.git_diff`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |
| `staged` | `boolean` | No | Show staged changes only (default: `false`) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `diff` | `string` | Diff output | `"diff --git..."` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_log`

### 1. Tool Purpose and Description

Get recent commit history for a git repository.

### 2. Invocation Name

`codomyrmex.git_log`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |
| `max_count` | `integer` | No | Maximum commits to return (default: 10) | `20` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `commits` | `array` | List of commit objects | `[...]` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_init`

### 1. Tool Purpose and Description

Initialize a new git repository at the given path.

### 2. Invocation Name

`codomyrmex.git_init`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path where to initialize the repo | `"/projects/new-app"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `initialized` | `boolean` | Whether initialization succeeded | `true` |
| `path` | `string` | Repository path | `"/projects/new-app"` |
| `result` | `any` | Result from `initialize_git_repository()` | `...` |

### 5. Idempotency

- **Idempotent**: No. Fails if already initialized.

---

## Tool: `git_clone`

### 1. Tool Purpose and Description

Clone a git repository from a URL to a local path.

### 2. Invocation Name

`codomyrmex.git_clone`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `url` | `string` | Yes | Repository URL to clone | `"https://github.com/org/repo.git"` |
| `path` | `string` | Yes | Local destination path | `"/projects/repo"` |
| `branch` | `string` | No | Branch to clone (default: default branch) | `"develop"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `cloned` | `boolean` | Whether clone succeeded | `true` |
| `result` | `any` | Result from `clone_repository()` | `...` |

### 5. Idempotency

- **Idempotent**: No. Fails if destination path already exists.

---

## Tool: `git_commit`

### 1. Tool Purpose and Description

Stage files and create a commit with a message.

### 2. Invocation Name

`codomyrmex.git_commit`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `message` | `string` | Yes | Commit message | `"Fix login bug"` |
| `files` | `array[string]` | No | Specific files to stage before commit | `["src/auth.py"]` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `committed` | `boolean` | Whether commit succeeded | `true` |
| `result` | `any` | Result from `commit_changes()` | `...` |

### 5. Idempotency

- **Idempotent**: No. Creates a new commit each time.

---

## Tool: `git_create_branch`

### 1. Tool Purpose and Description

Create a new branch in a git repository.

### 2. Invocation Name

`codomyrmex.git_create_branch`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `branch_name` | `string` | Yes | Name for the new branch | `"feature/new-login"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `branch` | `string` | Branch name | `"feature/new-login"` |
| `result` | `any` | Result from `create_branch()` | `...` |

### 5. Idempotency

- **Idempotent**: No. Fails if branch already exists.

---

## Tool: `git_switch_branch`

### 1. Tool Purpose and Description

Switch to a different branch in a git repository.

### 2. Invocation Name

`codomyrmex.git_switch_branch`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `branch_name` | `string` | Yes | Branch to switch to | `"feature/new-login"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `branch` | `string` | Current branch after switch | `"feature/new-login"` |
| `result` | `any` | Result from `switch_branch()` | `...` |

### 5. Idempotency

- **Idempotent**: Yes (switching to current branch is a no-op).

---

## Tool: `git_pull`

### 1. Tool Purpose and Description

Pull latest changes from a remote git repository.

### 2. Invocation Name

`codomyrmex.git_pull`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |
| `remote` | `string` | No | Remote name (default: `"origin"`) | `"upstream"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `pulled` | `boolean` | Whether pull succeeded | `true` |
| `result` | `any` | Result from `pull_changes()` | `...` |

### 5. Idempotency

- **Idempotent**: Yes (if already up to date, returns success).

---

## Tool: `git_push`

### 1. Tool Purpose and Description

Push local commits to a remote git repository.

### 2. Invocation Name

`codomyrmex.git_push`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |
| `remote` | `string` | No | Remote name (default: `"origin"`) | `"upstream"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `pushed` | `boolean` | Whether push succeeded | `true` |
| `result` | `any` | Result from `push_changes()` | `...` |

### 5. Error Handling

- Returns `{"status": "error", "error": "<message>"}` on failures (remote not found, auth issues, etc.).

### 6. Idempotency

- **Idempotent**: Yes (if already pushed, returns success).

---

## Security Considerations (All Tools)

- **Path Validation**: Repository paths should be validated to prevent directory traversal.
- **Credential Handling**: Git credentials are managed by the system's git credential helper; never stored in tool responses.
- **Remote Operations**: `git_push`, `git_pull`, and `git_clone` perform network operations.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

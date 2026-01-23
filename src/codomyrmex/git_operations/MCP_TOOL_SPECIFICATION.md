# Git Operations - MCP Tool Specification

This document outlines the specification for tools within the Git Operations module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Tool Integration**: This module provides version control automation and Git workflow management.
- **Configuration**: Operations are performed relative to a repository root, which can be specified or auto-detected.

---

## Tool: `git_status`

### 1. Tool Purpose and Description

Gets the current status of a Git repository, including staged/unstaged changes, untracked files, and branch information.

### 2. Invocation Name

`git_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `repository_path` | `string` | No | Path to repository (default: current directory) | `"/path/to/repo"` |
| `include_untracked` | `boolean` | No | Include untracked files (default: true) | `true` |
| `include_ignored` | `boolean` | No | Include ignored files | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success" or "error" | `"success"` |
| `branch` | `string` | Current branch name | `"main"` |
| `ahead` | `integer` | Commits ahead of upstream | `2` |
| `behind` | `integer` | Commits behind upstream | `0` |
| `staged` | `array[object]` | Staged changes | `[{"file": "a.py", "status": "modified"}]` |
| `unstaged` | `array[object]` | Unstaged changes | `[{"file": "b.py", "status": "modified"}]` |
| `untracked` | `array[string]` | Untracked files | `["new_file.py"]` |
| `is_clean` | `boolean` | True if working directory is clean | `false` |

### 5. Error Handling

- **Not a Repository**: Returns error if path is not a Git repository
- **Corrupted Repository**: Returns error with details

### 6. Idempotency

- **Idempotent**: Yes

### 7. Usage Examples

```json
{
  "tool_name": "git_status",
  "arguments": {
    "repository_path": "/projects/myapp",
    "include_untracked": true
  }
}
```

### 8. Security Considerations

- **Path Validation**: Repository paths should be validated to prevent directory traversal

---

## Tool: `git_commit`

### 1. Tool Purpose and Description

Creates a new commit with the specified files and message.

### 2. Invocation Name

`git_commit`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `repository_path` | `string` | No | Path to repository | `"/path/to/repo"` |
| `message` | `string` | Yes | Commit message | `"Fix login bug"` |
| `files` | `array[string]` | No | Specific files to commit (default: all staged) | `["src/auth.py"]` |
| `author` | `string` | No | Author override | `"John <john@example.com>"` |
| `allow_empty` | `boolean` | No | Allow empty commits | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success" or "error" | `"success"` |
| `commit_hash` | `string` | Full commit SHA | `"abc123..."` |
| `short_hash` | `string` | Short commit SHA | `"abc123"` |
| `files_committed` | `integer` | Number of files in commit | `3` |
| `insertions` | `integer` | Lines added | `25` |
| `deletions` | `integer` | Lines removed | `10` |

### 5. Error Handling

- **Nothing to Commit**: Returns error if no changes to commit
- **Merge Conflict**: Returns error if unresolved conflicts exist
- **Pre-commit Hook Failure**: Returns error with hook output

### 6. Idempotency

- **Idempotent**: No, creates new commit each time

---

## Tool: `git_branch`

### 1. Tool Purpose and Description

Manages Git branches - create, delete, list, or switch branches.

### 2. Invocation Name

`git_branch`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `repository_path` | `string` | No | Path to repository | `"/path/to/repo"` |
| `action` | `string` | Yes | Action: "list", "create", "delete", "checkout" | `"create"` |
| `branch_name` | `string` | Conditional | Branch name (required for create/delete/checkout) | `"feature/new-login"` |
| `start_point` | `string` | No | Starting point for new branch | `"main"` |
| `force` | `boolean` | No | Force operation | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success" or "error" | `"success"` |
| `branches` | `array[object]` | List of branches (for "list" action) | See below |
| `current_branch` | `string` | Current branch after operation | `"feature/new-login"` |

**Branch object structure (for list action):**

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `name` | `string` | Branch name |
| `is_current` | `boolean` | Whether this is the current branch |
| `upstream` | `string` | Upstream tracking branch |
| `last_commit` | `string` | Last commit hash |

### 5. Error Handling

- **Branch Exists**: Returns error when creating existing branch
- **Branch Not Found**: Returns error when deleting/checking out non-existent branch
- **Uncommitted Changes**: Returns error if checkout would overwrite changes

### 6. Idempotency

- **Idempotent**: list=Yes, create=No (fails if exists), delete=Yes, checkout=Yes

---

## Tool: `git_diff`

### 1. Tool Purpose and Description

Shows differences between commits, branches, or working directory.

### 2. Invocation Name

`git_diff`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `repository_path` | `string` | No | Path to repository | `"/path/to/repo"` |
| `target` | `string` | No | Commit/branch to compare against | `"HEAD~1"` |
| `source` | `string` | No | Source commit/branch (default: working dir) | `"main"` |
| `files` | `array[string]` | No | Specific files to diff | `["src/auth.py"]` |
| `stat_only` | `boolean` | No | Only show statistics | `false` |
| `context_lines` | `integer` | No | Number of context lines | `3` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success" or "error" | `"success"` |
| `diff` | `string` | Full diff output | `"diff --git..."` |
| `files_changed` | `integer` | Number of files changed | `5` |
| `insertions` | `integer` | Lines added | `100` |
| `deletions` | `integer` | Lines removed | `50` |
| `file_stats` | `array[object]` | Per-file statistics | See below |

### 5. Error Handling

- **Invalid Reference**: Returns error if commit/branch doesn't exist
- **Binary Files**: Indicates when diff contains binary files

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_log`

### 1. Tool Purpose and Description

Shows commit history with customizable formatting and filtering.

### 2. Invocation Name

`git_log`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `repository_path` | `string` | No | Path to repository | `"/path/to/repo"` |
| `branch` | `string` | No | Branch to show history for | `"main"` |
| `limit` | `integer` | No | Maximum commits to return | `10` |
| `since` | `string` | No | Show commits since date | `"2024-01-01"` |
| `author` | `string` | No | Filter by author | `"john@example.com"` |
| `path` | `string` | No | Filter by file path | `"src/"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | "success" or "error" | `"success"` |
| `commits` | `array[object]` | List of commits | See below |
| `total_count` | `integer` | Total matching commits | `150` |

**Commit object structure:**

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `hash` | `string` | Full commit SHA |
| `short_hash` | `string` | Short commit SHA |
| `author` | `string` | Author name and email |
| `date` | `string` | Commit date (ISO format) |
| `message` | `string` | Commit message |
| `files_changed` | `integer` | Number of files changed |

### 5. Error Handling

- **Invalid Branch**: Returns error if branch doesn't exist
- **Invalid Date Format**: Returns error for malformed date

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_push`

### 1. Tool Purpose and Description

Pushes local commits to a remote repository.

### 2. Invocation Name

`git_push`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `repository_path` | `string` | No | Path to repository | `"/path/to/repo"` |
| `remote` | `string` | No | Remote name (default: origin) | `"origin"` |
| `branch` | `string` | No | Branch to push (default: current) | `"main"` |
| `force` | `boolean` | No | Force push (use with caution) | `false` |
| `set_upstream` | `boolean` | No | Set upstream tracking | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `status` | `string` | "success" or "error" |
| `commits_pushed` | `integer` | Number of commits pushed |
| `remote_url` | `string` | URL of the remote |

### 5. Error Handling

- **Remote Not Found**: Returns error if remote doesn't exist
- **Push Rejected**: Returns error if push is rejected (need pull)
- **Authentication Failed**: Returns error for auth issues

### 6. Idempotency

- **Idempotent**: Yes (if already pushed, returns success)

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

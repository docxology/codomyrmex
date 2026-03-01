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

## Tool: `git_delete_branch`

### 1. Tool Purpose and Description

Delete a local branch. Use `force=True` to delete unmerged branches.

### 2. Invocation Name

`codomyrmex.git_delete_branch`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `branch_name` | `string` | Yes | Branch to delete | `"feature/old-work"` |
| `force` | `boolean` | No | Force-delete unmerged branch (default: `false`) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `branch` | `string` | Deleted branch name | `"feature/old-work"` |
| `deleted` | `any` | Result from `delete_branch()` | `...` |

### 5. Idempotency

- **Idempotent**: No. Fails if branch does not exist.

---

## Tool: `git_merge`

### 1. Tool Purpose and Description

Merge a source branch into a target branch (or the current branch if target is omitted).

### 2. Invocation Name

`codomyrmex.git_merge`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `source_branch` | `string` | Yes | Branch to merge from | `"feature/login"` |
| `target_branch` | `string` | No | Branch to merge into (default: current branch) | `"main"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `merged` | `any` | Result from `merge_branch()` | `...` |
| `source` | `string` | Source branch name | `"feature/login"` |
| `target` | `string` | Target branch name | `"main"` |

### 5. Idempotency

- **Idempotent**: No. Creates a merge commit each time.

---

## Tool: `git_rebase`

### 1. Tool Purpose and Description

Rebase the current branch onto a target branch.

### 2. Invocation Name

`codomyrmex.git_rebase`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `target_branch` | `string` | Yes | Branch to rebase onto | `"main"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `rebased` | `any` | Result from `rebase_branch()` | `...` |
| `target` | `string` | Target branch | `"main"` |

### 5. Idempotency

- **Idempotent**: No. Rewrites commit history.

---

## Tool: `git_cherry_pick`

### 1. Tool Purpose and Description

Cherry-pick a specific commit onto the current branch.

### 2. Invocation Name

`codomyrmex.git_cherry_pick`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `commit_sha` | `string` | Yes | SHA of the commit to cherry-pick | `"a1b2c3d"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `cherry_picked` | `any` | Result from `cherry_pick()` | `...` |
| `commit` | `string` | Commit SHA | `"a1b2c3d"` |

### 5. Idempotency

- **Idempotent**: No. Creates a new commit each time.

---

## Tool: `git_revert`

### 1. Tool Purpose and Description

Revert a specific commit by creating a new inverse commit.

### 2. Invocation Name

`codomyrmex.git_revert`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `commit_sha` | `string` | Yes | SHA of the commit to revert | `"a1b2c3d"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `reverted` | `any` | Result from `revert_commit()` | `...` |
| `commit` | `string` | Reverted commit SHA | `"a1b2c3d"` |

### 5. Idempotency

- **Idempotent**: No. Creates a new revert commit each time.

---

## Tool: `git_reset`

### 1. Tool Purpose and Description

Reset the repository to a commit using soft, mixed, or hard mode.

### 2. Invocation Name

`codomyrmex.git_reset`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `mode` | `string` | No | Reset mode: `"soft"`, `"mixed"`, or `"hard"` (default: `"mixed"`) | `"hard"` |
| `target` | `string` | No | Commit to reset to (default: `"HEAD"`) | `"HEAD~3"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `reset` | `any` | Result from `reset_changes()` | `...` |
| `mode` | `string` | Reset mode used | `"hard"` |
| `target` | `string` | Target commit | `"HEAD~3"` |

### 5. Idempotency

- **Idempotent**: Yes (resetting to the same target is a no-op).

---

## Tool: `git_amend`

### 1. Tool Purpose and Description

Amend the most recent commit message or content.

### 2. Invocation Name

`codomyrmex.git_amend`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `message` | `string` | No | New commit message (default: keep existing) | `"Updated commit msg"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `amended_sha` | `any` | New commit SHA after amend | `"d4e5f6g"` |

### 5. Idempotency

- **Idempotent**: No. Rewrites the most recent commit.

---

## Tool: `git_stash`

### 1. Tool Purpose and Description

Stash uncommitted changes with an optional description message.

### 2. Invocation Name

`codomyrmex.git_stash`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |
| `message` | `string` | No | Description for the stash entry | `"WIP: login feature"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `stashed` | `any` | Result from `stash_changes()` | `...` |

### 5. Idempotency

- **Idempotent**: No. Creates a new stash entry each time.

---

## Tool: `git_stash_apply`

### 1. Tool Purpose and Description

Apply a stash entry to the working directory.

### 2. Invocation Name

`codomyrmex.git_stash_apply`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |
| `stash_ref` | `string` | No | Stash reference to apply (default: latest) | `"stash@{2}"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `applied` | `any` | Result from `apply_stash()` | `...` |

### 5. Idempotency

- **Idempotent**: Yes (applying the same stash twice may conflict but does not create new state).

---

## Tool: `git_stash_list`

### 1. Tool Purpose and Description

List all stash entries in the repository.

### 2. Invocation Name

`codomyrmex.git_stash_list`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `stashes` | `array` | List of stash entries | `[...]` |
| `count` | `integer` | Number of stash entries | `3` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_create_tag`

### 1. Tool Purpose and Description

Create a lightweight or annotated tag at the current commit.

### 2. Invocation Name

`codomyrmex.git_create_tag`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `tag_name` | `string` | Yes | Tag name | `"v1.2.0"` |
| `message` | `string` | No | Annotation message (creates annotated tag if provided) | `"Release 1.2.0"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `tag` | `string` | Tag name | `"v1.2.0"` |
| `created` | `any` | Result from `create_tag()` | `...` |

### 5. Idempotency

- **Idempotent**: No. Fails if tag already exists.

---

## Tool: `git_list_tags`

### 1. Tool Purpose and Description

List all tags in the repository.

### 2. Invocation Name

`codomyrmex.git_list_tags`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `tags` | `array` | List of tag names | `["v1.0.0", "v1.1.0"]` |
| `count` | `integer` | Number of tags | `2` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_fetch`

### 1. Tool Purpose and Description

Fetch changes from a remote repository without merging.

### 2. Invocation Name

`codomyrmex.git_fetch`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |
| `remote` | `string` | No | Remote name (default: `"origin"`) | `"upstream"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `fetched` | `any` | Result from `fetch_changes()` | `...` |
| `remote` | `string` | Remote name | `"origin"` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_add_remote`

### 1. Tool Purpose and Description

Add a named remote URL to the repository.

### 2. Invocation Name

`codomyrmex.git_add_remote`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `name` | `string` | Yes | Remote name | `"upstream"` |
| `url` | `string` | Yes | Remote URL | `"https://github.com/org/repo.git"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `added` | `any` | Result from `add_remote()` | `...` |
| `name` | `string` | Remote name | `"upstream"` |
| `url` | `string` | Remote URL | `"https://github.com/org/repo.git"` |

### 5. Idempotency

- **Idempotent**: No. Fails if remote name already exists.

---

## Tool: `git_remove_remote`

### 1. Tool Purpose and Description

Remove a named remote from the repository.

### 2. Invocation Name

`codomyrmex.git_remove_remote`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `name` | `string` | Yes | Remote name to remove | `"upstream"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `removed` | `any` | Result from `remove_remote()` | `...` |
| `name` | `string` | Removed remote name | `"upstream"` |

### 5. Idempotency

- **Idempotent**: No. Fails if remote does not exist.

---

## Tool: `git_list_remotes`

### 1. Tool Purpose and Description

List all configured remotes for the repository.

### 2. Invocation Name

`codomyrmex.git_list_remotes`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | No | Path to repository (default: `"."`) | `"/path/to/repo"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `remotes` | `array` | List of remote objects | `[...]` |
| `count` | `integer` | Number of remotes | `2` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_blame`

### 1. Tool Purpose and Description

Show git blame output for a file (line-by-line commit attribution).

### 2. Invocation Name

`codomyrmex.git_blame`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `file_path` | `string` | Yes | File to blame | `"src/auth.py"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `blame` | `any` | Blame output from `get_blame()` | `...` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_commit_details`

### 1. Tool Purpose and Description

Get detailed metadata for a specific commit by SHA.

### 2. Invocation Name

`codomyrmex.git_commit_details`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `commit_sha` | `string` | Yes | Commit SHA to inspect | `"a1b2c3d"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `commit` | `object` | Commit metadata from `get_commit_details()` | `{...}` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_get_config`

### 1. Tool Purpose and Description

Read a git configuration value by key.

### 2. Invocation Name

`codomyrmex.git_get_config`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `key` | `string` | Yes | Config key to read | `"user.email"` |
| `global_config` | `boolean` | No | Read from global config (default: `false`) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `key` | `string` | Config key | `"user.email"` |
| `value` | `string` | Config value | `"dev@example.com"` |

### 5. Idempotency

- **Idempotent**: Yes

---

## Tool: `git_set_config`

### 1. Tool Purpose and Description

Set a git configuration value (local or global scope).

### 2. Invocation Name

`codomyrmex.git_set_config`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `key` | `string` | Yes | Config key to set | `"user.email"` |
| `value` | `string` | Yes | Config value | `"dev@example.com"` |
| `global_config` | `boolean` | No | Set in global config (default: `false`) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `key` | `string` | Config key | `"user.email"` |
| `value` | `string` | Config value | `"dev@example.com"` |
| `set` | `any` | Result from `set_config()` | `...` |

### 5. Idempotency

- **Idempotent**: Yes (setting the same value is a no-op).

---

## Tool: `git_clean`

### 1. Tool Purpose and Description

WARNING: Irreversible. Deletes untracked files from the working tree.

### 2. Invocation Name

`codomyrmex.git_clean`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `path` | `string` | Yes | Path to repository | `"/path/to/repo"` |
| `force` | `boolean` | No | Force clean (default: `false`) | `true` |
| `directories` | `boolean` | No | Also remove untracked directories (default: `false`) | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `cleaned` | `any` | Result from `clean_repository()` | `...` |

### 5. Idempotency

- **Idempotent**: Yes (cleaning an already-clean tree is a no-op).

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

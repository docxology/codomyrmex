# Git Agent -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `git_agent` module provides a `GitAgent` class that wraps Git and GitHub operations behind the standard `BaseAgent` interface. It parses structured command prompts and dispatches them to the `git_operations` module, enabling automated repository management within agentic workflows.

## Architecture

Command-dispatch pattern: `GitAgent._execute_impl` parses the incoming prompt (JSON or colon-delimited string) into an action name and parameter dict, then delegates to `_handle_action` which routes to the appropriate `RepositoryManager` method or `git_operations` function.

## Key Classes

### `GitAgent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict\|None, repository_manager: RepositoryManager\|None` | -- | Initialize with optional config and repository manager (defaults to `RepositoryManager()`) |
| `_execute_impl` | `request: AgentRequest` | `AgentResponse` | Parse prompt into action + params, dispatch via `_handle_action` |
| `_handle_action` | `action: str, params: dict` | `Any` | Route to specific Git/GitHub operation |
| `stream` | `request: AgentRequest` | `Iterator[str]` | Yields single chunk from `execute()` (streaming not natively supported) |

### Supported Actions

| Action | Required Params | Delegates To |
|--------|----------------|-------------|
| `sync` | `repository` | `RepositoryManager.sync_repository` |
| `prune` | `repository` | `RepositoryManager.prune_repository` |
| `clean` | `repository`, optional `force` | `git_operations.core.git.clean_repository` |
| `status` | `repository` | `RepositoryManager.get_repository_status` |
| `list_remotes` | `repository` | `git_operations.core.git.list_remotes` |
| `add_remote` | `repository`, `name`, `url` | `git_operations.core.git.add_remote` |
| `create_issue` | `owner`, `repo_name`, `title`, optional `body`, `labels` | `git_operations.api.github.create_issue` |
| `list_issues` | `owner`, `repo_name`, optional `state` | `git_operations.api.github.list_issues` |

## Dependencies

- **Internal**: `codomyrmex.agents.core.base` (BaseAgent, AgentRequest, AgentResponse, AgentCapabilities), `codomyrmex.git_operations.core.git`, `codomyrmex.git_operations.core.repository`, `codomyrmex.git_operations.api.github`, `codomyrmex.logging_monitoring`
- **External**: None beyond stdlib (`json`)

## Constraints

- Prompt format must be valid JSON or `action: key=value, key=value` -- free-form natural language is not parsed.
- Repository lookup via `RepositoryManager.get_repository` must succeed or `ValueError` is raised.
- `clean` with `force=true` performs irreversible deletion of untracked files and directories.
- Zero-mock: real Git operations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ValueError` raised for missing required parameters, unknown actions, or repository-not-found conditions.
- All exceptions are caught in `_execute_impl`, logged via `logger.exception`, and returned as `AgentResponse(error=...)`.
- No silent fallbacks: invalid prompts return an explicit error response, not empty content.

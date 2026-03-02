# Codomyrmex Agents -- src/codomyrmex/agents/git_agent

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Specialized agent for automated Git and GitHub operations. Accepts structured commands (JSON or `action: key=value` format) and dispatches them to `RepositoryManager` and `git_operations` functions for repository sync, clean, prune, remote management, and GitHub issue CRUD.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `agent.py` | `GitAgent` | BaseAgent subclass that parses structured prompts into action dispatches; supports `sync`, `prune`, `clean`, `status`, `list_remotes`, `add_remote`, `create_issue`, and `list_issues` actions |
| `__init__.py` | -- | Exports `GitAgent` |

## Operating Contracts

- `GitAgent._execute_impl` expects prompts in either JSON format (`{"action": "sync", "repository": "owner/repo"}`) or colon-separated format (`sync: repository=owner/repo`).
- All actions that operate on a repository require a `repository` parameter; `ValueError` is raised if missing.
- `clean` action delegates to `git_operations.core.git.clean_repository` with `force` and `directories` flags.
- GitHub issue actions (`create_issue`, `list_issues`) delegate to `git_operations.api.github` functions and require `owner` and `repo_name` parameters.
- Streaming is not natively supported; `stream()` yields the full `execute()` result as a single chunk.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.agents.core.base` (BaseAgent, AgentRequest, AgentResponse, AgentCapabilities), `codomyrmex.git_operations.core.git` (add_remote, clean_repository, list_remotes), `codomyrmex.git_operations.core.repository` (RepositoryManager), `codomyrmex.git_operations.api.github` (create_issue, list_issues), `codomyrmex.logging_monitoring`
- **Used by**: Agent orchestrator, PAI BUILD/EXECUTE phases for automated version control workflows

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Root](../../../../README.md)

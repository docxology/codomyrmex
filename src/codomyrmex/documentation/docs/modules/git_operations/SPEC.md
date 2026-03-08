# Git Operations -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Core Functionality
- The module shall provide git operations capabilities as described in the module docstring.
- The module shall export 51 public symbols via `__all__`.

### FR-2: MCP Integration
- The module shall expose 32 MCP tools for agent consumption.

## Interface Contracts

### MCP Tool Signatures

- `git_check_availability()`
- `git_is_repo()`
- `git_current_branch()`
- `git_diff()`
- `git_log()`
- `git_init()`
- `git_clone()`
- `git_commit()`
- `git_create_branch()`
- `git_switch_branch()`
- `git_list_branches()`
- `git_pull()`
- `git_push()`
- `git_delete_branch()`
- `git_merge()`
- `git_rebase()`
- `git_cherry_pick()`
- `git_revert()`
- `git_reset()`
- `git_amend()`
- `git_stash()`
- `git_stash_apply()`
- `git_stash_list()`
- `git_create_tag()`
- `git_list_tags()`
- `git_fetch()`
- `git_add_remote()`
- `git_remove_remote()`
- `git_list_remotes()`
- `git_commit_details()`
- `git_get_config()`
- `git_clean()`

## Non-Functional Requirements

### NFR-1: Zero-Mock Testing
- All tests follow the Zero-Mock policy -- no unittest.mock, MagicMock, or monkeypatch.

### NFR-2: Explicit Failure
- All failures shall raise exceptions; no silent fallbacks or placeholder returns.

## Navigation

- **Source**: [src/codomyrmex/git_operations/](../../../../src/codomyrmex/git_operations/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)

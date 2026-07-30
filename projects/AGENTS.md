<!-- agents: curated -->

# Agent guidance for project workspaces

## Purpose

Preserve ownership and Git boundaries for integration and example workspaces.

## Development Guidelines

- Detect nested `.git` directories or gitfiles before editing.
- Treat every nested repository as an independent worktree with its own status,
  history, remotes, and agent instructions.
- Never fold nested changes into root formatting, cleanup, documentation
  generation, or release claims.
- Run commands from the owning workspace only after reading its README,
  AGENTS, and package metadata.
- Keep root documentation limited to workspace ownership and integration
  boundaries; detailed behavior belongs with the workspace.
- Do not infer that a historically documented workspace still exists.

## Key Files

- [README.md](README.md) — current workspace inventory and safety boundary
- [SPEC.md](SPEC.md) — workspace specification
- `test_project/` — current standalone nested worktree

## Current scope

The current checkout contains `projects/test_project/` as a nested Git
worktree. Recheck this fact live before acting.

## Navigation

- [Human overview](README.md)
- [Workspace specification](SPEC.md)
- [Repository agent contract](../AGENTS.md)

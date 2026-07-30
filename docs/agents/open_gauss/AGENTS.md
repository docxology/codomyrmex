<!-- agents: curated -->

# Agent guidance for OpenGauss documentation

## Purpose

This directory documents Codomyrmex's integration boundary with the OpenGauss
Git submodule. The human-facing overview is [README.md](README.md).

## Development Guidelines

- Treat [`src/codomyrmex/agents/open_gauss/`](../../../src/codomyrmex/agents/open_gauss/)
  as a separate Git worktree with its own history and instructions.
- Inspect both the superproject and submodule status before any operation that
  could update, clean, format, or test the submodule.
- Derive commands, versions, entry points, and supported workflows from the
  checked-out submodule. Do not reintroduce the removed
  `open_gauss_client.py` wrapper or fixed test-count claims.
- Keep Codomyrmex documentation focused on initialization, ownership, and
  navigation. Detailed OpenGauss behavior belongs in its upstream docs.
- Do not run broad documentation generators over this curated directory.
- Preserve credentials: examples may name environment variables but must never
  contain tokens or user-specific paths.

## Key Files

- [README.md](README.md) — integration and installation boundary
- [Submodule README](../../../src/codomyrmex/agents/open_gauss/README.md) —
  upstream operational authority
- [`.gitmodules`](../../../.gitmodules) — repository ownership declaration

## Validation

Check relative links with the package documentation gate and verify the
submodule boundary directly:

```bash
git status --short
git -C src/codomyrmex/agents/open_gauss status --short
uv run --locked python scripts/documentation/audit_readme_agents.py --strict
```

The last command is read-only apart from its reports under `output/`.

## Navigation

- [OpenGauss integration overview](README.md)
- [Agent documentation index](../README.md)
- [Repository agent contract](../../../AGENTS.md)
- [Submodule agent instructions](../../../src/codomyrmex/agents/open_gauss/AGENTS.md)

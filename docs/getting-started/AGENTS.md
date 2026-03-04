# Codomyrmex Agents — docs/getting-started

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination guidelines for the `docs/getting-started/` directory.

## Key Files

| File | Purpose |
|------|---------|
| `quickstart.md` | 5-minute quick start |
| `setup.md` | Full installation and environment config |
| `GETTING_STARTED_WITH_AGENTS.md` | Agent deployment, orchestration, MCP, skills |
| `tutorials/` | Hands-on learning guides (8 tutorials) |
| `installation.md` | Redirect to `setup.md` (legacy) |

## Agent Interaction Rules

1. **Use real examples**: All code snippets must use real, functional imports
2. **Keep prerequisites minimal**: Default to `uv sync` without optional extras
3. **Link to source**: Reference actual module paths (`src/codomyrmex/...`)
4. **Maintain cross-references**: Ensure links between docs are valid
5. **Zero-Mock policy**: No placeholder or mocked code examples

## Content Standards

- Tutorials must include runnable code blocks
- Version numbers must match `pyproject.toml`
- All file references must use relative paths
- Include navigation links (Parent, Root)

## Navigation

- **Parent**: [README.md](README.md)
- **Root**: [Project Root](../../README.md)

# AGENTS.md — `codomyrmex/.agents/skills/mcp-tool-use`

## Purpose
Portable repository-scoped skill: Use Model Context Protocol tools safely: schema inspection, least-privilege selection, explicit approvals, bounded execution, result verification. Defined entirely by [`SKILL.md`](SKILL.md).

## Layout
- `SKILL.md` — the skill definition (frontmatter: name, description).

## Gotchas
- Use whenever an MCP server or external tool is involved.
- Runtime adapters (`.cursor/skills/`, `.agent/skills/`) may mirror this skill; edit the canonical copy here first.

## Key Files
- `README.md`: Readme file

## Dependencies
- None

## Development Guidelines
- Follow standard practices

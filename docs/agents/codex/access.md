# Codex Access to Codomyrmex

**Status**: Active | **Last Updated**: June 2026

## Purpose

This guide shows the safe, repo-native path for Codex and sibling agents to see
what Codomyrmex can do before they execute tools or dispatch other agents.

## Read-Only Probes

```bash
uv run python scripts/agents/codex_access.py --json
uv run python scripts/agents/codex_access.py --check --json
uv run python scripts/agents/codex_access.py --dispatch-only --json
uv run python scripts/agents/improve_src.py --dry-run --limit 2 --json
```

The probes do not mutate trust state, run tests, call remote model APIs, sync
skill repositories, or launch agent workers.

Use `--check` when a workflow needs an exit-code gate. It returns nonzero if
any access surface reports a non-ready status.

## MCP Tools

| Tool | Safety | Purpose |
|:---|:---|:---|
| `codomyrmex.codex_access_status` | read-only | One payload covering MCP, skills, trust, Hermes, Codex, and dispatch readiness |
| `codomyrmex.codex_dispatch_catalog` | read-only | Multiagent dispatch paths classified before launch |
| `codomyrmex.codex_execute` | remote API call | Single-turn Codex API execution through `CodexClient` |

## Dispatch Classifications

| Classification | Meaning |
|:---|:---|
| `read_only` | Inspection only; no agent launch or state change |
| `dry_run` | Builds a manifest of intended work without dispatching it |
| `side_effectful` | May launch agents, invoke handlers, call services, or mutate external state |

Real multiagent work should start from a reviewed dry-run manifest. The current
source swarm dry run is:

```bash
uv run python scripts/agents/improve_src.py --dry-run --json
```

## Skill Surfaces

Codex can inspect three skill families:

- Markdown skill packs such as root `SKILL.md` and `src/codomyrmex/agents/pai/SKILL.md`.
- YAML skill packs under `src/codomyrmex/skills/skills/`.
- Python-discovery skills registered through `codomyrmex.skills.discovery`.

The access probe reports these as separate surfaces because they have different
runtime contracts and should not be treated as one registry.

## Navigation

- **Source module**: [../../../src/codomyrmex/agents/codex/](../../../src/codomyrmex/agents/codex/)
- **PAI tools**: [../../pai/tools-reference.md](../../pai/tools-reference.md)
- **Skills overview**: [../../skills/index.md](../../skills/index.md)

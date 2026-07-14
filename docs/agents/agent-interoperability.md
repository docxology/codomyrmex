# Agent Interoperability

Codomyrmex keeps the reasoning and safety workflows portable while leaving transport and permission settings to each runtime.

## Shared skills

The canonical repository-scoped skills live under `.agents/skills/`:

| Skill | Use it for |
| --- | --- |
| `first-principles` | Reduce a problem to verified facts, constraints, and decisions |
| `red-team` | Exercise realistic abuse, failure, and permission paths |
| `systems-thinking` | Trace dependencies, feedback loops, delays, and second-order effects |
| `mcp-tool-use` | Inspect, constrain, approve, execute, and verify tool calls |
| `agent-interop` | Transfer work between Codex, Claude Code, and Hermes |

They follow the portable [Agent Skills specification](https://agentskills.io/specification): concise frontmatter, progressive disclosure, and supporting resources only when needed. A runtime-specific adapter should point to these files rather than fork their logic.

## Runtime setup

### Codex

Codex discovers project skills from `.agents/skills/` and reads the project MCP configuration from [.codex/config.toml](../../.codex/config.toml). The checked-in server configuration deliberately allow-lists read-only tools and keeps approval mode at `prompt`.

Inspect the server from the repository root:

```bash
uv run python scripts/model_context_protocol/run_mcp_server.py --profile readonly --list-tools
codex mcp list
```

The server also supports a `full` profile for explicitly authorized local work, but the checked-in Codex and Claude examples use `readonly`. The [Codex MCP documentation](https://developers.openai.com/codex/mcp/) describes stdio and Streamable HTTP servers, tool filtering, timeouts, and approval modes. Project configuration is used only when the project is trusted by Codex.

### Claude Code

Claude Code discovers skills from `.claude/skills/` and project MCP servers from `.mcp.json`. The additive wrappers under `.claude/skills/` point to the canonical files without duplicating them. Use [config/claude_code_mcp.example.json](../../config/claude_code_mcp.example.json) as an explicit project opt-in, and read the matching portable skill under `.agents/skills/` when a Claude-specific wrapper is not present.

The [Claude Code skills documentation](https://code.claude.com/docs/en/skills) and [MCP documentation](https://code.claude.com/docs/en/mcp) describe project scope, approval prompts, and server management.

### Hermes

Hermes can discover the same portable skills through `skills.external_dirs`. Merge [config/hermes_external_skills.example.yaml](../../config/hermes_external_skills.example.yaml) into `~/.hermes/config.yaml`, replacing the placeholders with this checkout’s absolute path. The example also configures the readonly Codomyrmex MCP server. External skill directories are discovery-only and read-only; local Hermes skills take precedence.

Hermes MCP configuration supports stdio and HTTP servers and per-server filtering. Keep the server surface narrow; do not connect a broad command-execution surface when a read-only subset is enough. Verify the active setup with `hermes mcp test codomyrmex`. See the [Hermes skills guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) and [Hermes MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp).

## Tool-use contract

Use this sequence for every MCP server:

1. Inspect instructions, schemas, annotations, timeouts, and rate limits.
2. Select the smallest tool allow-list and bounded arguments that satisfy the task.
3. Confirm sensitive side effects before calling a mutating, shell, network, credential, or publication tool.
4. Validate the returned structure and independently check important side effects.
5. Record the call and evidence without logging secrets.

This follows the [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools), which treats tool annotations as untrusted unless the server is trusted and expects input validation, access control, rate limiting, output sanitization, confirmation for sensitive operations, timeouts, and logging.

## Reasoning composition

For a substantial change, compose the skills in this order:

```text
first-principles -> systems-thinking -> red-team -> mcp-tool-use -> agent-interop
```

Start by defining the outcome and facts, map system effects, attack the proposal, constrain the tools, then write a handoff with evidence and unresolved risk. Use the [first-principles primer](https://jamesclear.com/first-principles), [Meadows leverage-points paper](https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/), and OpenAI’s [human-and-AI red-teaming overview](https://openai.com/index/advancing-red-teaming-with-people-and-ai/) as conceptual references rather than as executable instructions.

## Change verification

Before changing a source symbol, run the repository’s GitNexus impact analysis and report the blast radius. Before committing, run GitNexus `detect_changes()` or the closest available local comparison. The local fallback is:

```bash
node .gitnexus/run.cjs impact <symbol> --direction upstream
node .gitnexus/run.cjs status
```

If the MCP tools are unavailable, say so explicitly and use the local CLI plus `git diff --name-only`, targeted tests, and runtime checks as evidence. Never claim that a GitNexus MCP analysis ran when it did not.

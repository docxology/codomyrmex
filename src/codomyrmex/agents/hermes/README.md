# Hermes Agent Module

**Version**: v2.5.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Hermes Agent Module integrates NousResearch's Hermes capabilities deeply into the Codomyrmex ecosystem. Designed for maximum reliability and local-first execution, it provides dual-backend scaling, persistent multi-turn chat, provider-agnostic routing, context compression, and specialized prompt templating. v2.5.0 adds a **git-based plugin system**, **@ context references**, a **gateway agent cache**, **Mattermost** support, and optional **meme-generation** and **bioinformatics** skills.

## Core Features

1. **Dual-Backend Auto-Detection**: The module seamlessly targets either the official `hermes` CLI binary or a local `ollama` instance. Fallback ensures availability without the CLI.

2. **Persistent Stateful Chat**: Using `SQLiteSessionStore`, the module tracks multi-turn conversational history natively — with session forking, merging, FTS5 search, and automated lifecycle management.

3. **Plugin System (v2.5.0)**:
   Install third-party Hermes plugins from any Git repository:
   ```bash
   hermes plugins install owner/repo          # GitHub shorthand
   hermes plugins update my-plugin            # git pull
   hermes plugins list                        # Rich table display
   ```
   Plugins live in `~/.hermes/plugins/` (respects `HERMES_HOME`). See [plugins.md](../../../../docs/agents/hermes/plugins.md).

4. **@ Context References (v2.5.0)**:
   Inline file, folder, git diff, and URL content into any gateway message:

   | Token | Expands To |
   |-------|-----------|
   | `@file:path` | File contents |
   | `@file:path:L-R` | Lines L–R |
   | `@folder:path` | Directory listing |
   | `@diff` / `@staged` | Git diffs |
   | `@git:N` | Last N commits |
   | `@url:https://...` | Web page |

   Hard limit: 50% of context window. See [context-references.md](../../../../docs/agents/hermes/context-references.md).

5. **Gateway Agent Cache (v2.5.0)**: `GatewayRunner` reuses `AIAgent` instances per session via config signature (model + provider + toolsets). System prompt frozen after first turn. Thread-safe. See [agent-cache.md](../../../../docs/agents/hermes/agent-cache.md).

6. **Multi-Platform Gateway**: Telegram, Discord (voice + text via RTP/DAVE E2EE), WhatsApp, **Mattermost** (v2.5.0).

7. **Batch Execution**: Parallel multi-prompt dispatch via `HermesClient.batch_execute()` for swarm-scale processing.

8. **Provider Router**: Unified `call_llm()` across OpenRouter, Ollama, Anthropic, OpenAI, z.ai, Nous. Credentials auto-resolved from env + `~/.hermes/.env`.

9. **Context Compression**: `ContextCompressor` progressively compresses conversations at configurable token thresholds.

10. **Cross-Session User Model**: Persists preferences, coding style observations, and summaries across sessions.

11. **MCP Tool Suite**: **55** `@mcp_tool` definitions in `mcp_tools.py` (see [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)).

12. **FastMCP Scaffold Lane**: `HermesClient.scaffold_fastmcp()` plus MCP tool `hermes_fastmcp_scaffold` generate a minimal FastMCP server package from `optional-skills/mcp/fastmcp/scaffold_fastmcp.py` for Codomyrmex↔Hermes integration work.

13. **Evolutionary Submodule**: DSPy-based GEPA prompt optimization via `evolution/` submodule.

## Optional Skills (v2.5.0)

| Skill | Description |
|-------|-------------|
| `meme-generation` | Real `.png` meme images via Pillow; 10 curated templates + imgflip API |
| `bioinformatics` | Gateway to 400+ bioSkills patterns and 33+ ClawBio pipelines |

```bash
hermes skills enable meme-generation
hermes skills enable bioinformatics
```

## Directory Structure

- `hermes_client.py`: `HermesClient` — dual-backend, sessions, worktrees, CLI flags, batch.
- `_provider_router.py`: `ProviderRouter`, `UserModel`, `ContextCompressor`, `MCPBridgeManager`.
- `session.py`: `SQLiteSessionStore` with FTS5, archiving, and lifecycle hooks.
- `mcp_tools.py`: 55 MCP tools (see `MCP_TOOL_SPECIFICATION.md`).
- `optional-skills/mcp/fastmcp/scaffold_fastmcp.py`: Built-in scaffold generator for FastMCP server packages.
- `templates/`: Built-in prompt templates (code review, debugging, documentation, decomposition).
- `scripts/`: Operational scripts (`run_chat.py`, `run_batch.py`, `run_health.py`, etc.).
- `evolution/`: GEPA self-improvement submodule.
- `gateway/`: Multi-platform gateway (Telegram, Discord, WhatsApp, Mattermost).
- `instance_templates/`: Config templates, `SOUL.md`, `.env.example`.

## Navigation

- **Parent Directory**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
- **Plugins Reference**: [plugins.md](../../../../docs/agents/hermes/plugins.md)
- **@ Context References**: [context-references.md](../../../../docs/agents/hermes/context-references.md)
- **Agent Cache**: [agent-cache.md](../../../../docs/agents/hermes/agent-cache.md)

# Hermes Agent - Functional Specification

**Version**: v2.5.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

To integrate NousResearch Hermes capabilities within the Codomyrmex agent ecosystem via a dual-backend client. This client exposes both stateless queries and stateful multi-turn persistent sessions, scaling flexibly between the official `hermes` CLI and local Ollama deployments. Provider routing, context compression, and cross-session user modeling ensure resilient, context-aware operation. v2.5.0 adds a **git-based plugin system** (`hermes plugins`), **@ context references** for inline file/git/URL injection, a **gateway agent cache** for per-session AIAgent reuse, optional **meme-generation** and **bioinformatics** skills, and a **Mattermost** gateway integration.

## Architecture

```mermaid
graph TD
    AC[Codomyrmex Agentic Clients] --> HC[HermesClient]
    HC --> |auto-detect| BD{Backend?}
    BD --> |CLI available| HCLI[hermes CLI]
    BD --> |Ollama fallback| OL[ollama run hermes3]

    HC -.-> |chat_session| SS[(SQLiteSessionStore)]
    HC -.-> |compress| CC[ContextCompressor]

    PR[ProviderRouter] --> |call_llm| HCLI
    PR --> |call_llm| OL
    PR --> |credentials| ENV[~/.hermes/.env]

    HCLI --> |skills| HS[Hermes Skills]
    HCLI --> |honcho| HO[Honcho Memory]
    HCLI --> |plugins| PL[~/.hermes/plugins/]
    REG[skill_registry + profile YAML] -.-> HC
    MCP[MCP Tools ×50] --> HC
    HC -.-> Base[CLIAgentBase]
    UM[UserModel] -.-> |context| HC
    MB[MCPBridgeManager] -.-> |hot-reload| HCLI
    Gateway[GatewayRunner] --> HC
    Gateway --> |Voice| VR[VoiceReceiver]
    Gateway --> |Agent Cache| AgC[AIAgent Cache]
    CTX[@ Context Reference] -.-> |expand| Gateway
    PL2[Platform: Mattermost] -.-> Gateway
```

## Core Requirements

1. **Dual-Backend**: Auto-detect the `hermes` CLI vs `ollama`; configurable via `hermes_backend`.
   - Supported values: `auto`, `cli`, `ollama`.
2. **Graceful Fallback**: If the CLI is not in `$PATH`, seamlessly fall back to Ollama with the `hermes3` model.
3. **Persistent Sessions**: The `HermesClient.chat_session` method MUST track conversation history via `SQLiteSessionStore` at `~/.codomyrmex/hermes_sessions.db`.
   - `ContextCompressor` auto-compresses long conversations before dispatch.
4. **Provider Routing**: `ProviderRouter` abstracts LLM invocation across OpenRouter, Ollama, Anthropic, OpenAI, z.ai, and Nous.
5. **Plugin System (v2.5.0)**: `hermes plugins install/update/remove/list` manages Git-sourced plugins in `~/.hermes/plugins/`.
   - Plugins ship a `plugin.yaml` manifest and optional `after-install.md`.
   - Path traversal protection enforced on all plugin names.
6. **@ Context References (v2.5.0)**: Messages may contain `@file:`, `@folder:`, `@diff`, `@staged`, `@git:N`, `@url:` tokens that are expanded before dispatch.
   - Hard limit: 50% of context window; soft limit: 25% (warning only).
   - File line ranges: `@file:path:L-R`.
   - Workspace sandbox: `allowed_root` confines path expansion.
7. **Gateway Agent Cache (v2.5.0)**: `GatewayRunner` caches one `AIAgent` per session keyed by a config signature (model, provider, toolsets, system_prompt MD5).
   - Same-config reuse: system prompt frozen across turns (no rebuild).
   - Rebuild triggers: model, provider, or toolset change.
   - In-place updates: `reasoning_config` and callbacks updated without eviction.
   - Eviction: on session reset or fallback activation.
8. **Mattermost Integration (v2.5.0)**: New messaging platform alongside Telegram, Discord, WhatsApp.
9. **Discord Voice Support (v2.2.0)**: `VoiceReceiver` for RTP capture and DAVE E2EE decryption.
10. **Standard Subclassing**: Inherits from `CLIAgentBase`.
11. **Zero-Mock Policy**: All tests must execute functional logic (e.g., use `echo` as proxy, not `MagicMock`).

## Model Context Protocol (MCP) Interface

The module exposes **55 tools** to the swarm (see `MCP_TOOL_SPECIFICATION.md`):

| Tool | Purpose | Category |
| :--- | :--- | :--- |
| `hermes_execute` | Single-turn, stateless execution | Core |
| `hermes_chat_session` | Multi-turn stateful chat | Core |
| `hermes_stream` | Real-time streaming output | Core |
| `hermes_batch_execute` | Parallel multi-prompt dispatch (v2.2.0) | Core |
| `hermes_set_system_prompt` | Persist system instructions to session (v2.2.0) | Core |
| `hermes_status` | Backend availability diagnostics | Diagnostic |
| `hermes_doctor` | Comprehensive health check (CLI v0.2.0+) | Diagnostic |
| `hermes_version` | CLI version info | Diagnostic |
| `hermes_provider_status` | Multi-provider credential status | Diagnostic |
| `hermes_skills_list` | Available Hermes skills (CLI only) | Skills |
| `hermes_skills_resolve` | Registry `skill_ids` → Hermes `-s` names | Skills |
| `hermes_skills_validate_registry` | Registry vs `hermes skills list` (CLI) | Skills |
| `hermes_fastmcp_scaffold` | Generate FastMCP scaffold package for Hermes MCP integration | Skills |
| `hermes_template_list` | Prompt template names | Templates |
| `hermes_template_render` | Template rendering with variables | Templates |
| `hermes_session_list` | All active session IDs | Sessions |
| `hermes_session_detail` | Rich metrics/last-message for session (v2.2.0) | Sessions |
| `hermes_session_stats` | Database-wide storage/count metrics (v2.2.0) | Sessions |
| `hermes_session_fork` | Copy history to new child session (v2.2.0) | Sessions |
| `hermes_session_export_md` | Export conversation to Markdown (v2.2.0) | Sessions |
| `hermes_session_merge` | Consolidate context (v2.2.1) | Sessions |
| `hermes_prune_sessions` | Archive and delete old sessions (v2.2.0) | Sessions |
| `hermes_rotation_status` | Free model health/cooldown (v2.2.1) | Diagnostic |
| `hermes_health_check` | Deep agentic diagnostics (v2.2.1) | Diagnostic |
| `hermes_session_clear` | Delete a session | Sessions |
| `hermes_session_search` | Search sessions by name | Sessions |
| `hermes_honcho_status` | Honcho AI memory status | Memory |
| `hermes_insights` | Usage analytics (tokens, costs, trends) | Analytics |
| `hermes_worktree_create` | Git worktree isolation for sessions | Isolation |
| `hermes_worktree_cleanup` | Worktree teardown | Isolation |
| `hermes_mcp_reload` | Hot-reload MCP server config | Admin |
| `hermes_user_context` | Cross-session user model management | User Model |
| `hermes_plugins_install` | Install plugin from Git URL / owner/repo (v2.5.0) | Plugins |
| `hermes_plugins_list` | List installed plugins with metadata (v2.5.0) | Plugins |
| `hermes_context_expand` | Preview @ context reference expansion (v2.5.0) | Context |

## Configuration Parameters

| Key | Default | Description |
| --- | --- | --- |
| `hermes_backend` | `auto` | Forced backend (`auto`, `cli`, `ollama`) |
| `hermes_model` | `hermes3` | Fallback Ollama model name |
| `hermes_command` | `hermes` | Path/alias to the official CLI binary |
| `hermes_timeout` | `120` | Subprocess command timeout (seconds) |
| `hermes_session_db` | `~/.codomyrmex/hermes_sessions.db` | Path to persistent SQLite storage |
| `hermes_provider` | `openrouter` | Primary inference provider |
| `fallback_model` | `None` | Fallback model on provider errors |
| `fallback_provider` | `None` | Fallback provider (e.g. `ollama`) |
| `yolo` | `False` | Bypass CLI dangerous command prompts |
| `continue_session` | `None` | Resume session by name via `--continue` |
| `pass_session_id` | `False` | Include session ID in system prompt |
| `max_context_tokens` | `100000` | ContextCompressor token threshold |
| `worktree_base_dir` | `~/.codomyrmex/worktrees` | Git worktree base directory |
| `hermes_skill_profile_disable` | `False` | Skip `.codomyrmex/hermes_skills_profile.yaml` |
| `hermes_default_skill_ids` | `[]` | Registry ids → CLI `-s` names (merged each turn) |
| `hermes_default_hermes_skills` | `[]` | Extra raw Hermes skill names |
| `plugins_dir` | `~/.hermes/plugins/` | Root directory for installed plugins (v2.5.0) |
| `context_ref_hard_limit_pct` | `0.50` | @ context hard limit as fraction of context window (v2.5.0) |
| `context_ref_soft_limit_pct` | `0.25` | @ context soft limit as fraction of context window (v2.5.0) |
| `gateway_agent_cache_enabled` | `True` | Enable per-session AIAgent caching in gateway (v2.5.0) |

Environment:
- **`CODOMYRMEX_SKILLS_REGISTRY`** — optional path to YAML extending the bundled skill registry.
- **`HERMES_HOME`** — override for `~/.hermes` (plugins, config, env).

## Plugin System (v2.5.0)

Plugins are external extensions installed from Git repositories into `~/.hermes/plugins/`:

```bash
hermes plugins install owner/repo          # GitHub shorthand
hermes plugins install https://github.com/owner/repo.git
hermes plugins update <name>              # git pull --ff-only
hermes plugins remove <name>              # delete from plugins dir
hermes plugins list                       # Rich table with version/description
```

**Plugin manifest** (`plugin.yaml`):
```yaml
name: my-plugin
version: 1.0.0
description: Does useful things
manifest_version: 1     # semver for installer compat
```

After install: `after-install.md` rendered via Rich if present. Example files (`*.example`) auto-copied.
Security: plugin names validated against path traversal (`../`, `\`, `/`).

## @ Context References (v2.5.0)

Any message sent through the gateway can include `@` tokens that are expanded into attached context:

| Token | Expands to |
|-------|------------|
| `@file:path` | File contents as fenced code block |
| `@file:path:L-R` | Lines L through R only |
| `@folder:path` | Directory tree listing (rg-accelerated) |
| `@diff` | `git diff` (unstaged changes) |
| `@staged` | `git diff --staged` |
| `@git:N` | `git log -N -p` (last N commits) |
| `@url:https://...` | Web page content (via `web_extract_tool`) |

**Token budget**: Injected tokens are measured before dispatch.
- ≤ 25%: injected silently.
- 25-50%: warning appended to message.
- > 50%: expansion blocked (`blocked=True`); original message sent unchanged.

**Workspace sandbox**: `allowed_root` confines all path references; attempts outside raise `ValueError`.

## Gateway Agent Cache (v2.5.0)

The gateway maintains a per-session `AIAgent` cache to avoid re-building agents on every message:

```python
# Config signature = MD5(model + base_url + provider + toolsets + system_prompt)
signature = GatewayRunner._agent_config_signature(model, runtime, toolsets, sys_prompt)
```

**Cache lifecycle**:
- **Hit**: same config → reuse agent; system prompt frozen (not rebuilt).
- **Miss**: new/changed config → build fresh agent, update cache entry.
- **In-place updates** (no eviction): `reasoning_config`, per-message callbacks.
- **Eviction**: `/reset` session command, fallback provider activation.

Thread-safe via `_agent_cache_lock` (threading.Lock).

## Optional Skills (v2.5.0)

Two new optional skills are available under `~/.hermes/skills/`:

### meme-generation
Generates real `.png` meme images using Pillow. Supports 10 curated templates (drake, this-is-fine, expanding-brain, etc.) + any imgflip template by name/ID. Two modes: classic template and AI-image overlay.

```bash
hermes skills enable meme-generation
```

### bioinformatics
Gateway skill to 400+ bioinformatics reference patterns (bioSkills) and 33+ runnable pipelines (ClawBio). Covers genomics, scRNA-seq, variant calling, metagenomics, structural biology, and more. Fetches domain-specific guides on demand via shallow git clone.

```bash
hermes skills enable bioinformatics
```

## Evolution Submodule

The `evolution/` git submodule ([NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution)) provides evolutionary self-improvement capabilities to Hermes:

- **DSPy + GEPA**: Genetic-Pareto Prompt Evolution reads execution traces to understand failures and proposes targeted prompt/skill improvements.
- **Guardrails**: Evolved variants MUST pass the repository-wide test suite before prompting PR reviews.

## Honcho Integration

Hermes v0.2.0 integrates with [Honcho](https://docs.honcho.dev) for persistent cross-session memory:

- **Modes**: `hybrid` (Honcho + local MEMORY.md), `honcho` (Honcho only), `local` (MEMORY.md only)
- **Dialectic reasoning**: Configurable peer interactions with user context
- **Session mapping**: `hermes honcho map` maps directories to Honcho sessions

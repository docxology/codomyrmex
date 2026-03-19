# Hermes Skills System

**Version**: v0.3.0 | **Last Updated**: March 2026 (73-commit update)

## Overview

Hermes features an autonomous, self-improving skills system. Skills are portable, shareable modules that the agent can create, refine, and invoke during conversations. They are compatible with the [agentskills.io](https://agentskills.io) standard for community sharing.

## How Skills Work

### Discovery and Loading

1. **skills_hub.py** scans `$HERMES_HOME/skills/` on startup
2. Skills are registered in the tool registry
3. During conversation, `prompt_builder.py` may inject relevant skills into the system prompt
4. The agent can also explicitly invoke skills via `skills_tool.py`

### Self-Improvement Loop

```text
User Interaction
      │
      ├── Agent identifies reusable pattern
      │
      ├── Agent auto-extracts skill (YAML/JSON)
      │
      ├── Skill saved to $HERMES_HOME/skills/
      │
      └── On next invocation, skill is refined
          based on outcomes
```

## Skills Directory Structure

```text
$HERMES_HOME/skills/
├── bundled/               # built-in skills (from installation)
│   ├── web_research.yaml
│   └── code_review.yaml
├── learned/               # auto-created by the agent
│   ├── data_analysis.yaml
│   └── email_summary.yaml
└── custom/                # manually added
    └── my_workflow.yaml
```

## Skill Format

```yaml
name: Example Skill
description: A reusable skill for doing X
prompt: |
    You are an expert in X. When asked to perform Y,
    follow these steps:
    1. Step one
    2. Step two
    3. Step three
tools:
    - web_search
    - code_execution
    - file_operations
```

## CLI Commands

```bash
# List installed skills
hermes skills

# Manage skills
hermes skills list
hermes skills sync          # sync from Skills Hub

# Tool-level management (from within a conversation)
# The agent can create/update/delete skills autonomously
```

## Codomyrmex MCP: preloading skills

Third-party packs (for example [PrediHermes / geopolitical-market-sim](https://github.com/nativ3ai/hermes-geopolitical-market-sim)) install under `$HERMES_HOME/skills/`. The Hermes CLI loads them with `hermes chat -s <name>` (or comma-separated names).

Codomyrmex maps the same behavior onto MCP tools:

- `hermes_execute`, `hermes_stream`, `hermes_sampling`, `hermes_batch_execute`: optional `hermes_skill` (one name) and/or `hermes_skills` (list or comma-separated string).
- `hermes_chat_session`: same parameters; normalized names are stored on the session as `hermes_skills` in metadata and reused on later turns until you pass new skill arguments.

**Ollama fallback**: when the client runs `ollama run` instead of `hermes`, these flags are not applied—Hermes-native skills exist only on the CLI path.

**Response metadata**: on successful CLI turns, `AgentResponse.metadata` may include `hermes_skills_loaded` (list of names) echoing what was passed to `-s`, for tracing and orchestration logs.

## Community Skills Hub

Hermes integrates with [agentskills.io](https://agentskills.io) for community sharing:

- **Install community skills** via `hermes skills sync`
- **Share your skills** by publishing to the hub
- **Portable format** works across Hermes instances

## Newly Bundled Skills (March 2026)

The 73-commit update added 2 new bundled skills synced via `hermes update`:

| Skill | Path | Purpose |
| :---- | :--- | :------ |
| **huggingface-hub** | `skills/mlops/huggingface-hub/SKILL.md` | Hugging Face `hf` CLI — search/download/upload models & datasets, manage repos, SQL queries via DuckDB, deploy inference endpoints, manage Spaces |
| **hermes-agent-setup** | `skills/dogfood/hermes-agent-setup/SKILL.md` | Self-documentation skill — Hermes can now help users configure itself, set up voice/TTS/STT, manage tools, and troubleshoot |

Install/verify with:

```bash
hermes skills list  # should show both new skills
```

## Key Implementation Files

| File                          | Purpose                                          |
| :---------------------------- | :----------------------------------------------- |
| `tools/skills_hub.py`         | Skills Hub CLI handler and sync                  |
| `tools/skills_tool.py`        | In-conversation skill invocation                 |
| `tools/skill_manager_tool.py` | CRUD operations on skills                        |
| `tools/skills_guard.py`       | Safety guard: blocks dangerous skill ops         |

## Codomyrmex HermesSkillBridge

The [`HermesSkillBridge`](../../../src/codomyrmex/skills/hermes_skill_bridge.py) syncs
`$HERMES_HOME/skills/` into the Codomyrmex `SkillRegistry`, making every installed
Hermes skill (including third-party packs like PrediHermes) a first-class Python callable:

```python
from codomyrmex.skills.hermes_skill_bridge import HermesSkillBridge

bridge = HermesSkillBridge()

# Discover all installed Hermes skills
skills = bridge.list_hermes_skills()   # dict[name → HermesSkillEntry]

# Run a skill directly
entry = bridge.get_skill("geopolitical-market-sim")
resp = entry.run("Use PrediHermes health")

# Or via the convenience method
resp = bridge.run_skill("geopolitical-market-sim", "Use PrediHermes health")
```

See [PrediHermes Integration Guide](predihermes.md) for full end-to-end examples.

## Related Documents

- [Architecture](architecture.md) — Prompt building and skill injection
- [Tools](tools.md) — Tool registry system
- [PrediHermes](predihermes.md) — Full PrediHermes integration guide

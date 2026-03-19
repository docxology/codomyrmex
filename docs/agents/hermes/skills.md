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

## Codomyrmex MCP preload

From Codomyrmex, Hermes CLI turns can pass **`hermes_skill`** (one name) and/or **`hermes_skills`** (list or comma-separated string) on MCP tools such as `hermes_execute`, `hermes_stream`, `hermes_chat_session`, `hermes_batch_execute`, and `hermes_sampling`. The client maps these to `hermes chat -s <names>` (comma-joined). **Ollama** fallback does not load Hermes skill packs.

For **multi-turn** `hermes_chat_session`, skill names are stored on the session (`metadata.hermes_skills`) and reused on each turn.

PAI **`get_skill_manifest()`** lists every tool with **`tags`** (for example `hermes`, `skills`, `cli_preload`, `interop`, `mcp`). Filter manifest tools by `category == "hermes"` or by tag `skills`. Workflow **`hermes_external_skills`** lists a discover → chat → execute sequence.

## Unified registry and project profile

Codomyrmex ships a **bundled skill registry** (`codomyrmex.agents.hermes.data.skills_registry.yaml`): each entry has a stable **`id`**, human **`title`**, and **`hermes_preload`** names passed to `hermes chat -s`. Optional overlay: set **`CODOMYRMEX_SKILLS_REGISTRY`** to a path of extra YAML in the same shape (merged by id; later files do not remove bundled entries unless you use distinct ids).

**Project defaults**: from the process current working directory, walk upward for **`.codomyrmex/hermes_skills_profile.yaml`**. It may list:

- **`skill_ids`** — resolved through the registry to Hermes preload names
- **`hermes_preload`** — raw CLI names appended after resolution

**Client config** (passed into `HermesClient` or agent config) may set:

- **`hermes_default_skill_ids`** — registry ids
- **`hermes_default_hermes_skills`** — raw Hermes names
- **`hermes_skill_profile_disable`** — skip the project profile file

**Merge order** for each CLI turn (unique, first-wins order): profile → client config → session metadata (`hermes_skills` stored on the session) → explicit `AgentRequest.context` / MCP `hermes_skill(s)` parameters.

MCP tools: **`hermes_skills_resolve`** (ids → names + metadata), **`hermes_skills_validate_registry`** (compare registry to `hermes skills list` when CLI is active). Example profile: [config/hermes_skills_profile.example.yaml](../../../config/hermes_skills_profile.example.yaml).

## Key Implementation Files

| File                          | Purpose                                          |
| :---------------------------- | :----------------------------------------------- |
| `tools/skills_hub.py`         | Skills Hub CLI handler and sync                  |
| `tools/skills_tool.py`        | In-conversation skill invocation                 |
| `tools/skill_manager_tool.py` | CRUD operations on skills                        |
| `tools/skills_guard.py`       | Safety guard: blocks dangerous skill ops         |

## Related Documents

- [Architecture](architecture.md) — Prompt building and skill injection
- [Tools](tools.md) — Tool registry system (distinct from Codomyrmex skill id registry)
- [codomyrmex_integration.md](codomyrmex_integration.md) — MCP tool surface and §3c skill preload overview
- [configuration.md](configuration.md) — Hermes `config.yaml` vs `HermesClient` keys
- [environment.md](environment.md) — `CODOMYRMEX_SKILLS_REGISTRY`, `HERMES_HOME`

# Hermes Skills System

**Version**: v0.2.0 | **Last Updated**: March 2026

## Overview

Hermes features an autonomous, self-improving skills system. Skills are portable, shareable modules that the agent can create, refine, and invoke during conversations. They are compatible with the [agentskills.io](https://agentskills.io) standard for community sharing.

## How Skills Work

### Discovery and Loading

1. **skills_hub.py** scans `$HERMES_HOME/skills/` on startup
2. Skills are registered in the tool registry
3. During conversation, `prompt_builder.py` may inject relevant skills into the system prompt
4. The agent can also explicitly invoke skills via `skills_tool.py`

### Self-Improvement Loop

```
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

```
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

## Key Implementation Files

| File                          | Purpose                          |
| :---------------------------- | :------------------------------- |
| `tools/skills_hub.py`         | Skills Hub CLI handler and sync  |
| `tools/skills_tool.py`        | In-conversation skill invocation |
| `tools/skill_manager_tool.py` | CRUD operations on skills        |

## Related Documents

- [Architecture](architecture.md) — Prompt building and skill injection
- [Tools](tools.md) — Tool registry system

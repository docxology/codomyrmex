# Codomyrmex Agents — docs/agents/ Coordination

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination document for the `docs/agents/` directory. This directory contains documentation for all **38 AI agent integrations** in the Codomyrmex ecosystem, mirroring the structure of `src/codomyrmex/agents/`.

## Agent Documentation Index

### CLI-based Agents (10)

| Agent | Documentation | Source Module |
|:---|:---|:---|
| Jules | [jules/](jules/) | `src/codomyrmex/agents/jules/` |
| Gemini | [gemini/](gemini/) | `src/codomyrmex/agents/gemini/` |
| Hermes | [hermes/](hermes/) — 21 docs, [skills.md](hermes/skills.md) (registry / profile / MCP) | `src/codomyrmex/agents/hermes/` |
| OpenCode | [opencode/](opencode/) | `src/codomyrmex/agents/opencode/` |
| Mistral Vibe | [mistral_vibe/](mistral_vibe/) | `src/codomyrmex/agents/mistral_vibe/` |
| Every Code | [every_code/](every_code/) | `src/codomyrmex/agents/every_code/` |
| OpenClaw | [openclaw/](openclaw/) | `src/codomyrmex/agents/openclaw/` |
| agenticSeek | [agentic_seek/](agentic_seek/) | `src/codomyrmex/agents/agentic_seek/` |
| OpenFang | [openfang/](openfang/) | `src/codomyrmex/agents/openfang/` |
| Pi | [pi/](pi/) | `src/codomyrmex/agents/pi/` |

### API-based Agents (6)

| Agent | Documentation | Source Module |
|:---|:---|:---|
| Claude | [claude/](claude/) | `src/codomyrmex/agents/claude/` |
| Codex | [codex/](codex/) | `src/codomyrmex/agents/codex/` |
| O1/O3 | [o1/](o1/) | `src/codomyrmex/agents/o1/` |
| DeepSeek | [deepseek/](deepseek/) | `src/codomyrmex/agents/deepseek/` |
| Qwen | [qwen/](qwen/) | `src/codomyrmex/agents/qwen/` |
| Perplexity | [perplexity/](perplexity/) | `src/codomyrmex/agents/perplexity/` |

### Core Infrastructure (8)

| Module | Documentation | Source Module |
|:---|:---|:---|
| Core | [core/](core/) | `src/codomyrmex/agents/core/` |
| AI Code Editing | [ai_code_editing/](ai_code_editing/) | `src/codomyrmex/agents/ai_code_editing/` |
| Droid | [droid/](droid/) | `src/codomyrmex/agents/droid/` |
| Learning | [learning/](learning/) | `src/codomyrmex/agents/learning/` |
| Memory | [memory/](memory/) | `src/codomyrmex/agents/memory/` |
| Meta | [meta/](meta/) | `src/codomyrmex/agents/meta/` |
| Planner | [planner/](planner/) | `src/codomyrmex/agents/planner/` |
| PAI | [pai/](pai/) | `src/codomyrmex/agents/pai/` |

### Infrastructure (9)

| Module | Documentation | Source Module |
|:---|:---|:---|
| Agent Setup | [agent_setup/](agent_setup/) | `src/codomyrmex/agents/agent_setup/` |
| CLI | [cli/](cli/) | `src/codomyrmex/agents/cli/` |
| Context | [context/](context/) | `src/codomyrmex/agents/context/` |
| Evaluation | [evaluation/](evaluation/) | `src/codomyrmex/agents/evaluation/` |
| Generic | [generic/](generic/) | `src/codomyrmex/agents/generic/` |
| History | [history/](history/) | `src/codomyrmex/agents/history/` |
| Infrastructure | [infrastructure/](infrastructure/) | `src/codomyrmex/agents/infrastructure/` |
| Pooling | [pooling/](pooling/) | `src/codomyrmex/agents/pooling/` |
| Transport | [transport/](transport/) | `src/codomyrmex/agents/transport/` |

### Specialized (6)

| Module | Documentation | Source Module |
|:---|:---|:---|
| Ghost Architecture | [ghost_architecture/](ghost_architecture/) | `src/codomyrmex/agents/ghost_architecture/` |
| Git Agent | [git_agent/](git_agent/) | `src/codomyrmex/agents/git_agent/` |
| Google Workspace | [google_workspace/](google_workspace/) | `src/codomyrmex/agents/google_workspace/` |
| Mission Control | [mission_control/](mission_control/) | `src/codomyrmex/agents/mission_control/` |
| Specialized | [specialized/](specialized/) | `src/codomyrmex/agents/specialized/` |
| Theory | [theory/](theory/) | `src/codomyrmex/agents/theory/` |

## Operating Contracts

1. **Mirror Rule**: Every subdirectory in `src/codomyrmex/agents/` must have a corresponding documentation subfolder here
2. **Source Linking**: Each doc README must link back to the corresponding source module
3. **Agent Comparison**: Cross-reference the agent comparison matrix at `src/codomyrmex/agents/AGENT_COMPARISON.md`
4. **Rules**: Agent behavioral rules are in `rules/` subdirectory

## Navigation

- **Parent**: [docs/AGENTS.md](../AGENTS.md) — Documentation-level coordination
- **Root**: [AGENTS.md](../../AGENTS.md) — Root agent coordination
- **Source**: [src/codomyrmex/agents/](../../src/codomyrmex/agents/) — Source code
- **Comparison**: [AGENT_COMPARISON.md](../../src/codomyrmex/agents/AGENT_COMPARISON.md) — Agent comparison matrix

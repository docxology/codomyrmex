# Agent Documentation

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation for all AI agent integrations in the Codomyrmex ecosystem. This directory mirrors [`src/codomyrmex/agents/`](../../src/codomyrmex/agents/) with a documentation subfolder for each agent framework.

## Agent Index

### CLI-based Agents

| Agent | Documentation | Description |
|:---|:---|:---|
| **Jules** | [jules/](jules/) | Google Jules CLI, swarm orchestration |
| **Gemini** | [gemini/](gemini/) | Google Gemini CLI, OAuth/API key, @ file ops |
| **Hermes** | [hermes/](hermes/) | Nous Research, gateway, Telegram/WhatsApp; 19 docs incl. [skills.md](hermes/skills.md) (Codomyrmex skill registry / MCP preload) |
| **OpenCode** | [opencode/](opencode/) | Open-source coding agent |
| **Mistral Vibe** | [mistral_vibe/](mistral_vibe/) | Mistral AI vibe CLI |
| **Every Code** | [every_code/](every_code/) | Multi-agent orchestration, /plan /solve /code |
| **OpenClaw** | [openclaw/](openclaw/) | Open-source agentic CLI |
| **agenticSeek** | [agentic_seek/](agentic_seek/) | Autonomous browser-capable agent |
| **OpenFang** | [openfang/](openfang/) | Security-conscious agent framework |
| **Pi** | [pi/](pi/) | Pi coding agent via RPC |

### API-based Agents

| Agent | Documentation | Description |
|:---|:---|:---|
| **Claude** | [claude/](claude/) | Anthropic Claude 3, advanced reasoning |
| **Codex** | [codex/](codex/) | OpenAI Codex, code-focused models |
| **O1/O3** | [o1/](o1/) | OpenAI reasoning models, chain-of-thought |
| **DeepSeek** | [deepseek/](deepseek/) | Cost-effective code generation |
| **Qwen** | [qwen/](qwen/) | Alibaba DashScope, multilingual |
| **Perplexity** | [perplexity/](perplexity/) | Research-augmented generation |

### Core Infrastructure

| Module | Documentation | Description |
|:---|:---|:---|
| **Core** | [core/](core/) | Base classes, interfaces, LLM client factory |
| **AI Code Editing** | [ai_code_editing/](ai_code_editing/) | Diff-based editing, code transforms |
| **Droid** | [droid/](droid/) | Task management, priority queues |
| **Learning** | [learning/](learning/) | Self-improvement, feedback loops |
| **Memory** | [memory/](memory/) | Short/long-term memory, vector recall |
| **Meta** | [meta/](meta/) | Self-reflection, strategy selection |
| **Planner** | [planner/](planner/) | Goal decomposition, convergent planning |
| **PAI** | [pai/](pai/) | Personal AI Infrastructure bridge |

### Infrastructure

| Module | Documentation | Description |
|:---|:---|:---|
| **Agent Setup** | [agent_setup/](agent_setup/) | Environment validation, agent discovery |
| **CLI** | [cli/](cli/) | Common CLI handler framework |
| **Context** | [context/](context/) | Repository indexing, project scanning |
| **Evaluation** | [evaluation/](evaluation/) | Quality evaluation, benchmarks |
| **Generic** | [generic/](generic/) | Template for new agent integrations |
| **History** | [history/](history/) | Interaction history, audit logging |
| **Infrastructure** | [infrastructure/](infrastructure/) | Health checks, resource management |
| **Pooling** | [pooling/](pooling/) | Load balancing, circuit breakers |
| **Transport** | [transport/](transport/) | State serialization, checkpoints |

### Specialized

| Module | Documentation | Description |
|:---|:---|:---|
| **Ghost Architecture** | [ghost_architecture/](ghost_architecture/) | Continual-learning modular transformer; crystallized ghost modules (git submodule) |
| **Git Agent** | [git_agent/](git_agent/) | Git-aware operations, conflict resolution |
| **Google Workspace** | [google_workspace/](google_workspace/) | Docs, Sheets, Drive, Calendar |
| **Mission Control** | [mission_control/](mission_control/) | Multi-agent mission orchestration |
| **Specialized** | [specialized/](specialized/) | Autonomous code improvement pipeline |
| **Theory** | [theory/](theory/) | Agent architecture & reasoning theory |

## Other Files

- `AGENTS.md` — Agent coordination
- `PAI.md` — PAI bridge documentation
- `SPEC.md` — Functional specification
- `rules/` — Agent rules and guidelines
- `hermes/AGENTS.md` — Hermes doc index + **Mermaid diagram conventions** for this folder’s inline diagrams

## Navigation

- **Parent Directory**: [docs/](../README.md)
- **Source**: [src/codomyrmex/agents/](../../src/codomyrmex/agents/)
- **Agent Comparison**: [AGENT_COMPARISON.md](../../src/codomyrmex/agents/AGENT_COMPARISON.md)
- **Project Root**: [README.md](../../README.md)

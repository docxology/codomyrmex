# Agent Scripts

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Agent utility scripts for testing, orchestrating, and demonstrating the Codomyrmex agent ecosystem. All scripts are flat in this directory - no nested subfolders.

## Quick Start

```bash
# Run all agent examples
uv run python scripts/agents/run_all_agents.py

# Check agent system status
uv run python scripts/agents/agent_status.py --verbose

# Run Claude Code demo
uv run python scripts/agents/claude_code_demo.py
```

## Real Integration

All relay scripts support real LLM backends via `agent_utils.get_llm_client()`:

1. **Claude API**: Set `ANTHROPIC_API_KEY` environment variable.
2. **Ollama**: Ensure Ollama is running at `http://localhost:11434`.
3. **Requirement**: One of the above MUST be available. Mocks are disabled.

## Scripts

| Script | Description |
| ------ | ----------- |
| `agent_status.py` | System status, health checks, API key validation |
| `run_all_agents.py` | Execute all example scripts with pass/fail summary |
| `orchestrate.py` | Module-scoped script orchestration |
| `test_gemini_dispatch.py` | Gemini client, CodeEditor, and Orchestrator tests |
| `claude_code_demo.py` | Claude Code methods demonstration |
| `relay_chat_demo.py` | **Live Relay** Basic bidirectional chat |
| `recursive_task.py` | **Live Relay** Recursive delegation/clarification |
| `discursive_debate.py` | **Live Relay** Multi-turn dialectic debate |
| `orchestrate_with_ollama.py` | **Full Setup** Auto-starts Ollama, pulls model, runs Relay Chat |

## Agent Examples

| Script | Agent | Features |
| ------ | ----- | -------- |
| `basic_usage.py` | Generic | Agent initialization, requests |
| `claude_example.py` | Claude | Basic API usage |
| `claude_code_workflow.py` | Claude | Full Claude Code workflow |
| `gemini_example.py` | Gemini | Google AI integration |
| `codex_example.py` | Codex | OpenAI Codex integration |
| `droid_example.py` | Droid | Task coordination |
| `jules_example.py` | Jules | Git operations |
| `opencode_example.py` | OpenCode | Open-source models |
| `code_editor_example.py` | CodeEditor | Code generation/refactoring |
| `multi_agent_workflow.py` | Multiple | Orchestrated workflows |
| `advanced_workflow.py` | Multiple | Complex pipelines |
| `agent_diagnostics.py` | All | Capability diagnostics |
| `agent_comparison.py` | Multiple | Side-by-side comparison |
| `theory_example.py` | Theory | Code analysis |

## PAI (Personal AI Infrastructure)

| Script | Description |
| ------ | ----------- |
| `pai_example.py` | Full PAI bridge demo — all 11 subsystems (Algorithm, Skills, Tools, Hooks, Agents, Memory, Security, TELOS, Settings, MCP) |
| `pai_dashboard.py` | **Key entry point** — launches dashboard and opens browser to PAI Awareness page |

```bash
# Full PAI report
uv run python scripts/agents/pai_example.py

# Single subsystem
uv run python scripts/agents/pai_example.py --subsystem algorithm

# JSON output
uv run python scripts/agents/pai_example.py --json

# Launch PAI Control Center in browser
uv run python scripts/agents/pai_dashboard.py

# Launch on custom port without auto-open
uv run python scripts/agents/pai_dashboard.py --port 9000 --no-open
```

## Navigation

- **Parent**: [scripts](../README.md)
- **Agents Module**: [../../src/codomyrmex/agents/README.md](../../src/codomyrmex/agents/README.md)
- **PAI Module**: [../../src/codomyrmex/agents/pai/README.md](../../src/codomyrmex/agents/pai/README.md)
- **Claude Module**: [../../src/codomyrmex/agents/claude/README.md](../../src/codomyrmex/agents/claude/README.md)

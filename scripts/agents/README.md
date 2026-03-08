# Agent Scripts

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Thin orchestrator scripts for testing, demonstrating, and running the Codomyrmex agent ecosystem. Provider-specific scripts are organized into subfolders; shared utilities remain at root.

## Quick Start

```bash
# Run all agent examples
uv run python scripts/agents/run_all_agents.py

# Check agent system status
uv run python scripts/agents/agent_status.py --verbose

# Run Qwen demo (offline)
uv run scripts/agents/qwen/qwen_demo.py --offline
```

## Directory Structure

| Subfolder | Scripts | Description |
|-----------|---------|-------------|
| [claude/](claude/) | 3 | Claude Code demos and workflows |
| [codex/](codex/) | 1 | OpenAI Codex integration |
| [code_editing/](code_editing/) | 1 | Code editor/refactoring demos |
| [deepseek/](deepseek/) | 1 | DeepSeek model demos |
| [droid/](droid/) | 1 | Droid controller examples |
| [evaluation/](evaluation/) | 1 | Agent evaluation benchmarks |
| [gemini/](gemini/) | 2 | Google Gemini demos + dispatch |
| [history/](history/) | 1 | Agent history exploration |
| [jules/](jules/) | 4 | Jules, mega-swarm dispatcher/harvester |
| [o1/](o1/) | 1 | OpenAI o1 reasoning demos |
| [ollama/](ollama/) | 1 | Ollama orchestration |
| [opencode/](opencode/) | 1 | Open-source model CLI |
| [pai/](pai/) | 8+ | PAI bridge, dashboard, personality, security |
| [pooling/](pooling/) | 1 | Agent pooling demos |
| [qwen/](qwen/) | 1 | **Qwen demos** (14 models, 5 MCP tools) |

## Shared Root Scripts

| Script | Description |
|--------|-------------|
| `agent_status.py` | System status, health checks, API validation |
| `agent_diagnostics.py` | Capability diagnostics across all agents |
| `agent_comparison.py` | Side-by-side provider comparison |
| `agent_utils.py` | Shared utilities (`get_llm_client()`) |
| `run_all_agents.py` | Execute all examples with pass/fail summary |
| `orchestrate.py` | Module-scoped script orchestration |
| `basic_usage.py` | Generic agent initialization |
| `multi_agent_workflow.py` | Multi-agent orchestrated workflows |
| `advanced_workflow.py` | Complex multi-step pipelines |
| `relay_chat_demo.py` | Live bidirectional relay chat |
| `recursive_task.py` | Recursive delegation/clarification |
| `discursive_debate.py` | Multi-turn dialectic debate |
| `theory_example.py` | Code analysis via theory module |
| `verify_skill_structure.py` | Skill system structure validation |

## Real Integration

All relay scripts support real LLM backends via `agent_utils.get_llm_client()`:

1. **Claude API**: Set `ANTHROPIC_API_KEY`
2. **Ollama**: Ensure running at `http://localhost:11434`
3. **Qwen**: Set `DASHSCOPE_API_KEY`
4. **Zero-Mock**: One backend MUST be available. No mocks.

## Navigation

- **Parent**: [scripts/](../README.md)
- **Source Module**: [../../src/codomyrmex/agents/](../../src/codomyrmex/agents/README.md)
- **PAI Module**: [../../src/codomyrmex/agents/pai/](../../src/codomyrmex/agents/pai/README.md)

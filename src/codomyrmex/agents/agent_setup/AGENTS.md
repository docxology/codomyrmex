# Agent Setup — AGENTS.md

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

This module is consumed by autonomous agents to configure and verify agent availability.

## Key Entry Points

| Function / Class | Purpose |
|-----------------|---------|
| `AgentRegistry.probe_all()` | Probe all 12 agents, returns `list[ProbeResult]` |
| `AgentRegistry.get_operative()` | Returns names of currently working agents |
| `load_config()` / `save_config()` | YAML config persistence |
| `run_setup_wizard(non_interactive=True)` | Programmatic status scan |

## Environment Variables

| Variable | Agent | Type |
|----------|-------|------|
| `ANTHROPIC_API_KEY` | Claude | API |
| `OPENAI_API_KEY` | Codex, O1 | API |
| `DEEPSEEK_API_KEY` | DeepSeek | API |
| `DASHSCOPE_API_KEY` | Qwen | API |
| `OLLAMA_BASE_URL` | Ollama | Local |

## Testing

```bash
uv run python -m pytest tests/unit/agents/test_agent_setup.py -v --no-cov
```

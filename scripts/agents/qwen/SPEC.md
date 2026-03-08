# Qwen Scripts — SPEC

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

**Directory**: `scripts/agents/qwen/`

## Purpose

Thin orchestrator scripts for Qwen agent demos. All business logic resides in `src/codomyrmex/agents/qwen/`.

## Scripts

| Script | Exit Codes | Dependencies |
|--------|-----------|--------------|
| `qwen_demo.py` | 0=success, 1=error | `openai`, optional `qwen-agent` |

## Configuration

| Env Variable | Required | Description |
|-------------|----------|-------------|
| `DASHSCOPE_API_KEY` | For API demos | DashScope API key |
| `QWEN_API_KEY` | Alternative | Alternative API key |

## Navigation

- [README.md](README.md) · [AGENTS.md](AGENTS.md) · [PAI.md](PAI.md)

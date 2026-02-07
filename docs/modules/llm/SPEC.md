# LLM — Functional Specification

**Module**: `codomyrmex.llm`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

LLM integration modules for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Submodule Structure

- `chains/` — Chain implementations for LLM reasoning.
- `cost_tracking/` — LLM Cost Tracking Module
- `embeddings/` — LLM Embeddings Module
- `fabric/` — Codomyrmex Fabric Integration Module
- `guardrails/` — LLM Guardrails Module
- `memory/` — Conversation memory management for LLMs.
- `ollama/` — Codomyrmex Ollama Integration Module
- `prompts/` — LLM Prompts Module
- `providers/` — LLM Provider abstractions for unified API access.
- `rag/` — LLM RAG Module
- `streaming/` — LLM Streaming Module
- `tools/` — Tool calling framework for LLMs.

### Source Files

- `config.py`
- `exceptions.py`
- `mcp.py`
- `router.py`

## 3. Dependencies

See `src/codomyrmex/llm/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k llm -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/llm/)

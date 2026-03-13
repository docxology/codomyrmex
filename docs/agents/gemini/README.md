# Gemini (Google)

**Module**: `codomyrmex.agents.gemini` | **Category**: CLI-based | **Last Updated**: March 2026

## Overview

Google Gemini integration with both CLI wrapper (`gemini` command) and API client. Supports file operations, media handling, tuning/batch workflows, and caching for cost optimization.

## Key Classes

| Class | Purpose |
|:---|:---|
| `GeminiClient` | API client for Gemini models (chat, generate, embed) |
| `GeminiCLIWrapper` | CLI wrapper for `gemini` command-line tool |
| `GeminiIntegrationAdapter` | Bridges Gemini with other Codomyrmex modules |

## Extended Modules

| Module | Purpose |
|:---|:---|
| `_files.py` | File upload/download for context |
| `_media.py` | Media handling (images, audio, video) |
| `_cache.py` | Response caching for cost optimization |
| `_tuning_batch.py` | Fine-tuning and batch processing |

## Usage

```python
from codomyrmex.agents.gemini import GeminiClient, GeminiCLIWrapper

# API client
client = GeminiClient()
response = client.execute(AgentRequest(prompt="Explain this code"))

# CLI wrapper
cli = GeminiCLIWrapper()
result = cli.run("Analyze this project", working_dir="/path/to/project")
```

## Configuration

**Required API Key**: `GEMINI_API_KEY` or `GOOGLE_API_KEY`

```bash
export GEMINI_API_KEY=your-key-here
```

## Source Module

Source: [`src/codomyrmex/agents/gemini/`](../../../../src/codomyrmex/agents/gemini/)

| File | Purpose |
|:---|:---|
| `gemini_client.py` | API client for chat, generation, embedding |
| `gemini_cli.py` | CLI wrapper for the `gemini` command |
| `gemini_integration.py` | Integration adapter |
| `mcp_tools.py` | MCP tool definitions |
| `_files.py` | File upload/download operations |
| `_media.py` | Image/audio/video handling |
| `_cache.py` | Response caching |
| `_tuning_batch.py` | Fine-tuning and batch workflows |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/gemini/](../../../../src/codomyrmex/agents/gemini/)
- **Project Root**: [README.md](../../../README.md)

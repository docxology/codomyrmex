# Perplexity Agent

**Path**: `src/codomyrmex/agents/perplexity`

## Submodule Overview

- `__init__.py`: Exports `PerplexityClient`, `PerplexityError`.
- `perplexity_client.py`: Core client `PerplexityClient` interacting with the Perplexity Chat Completions API.
- `mcp_tools.py`: Exposes `perplexity_execute` to Claude contexts.

## Architecture

Follows `APIAgentBase`. Uses standard `requests` block to query Perplexity with optional streaming iterator.

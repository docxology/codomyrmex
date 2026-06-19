# Codex (OpenAI)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: June 2026

**Module**: `codomyrmex.agents.codex` | **Category**: API-based

## Key Classes

| Class | Purpose |
|:---|:---|
| `CodexClient` | OpenAI Codex-compatible API client implementing the Codomyrmex agent interface |
| `CodexIntegrationAdapter` | Bridges Codex with other Codomyrmex modules |

## Read-Only Access

Codex can inspect Codomyrmex capabilities without launching agents:

```bash
uv run python scripts/agents/codex_access.py --json
uv run python scripts/agents/improve_src.py --dry-run --limit 2 --json
```

See [Codex Access to Codomyrmex](access.md) for the MCP tools and dispatch
classifications.

## Usage

```python
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.codex import CodexClient

client = CodexClient()
response = client.execute(AgentRequest(prompt="Add error handling to parser.py"))
```

## Configuration

`CodexClient` uses the configured OpenAI-compatible API settings from the
Codomyrmex agent configuration, including `OPENAI_API_KEY` and `CODEX_MODEL`
when present. The read-only access probes do not require API credentials.

## Source Module

Source: [`src/codomyrmex/agents/codex/`](../../../src/codomyrmex/agents/codex/)

| File | Purpose |
|:---|:---|
| `access.py` | Read-only Codex access status and dispatch catalog |
| `codex_client.py` | API client, task submission, response parsing |
| `codex_integration.py` | Integration adapter |
| `mcp_tools.py` | MCP tool definitions |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/codex/](../../../src/codomyrmex/agents/codex/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Access Guide**: [access.md](access.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.

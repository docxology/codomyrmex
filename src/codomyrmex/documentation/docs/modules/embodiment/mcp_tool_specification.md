# Embodiment MCP Tool Specification

**Version**: v1.3.0 | **Status**: Active, no MCP tools | **Last Updated**: July 2026

The embodiment module currently exposes Python APIs only. It has no
`@mcp_tool` functions because its tested surface is local telemetry,
WebSocket, simulated hardware, topic history, and transform math.

Future MCP tools should be added only when there is a discrete, safe, local
operation that an external agent can invoke without opening persistent hardware
control channels.

## Validation

```bash
uv run pytest tests/unit/embodiment/ -q
```

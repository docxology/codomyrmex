# agents/openfang — PAI Integration

## Module Role

openfang is a **EXECUTE-phase amplifier**: it turns natural-language agent queries into
autonomous actions via a production-grade Agent OS. It also covers OBSERVE (health checks),
PLAN (Hands scheduling), and LEARN (upstream sync).

## MCP Tools

| Tool | Category | Description |
|------|----------|-------------|
| `openfang_check` | openfang | Installation status, version, submodule state |
| `openfang_execute` | openfang | Run agent query, return response |
| `openfang_hands_list` | openfang | List autonomous Hands with metadata |
| `openfang_send_message` | openfang | Send via channel adapter (telegram, slack, etc.) |
| `openfang_gateway` | openfang | Start/stop/status WebSocket gateway |
| `openfang_config` | openfang | Show current configuration from env vars |
| `openfang_update` | openfang | Pull upstream + optionally rebuild/install |

## PAI Phase Mapping

| Phase | Tools | Notes |
|-------|-------|-------|
| OBSERVE | `openfang_check`, `openfang_config` | Verify installation, confirm config |
| THINK | `openfang_execute` | Single-turn reasoning against openfang's agent engine |
| PLAN | `openfang_hands_list` | Enumerate available autonomous Hands |
| BUILD | `openfang_execute`, `openfang_update` | Generate/modify code; pull latest capabilities |
| EXECUTE | `openfang_execute`, `openfang_send_message`, `openfang_gateway` | Run tasks, deliver results |
| VERIFY | `openfang_check`, `openfang_gateway(action="status")` | Confirm binary health, gateway alive |
| LEARN | `openfang_update` | Pull latest upstream learnings and capabilities |

## Usage Examples

```python
# OBSERVE — check readiness
from codomyrmex.agents.openfang.mcp_tools import openfang_check
status = openfang_check()
assert status["installed"], "openfang not installed"

# EXECUTE — run an agent task
from codomyrmex.agents.openfang.mcp_tools import openfang_execute
result = openfang_execute(prompt="Summarize the last 10 git commits")
print(result["stdout"])

# EXECUTE — send notification via channel
from codomyrmex.agents.openfang.mcp_tools import openfang_send_message
openfang_send_message(channel="slack", target="#dev-alerts", message="Deploy complete")

# LEARN — pull latest upstream
from codomyrmex.agents.openfang.mcp_tools import openfang_update
openfang_update(rebuild=True, install=True)
```

## Auto-Discovery

The 7 tools above are automatically surfaced via the PAI MCP bridge through
`@mcp_tool` decorator scanning of `mcp_tools.py`. No manual registration required.

## Trust Level

`openfang_execute` and `openfang_gateway(action="start")` trigger subprocess execution.
These are gated by the PAI Trust Gateway in VERIFIED state.
`openfang_update(rebuild=True, install=True)` modifies filesystem — requires TRUSTED state.

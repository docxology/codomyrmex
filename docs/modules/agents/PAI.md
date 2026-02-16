# PAI Documentation Hub

Central navigation for **Personal AI Infrastructure (PAI)** integration with the Codomyrmex ecosystem.

**Upstream**: [github.com/danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)

## Documentation Suite

### Core

| Document | Purpose |
|:---|:---|
| [**README.md**](PAI/README.md) | Bidirectional architecture, PAI Principles mapping, quick start |
| [**ARCHITECTURE.md**](PAI/ARCHITECTURE.md) | Three-layer deep dive (PAIBridge → MCPBridge → TrustGateway) |
| [**FLOWS.md**](PAI/FLOWS.md) | 6 Mermaid diagrams for operational sequences |
| [**SIGNPOSTS.md**](PAI/SIGNPOSTS.md) | Line-level code pointers to 60+ symbols |
| [**AGENTS.md**](PAI/AGENTS.md) | Agent coordination guide |

### PAI Element Deep Dives

| Document | PAI Element |
|:---|:---|
| [**ALGORITHM.md**](PAI/ALGORITHM.md) | The Algorithm v0.2.25 — 7 phases, ISC, depth levels |
| [**SKILLS.md**](PAI/SKILLS.md) | Skill System — architecture, priority, assembly |
| [**TELOS.md**](PAI/TELOS.md) | Deep Goal Understanding — 10 identity files, memory |
| [**HOOKS.md**](PAI/HOOKS.md) | Hook System — 8 events, FormatReminder, security |
| [**WORKFLOWS.md**](PAI/WORKFLOWS.md) | Workflows & Dispatch — v3.2.1, PMServer |

## Quick Links

| Resource | Path |
|:---|:---|
| PAI Bridge source | [`src/codomyrmex/agents/pai/pai_bridge.py`](../../../src/codomyrmex/agents/pai/pai_bridge.py) |
| MCP Bridge source | [`src/codomyrmex/agents/pai/mcp_bridge.py`](../../../src/codomyrmex/agents/pai/mcp_bridge.py) |
| Trust Gateway source | [`src/codomyrmex/agents/pai/trust_gateway.py`](../../../src/codomyrmex/agents/pai/trust_gateway.py) |
| Claude Client source | [`src/codomyrmex/agents/claude/claude_client.py`](../../../src/codomyrmex/agents/claude/claude_client.py) |
| Root PAI doc | [`PAI.md`](../../../PAI.md) |

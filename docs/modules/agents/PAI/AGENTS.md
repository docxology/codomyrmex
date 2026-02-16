# AGENTS.md — PAI Documentation Folder

## Agent Coordination Guide

This folder contains the documentation for the bidirectional integration between **Codomyrmex** and [**Daniel Miessler's Personal AI Infrastructure (PAI)**](https://github.com/danielmiessler/Personal_AI_Infrastructure).

### For AI Agents Working in This Folder

When operating on PAI-related tasks, agents should:

1. **Read [README.md](README.md) first** — Understand the bidirectional architecture and the 16 PAI Principles.
2. **Consult [ARCHITECTURE.md](ARCHITECTURE.md)** — For the three-layer breakdown (PAIBridge → MCPBridge → TrustGateway).
3. **Reference [FLOWS.md](FLOWS.md)** — For operational sequence diagrams before implementing new flows.
4. **Use [SIGNPOSTS.md](SIGNPOSTS.md)** — For precise line-level code pointers before editing integration code.

### Key Source Files

| File | Path | Layer |
|:---|:---|:---|
| `pai_bridge.py` | `src/codomyrmex/agents/pai/pai_bridge.py` | Discovery |
| `mcp_bridge.py` | `src/codomyrmex/agents/pai/mcp_bridge.py` | Communication |
| `trust_gateway.py` | `src/codomyrmex/agents/pai/trust_gateway.py` | Security |
| `claude_client.py` | `src/codomyrmex/agents/claude/claude_client.py` | Execution |
| `claude_integration.py` | `src/codomyrmex/agents/claude/claude_integration.py` | Adaptation |

### Critical Constraints

- **Zero-Mock Policy**: All PAI/Codomyrmex tests use real filesystem operations. Never introduce mocks.
- **Trust Hierarchy**: Destructive tools must always go through [`trusted_call_tool()`](../../../src/codomyrmex/agents/pai/trust_gateway.py).
- **Upstream Alignment**: Any changes must maintain compatibility with [PAI upstream](https://github.com/danielmiessler/Personal_AI_Infrastructure).
- **Algorithm Compliance**: New tools should be mapped to Algorithm phases in [`get_skill_manifest()`](../../../src/codomyrmex/agents/pai/mcp_bridge.py).

### Workflow Commands

| Command | Purpose |
|:---|:---|
| `/codomyrmexVerify` | Audit all capabilities, promote safe tools to VERIFIED |
| `/codomyrmexTrust` | Promote destructive tools to TRUSTED |
| `/codomyrmexStatus` | Full PAI + Codomyrmex health report |
| `/codomyrmexAnalyze` | Deep structural analysis |
| `/codomyrmexSearch` | Regex search across codebase |
| `/codomyrmexDocs` | Retrieve module documentation |
| `/codomyrmexMemory` | Add entry to agentic memory |

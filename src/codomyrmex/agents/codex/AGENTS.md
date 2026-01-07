# Codomyrmex Agents — src/codomyrmex/agents/codex

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Integration with OpenAI Codex API. Provides client for interacting with Codex API, supports code generation and completion, and provides integration adapters for Codomyrmex modules.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `codex_client.py` – Codex API client implementation
- `codex_integration.py` – Integration adapters for Codomyrmex modules

## Key Classes and Functions

### CodexClient (`codex_client.py`)
- `CodexClient(config: Optional[dict[str, Any]] = None)` – Client for interacting with OpenAI Codex API (extends BaseAgent)
- `execute(request: AgentRequest) -> AgentResponse` – Execute an agent request
- `get_capabilities() -> list[AgentCapabilities]` – Get supported capabilities

### CodexIntegrationAdapter (`codex_integration.py`)
- `CodexIntegrationAdapter()` – Integration adapter for Codomyrmex modules (extends AgentIntegrationAdapter)

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation
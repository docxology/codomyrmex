# Codomyrmex Agents — src/codomyrmex/agents/gemini

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Integration with Google Gemini API. Provides client for interacting with Gemini API, supports code generation and completion, and provides integration adapters for Codomyrmex modules.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `gemini_client.py` – Gemini API client implementation
- `gemini_integration.py` – Integration adapters for Codomyrmex modules
- `tests/` – Directory containing tests components

## Key Classes and Functions

### GeminiClient (`gemini_client.py`)
- `GeminiClient(config: Optional[dict[str, Any]] = None)` – Client for interacting with Google Gemini API (extends BaseAgent)
- `execute(request: AgentRequest) -> AgentResponse` – Execute an agent request
- `get_capabilities() -> list[AgentCapabilities]` – Get supported capabilities

### GeminiIntegrationAdapter (`gemini_integration.py`)
- `GeminiIntegrationAdapter()` – Integration adapter for Codomyrmex modules (extends AgentIntegrationAdapter)

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation
# Codomyrmex Agents — src/codomyrmex/agents/opencode

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
Integration with OpenCode CLI tool. Provides client wrapper for executing opencode commands, handles command failures and timeouts gracefully, and provides integration adapters for Codomyrmex modules.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `opencode_client.py` – OpenCode CLI client wrapper implementation
- `opencode_integration.py` – Integration adapters for Codomyrmex modules

## Key Classes and Functions

### OpenCodeClient (`opencode_client.py`)
- `OpenCodeClient(config: Optional[dict[str, Any]] = None)` – Client for interacting with OpenCode CLI tool (extends BaseAgent)
- `execute(request: AgentRequest) -> AgentResponse` – Execute an agent request via OpenCode CLI
- `get_capabilities() -> list[AgentCapabilities]` – Get supported capabilities

### OpenCodeIntegrationAdapter (`opencode_integration.py`)
- `OpenCodeIntegrationAdapter(agent: AgentInterface)` – Integration adapter for Codomyrmex modules (extends AgentIntegrationAdapter)
- `adapt_for_ai_code_editing(prompt: str, language: str = "python", **kwargs) -> str` – Adapt for AI code editing module
- `adapt_for_llm(messages: list[dict], model: str = None, **kwargs) -> dict` – Adapt for LLM module
- `adapt_for_code_execution(code: str, language: str = "python", **kwargs) -> dict[str, Any]` – Adapt for code execution sandbox

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation
# Codomyrmex Agents — src/codomyrmex/agents/mistral_vibe

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
Integration with Mistral Vibe CLI tool. Provides client for interacting with Mistral Vibe CLI, supports code generation and completion, and provides integration adapters for Codomyrmex modules.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `mistral_vibe_client.py` – Mistral Vibe CLI client implementation
- `mistral_vibe_integration.py` – Integration adapters for Codomyrmex modules
- `tests/` – Directory containing tests components

## Key Classes and Functions

### MistralVibeClient (`mistral_vibe_client.py`)
- `MistralVibeClient(config: Optional[dict[str, Any]] = None)` – Client for interacting with Mistral Vibe CLI (extends BaseAgent)
- `execute(request: AgentRequest) -> AgentResponse` – Execute an agent request
- `stream(request: AgentRequest) -> Iterator[str]` – Stream response from agent
- `get_capabilities() -> list[AgentCapabilities]` – Get supported capabilities
- `execute_vibe_command(command: str, args: Optional[list[str]] = None, input_text: Optional[str] = None) -> dict[str, Any]` – Execute a vibe command
- `get_vibe_help() -> dict[str, Any]` – Get vibe help information

### MistralVibeIntegrationAdapter (`mistral_vibe_integration.py`)
- `MistralVibeIntegrationAdapter()` – Integration adapter for Codomyrmex modules (extends AgentIntegrationAdapter)
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


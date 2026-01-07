# Codomyrmex Agents — src/codomyrmex/agents/jules

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
Integration with Jules CLI tool. Provides client wrapper for executing jules commands, handles command failures and timeouts gracefully, and provides integration adapters for Codomyrmex modules. Supports code generation, code editing, code analysis, text completion, and streaming capabilities.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `jules_client.py` – Jules CLI client wrapper implementation
- `jules_integration.py` – Integration adapters for Codomyrmex modules

## Key Classes and Functions

### JulesClient (`jules_client.py`)
- `JulesClient(config: Optional[dict[str, Any]] = None)` – Client for interacting with Jules CLI tool (extends BaseAgent)
- `execute(request: AgentRequest) -> AgentResponse` – Execute an agent request via Jules CLI
- `stream(request: AgentRequest) -> Iterator[str]` – Stream response from Jules
- `get_capabilities() -> list[AgentCapabilities]` – Get supported capabilities (CODE_GENERATION, CODE_EDITING, CODE_ANALYSIS, TEXT_COMPLETION, STREAMING)
- `_check_jules_available() -> bool` – Check if jules command is available

### JulesIntegrationAdapter (`jules_integration.py`)
- `JulesIntegrationAdapter(agent: AgentInterface)` – Integration adapter for Codomyrmex modules (extends AgentIntegrationAdapter)
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
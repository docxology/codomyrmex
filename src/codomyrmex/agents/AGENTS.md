# Codomyrmex Agents — src/codomyrmex/agents

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [ai_code_editing](ai_code_editing/AGENTS.md)
    - [claude](claude/AGENTS.md)
    - [codex](codex/AGENTS.md)
    - [droid](droid/AGENTS.md)
    - [gemini](gemini/AGENTS.md)
    - [generic](generic/AGENTS.md)
    - [jules](jules/AGENTS.md)
    - [opencode](opencode/AGENTS.md)
    - [tests](tests/AGENTS.md)
    - [theory](theory/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Integration with various agentic frameworks including Jules CLI, Claude API, OpenAI Codex, OpenCode CLI, and Gemini CLI. Includes theoretical foundations, generic utilities, and framework-specific implementations that integrate seamlessly with Codomyrmex modules. Provides unified interface for all agents through `AgentInterface` abstract base class.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `ai_code_editing/` – Directory containing AI code editing components
- `claude/` – Directory containing Claude API integration
- `codex/` – Directory containing OpenAI Codex integration
- `config.py` – Configuration management
- `core.py` – Core interfaces and base classes
- `droid/` – Directory containing Droid task management components
- `exceptions.py` – Custom exceptions
- `gemini/` – Directory containing Gemini CLI integration
- `generic/` – Directory containing generic base agent classes and utilities
- `jules/` – Directory containing Jules CLI integration
- `opencode/` – Directory containing OpenCode CLI integration
- `tests/` – Directory containing tests components
- `theory/` – Directory containing theoretical foundations for agentic systems

## Key Classes and Functions

### AgentInterface (`core.py`)
- `AgentInterface` (ABC) – Abstract base class for all agent implementations:
  - `get_capabilities() -> list[AgentCapabilities]` – Get list of capabilities supported by this agent
  - `execute(request: AgentRequest) -> AgentResponse` – Execute an agent request
  - `stream(request: AgentRequest) -> Iterator[str]` – Stream response from agent
  - `supports_capability(capability: AgentCapabilities) -> bool` – Check if agent supports a specific capability
  - `validate_request(request: AgentRequest) -> list[str]` – Validate an agent request

### AgentRequest (`core.py`)
- `AgentRequest` (dataclass) – Agent request data structure:
  - `prompt: str` – Request prompt
  - `context: Optional[dict[str, Any]]` – Additional context
  - `capabilities: list[AgentCapabilities]` – Required capabilities
  - `metadata: Optional[dict[str, Any]]` – Additional metadata

### AgentResponse (`core.py`)
- `AgentResponse` (dataclass) – Agent response data structure:
  - `content: str` – Response content
  - `error: Optional[str]` – Error message if request failed
  - `metadata: dict[str, Any]` – Response metadata
  - `is_success() -> bool` – Check if the response is successful

### AgentCapabilities (`core.py`)
- `AgentCapabilities` (Enum) – Enum of agent capabilities (CODE_GENERATION, CODE_REVIEW, DOCUMENTATION, ANALYSIS, etc.)

### AgentConfig (`config.py`)
- `AgentConfig` (dataclass) – Agent configuration management
- `get_config() -> AgentConfig` – Get current agent configuration
- `set_config(config: AgentConfig) -> None` – Set agent configuration
- `reset_config() -> None` – Reset configuration to defaults

### AgentIntegrationAdapter (`core.py`)
- `AgentIntegrationAdapter` (ABC) – Base class for integrating agents with Codomyrmex modules

### Module Exports (`__init__.py`)
- `AgentInterface` – Abstract base class for all agents
- `AgentIntegrationAdapter` – Base class for integration adapters
- `AgentCapabilities` – Enum of agent capabilities
- `AgentRequest` – Request data structure
- `AgentResponse` – Response data structure
- `AgentConfig` – Configuration management
- `get_config`, `set_config`, `reset_config` – Configuration functions

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation
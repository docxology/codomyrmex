# Codomyrmex Agents — src/codomyrmex/agents

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [theory](theory/AGENTS.md)
    - [generic](generic/AGENTS.md)
    - [ai_code_editing](ai_code_editing/AGENTS.md)
    - [droid](droid/AGENTS.md)
    - [jules](jules/AGENTS.md)
    - [claude](claude/AGENTS.md)
    - [codex](codex/AGENTS.md)
    - [opencode](opencode/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Agents module providing integration with various agentic frameworks including Jules CLI, Claude API, OpenAI Codex, and OpenCode CLI. This module includes theoretical foundations, generic utilities, and framework-specific implementations that integrate seamlessly with Codomyrmex modules.

The agents module serves as the agentic framework integration layer, supporting multiple agent frameworks through a unified interface.

## Module Overview

### Key Capabilities
- **Agent Framework Integration**: Integrate with Jules CLI, Claude API, OpenAI Codex, and OpenCode CLI
- **Unified Interface**: Consistent interface across all agent frameworks
- **Code Generation**: Generate code using various agent frameworks
- **Code Editing**: Edit and refactor code using agents
- **Streaming Support**: Support streaming responses where available
- **Multi-Agent Orchestration**: Coordinate multiple agents for complex tasks

### Key Features
- Abstract base class for all agents (`AgentInterface`)
- Framework-specific implementations (Jules, Claude, Codex, OpenCode)
- Integration adapters for Codomyrmex modules
- Configuration management with environment variable support
- Comprehensive error handling and logging

## Function Signatures

### Core Interface Functions

```python
def get_capabilities(self) -> list[AgentCapabilities]
```

Get list of capabilities supported by this agent.

**Returns:** `list[AgentCapabilities]` - List of supported capabilities

```python
def execute(self, request: AgentRequest) -> AgentResponse
```

Execute an agent request.

**Parameters:**
- `request` (AgentRequest): Agent request with prompt and context

**Returns:** `AgentResponse` - Agent response with content and metadata

**Raises:**
- `AgentError`: If agent operation fails
- `AgentTimeoutError`: If operation times out

```python
def stream(self, request: AgentRequest) -> Iterator[str]
```

Stream response from agent.

**Parameters:**
- `request` (AgentRequest): Agent request with prompt and context

**Yields:** `str` - Chunks of response content

**Raises:**
- `AgentError`: If agent operation fails

```python
def supports_capability(self, capability: AgentCapabilities) -> bool
```

Check if agent supports a specific capability.

**Parameters:**
- `capability` (AgentCapabilities): Capability to check

**Returns:** `bool` - True if capability is supported

```python
def validate_request(self, request: AgentRequest) -> list[str]
```

Validate an agent request.

**Parameters:**
- `request` (AgentRequest): Agent request to validate

**Returns:** `list[str]` - List of validation errors (empty if valid)

### Configuration Functions

```python
def get_config() -> AgentConfig
```

Get global agent configuration instance.

**Returns:** `AgentConfig` - Global configuration instance

```python
def set_config(config: AgentConfig) -> None
```

Set global agent configuration instance.

**Parameters:**
- `config` (AgentConfig): Configuration instance to set

**Returns:** None

```python
def reset_config() -> None
```

Reset global configuration to default.

**Returns:** None

### Data Structures

```python
@dataclass
class AgentRequest:
    prompt: str
    context: dict[str, Any] = None
    capabilities: list[AgentCapabilities] = None
    timeout: Optional[int] = None
    metadata: dict[str, Any] = None
```

Request structure for agent operations.

```python
@dataclass
class AgentResponse:
    content: str
    metadata: dict[str, Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
```

Response structure from agent operations.

```python
class AgentCapabilities(Enum):
    CODE_GENERATION = "code_generation"
    CODE_EDITING = "code_editing"
    CODE_ANALYSIS = "code_analysis"
    TEXT_COMPLETION = "text_completion"
    STREAMING = "streaming"
    MULTI_TURN = "multi_turn"
    CODE_EXECUTION = "code_execution"
```

Enum of agent capabilities.

## Active Components

### Core Files
- `__init__.py` – Package initialization and exports
- `core.py` – Core agent interfaces and base classes
- `config.py` – Configuration management
- `exceptions.py` – Agent-specific exceptions

### Submodules
- `theory/` – Theoretical foundations for agentic systems
- `generic/` – Generic/shared functionality (BaseAgent, AgentOrchestrator, etc.)
- `ai_code_editing/` – AI-powered code generation and editing
- `droid/` – Droid task management system
- `jules/` – Jules CLI integration
- `claude/` – Claude API integration
- `codex/` – OpenAI Codex integration
- `opencode/` – OpenCode CLI integration


### Additional Files
- `README.md` – Readme Md
- `SPEC.md` – Spec Md
- `ai_code_editing` – Ai Code Editing
- `claude` – Claude
- `codex` – Codex
- `droid` – Droid
- `generic` – Generic
- `jules` – Jules
- `tests` – Tests
- `theory` – Theory

## Operating Contracts

### Universal Agent Protocols

All agents operating within this module must:

1. **Implement AgentInterface**: All agents must implement the `AgentInterface` abstract base class
2. **Support Capabilities**: Agents must declare their capabilities via `get_capabilities()`
3. **Handle Errors Gracefully**: All operations must handle errors and return structured responses
4. **Use Structured Logging**: All operations must use `logging_monitoring` for logging
5. **Validate Requests**: Agents should validate requests before processing
6. **Support Timeouts**: Agents should respect timeout configurations

### Integration Guidelines

When integrating with Codomyrmex modules:

1. **Use Integration Adapters**: Use `AgentIntegrationAdapter` for module integration
2. **Maintain Interface Consistency**: Keep integration interfaces consistent across frameworks
3. **Handle Module Errors**: Catch and handle module-specific errors appropriately
4. **Log Integration Operations**: Log all integration operations for debugging

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Submodule Documentation
- **Theory**: [theory/AGENTS.md](theory/AGENTS.md)
- **Generic**: [generic/AGENTS.md](generic/AGENTS.md)
- **AI Code Editing**: [ai_code_editing/AGENTS.md](ai_code_editing/AGENTS.md)
- **Droid**: [droid/AGENTS.md](droid/AGENTS.md)
- **Jules**: [jules/AGENTS.md](jules/AGENTS.md)
- **Claude**: [claude/AGENTS.md](claude/AGENTS.md)
- **Codex**: [codex/AGENTS.md](codex/AGENTS.md)
- **OpenCode**: [opencode/AGENTS.md](opencode/AGENTS.md)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src/README.md](../../README.md) - Source code documentation


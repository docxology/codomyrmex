# Codomyrmex Agents — src/codomyrmex/agents/jules

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Jules Agents](AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Jules submodule providing integration with Jules CLI tool (asynchronous coding agent from Google). This includes a client wrapper for executing jules commands and integration adapters for Codomyrmex modules.

Jules CLI is a task-based system that creates sessions for code generation, editing, and analysis tasks. The client integrates with the agent orchestration system and provides adapters for seamless integration with Codomyrmex modules.

## Capabilities

JulesClient supports the following capabilities:
- `CODE_GENERATION` - Generate code from task descriptions
- `CODE_EDITING` - Edit and refactor code through task sessions
- `CODE_ANALYSIS` - Analyze code quality and provide suggestions
- `TEXT_COMPLETION` - Complete text and code snippets
- `STREAMING` - Stream command output in real-time

## Function Signatures

### JulesClient

```python
def __init__(self, config: Optional[dict[str, Any]] = None) -> None
```

Initialize Jules client.

**Parameters:**
- `config` (Optional[dict[str, Any]]): Optional configuration override

**Returns:** None

```python
def execute(self, request: AgentRequest) -> AgentResponse
```

Execute a Jules task request. Creates a new Jules session with the task description.

**Parameters:**
- `request` (AgentRequest): Agent request with prompt and context

**Returns:** `AgentResponse` - Response with task output

**Context Parameters:**
- `repo` (str): Repository specification (e.g., "owner/repo")
- `parallel` (int): Number of parallel sessions to create

```python
def stream(self, request: AgentRequest) -> Iterator[str]
```

Stream Jules command output.

**Parameters:**
- `request` (AgentRequest): Agent request

**Yields:** `str` - Chunks of output

```python
def execute_jules_command(self, command: str, args: Optional[list[str]] = None) -> dict[str, Any]
```

Execute a jules command directly.

**Parameters:**
- `command` (str): Jules command name (e.g., "new", "help")
- `args` (Optional[list[str]]): Command arguments

**Returns:** `dict` - Command result with output, exit_code, stdout, stderr

```python
def get_jules_help(self) -> dict[str, Any]
```

Get jules help information.

**Returns:** `dict` - Help information with help_text, exit_code, available

### JulesIntegrationAdapter

```python
def adapt_for_ai_code_editing(self, prompt: str, language: str = "python", **kwargs) -> str
```

Adapt Jules for AI code editing module. Creates a Jules task to generate code.

**Parameters:**
- `prompt` (str): Code generation prompt
- `language` (str): Programming language
- `**kwargs`: Additional parameters (repo, parallel, etc.)

**Returns:** `str` - Generated code

```python
def adapt_for_llm(self, messages: list[dict], model: str = None, **kwargs) -> dict
```

Adapt Jules for LLM module. Converts messages to a task prompt.

**Parameters:**
- `messages` (list[dict]): Conversation messages
- `model` (str): Model name (not used for Jules)
- `**kwargs`: Additional parameters

**Returns:** `dict` - Completion result with content, model, usage, metadata

```python
def adapt_for_code_execution(self, code: str, language: str = "python", **kwargs) -> dict[str, Any]
```

Adapt Jules for code execution sandbox. Uses Jules to analyze code.

**Parameters:**
- `code` (str): Code to analyze
- `language` (str): Programming language
- `**kwargs`: Additional parameters

**Returns:** `dict` - Analysis result with success, output, error, metadata

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Parent Module**: [agents](../AGENTS.md)



## Active Components
- `README.md` - Component file.
- `SPEC.md` - Component file.
- `__init__.py` - Component file.
- `jules_client.py` - Component file.
- `jules_integration.py` - Component file.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update task queues when necessary.
- Jules CLI must be installed and available in PATH for full functionality.
- Task-based operations create asynchronous sessions; results may require polling.

## Orchestration Integration

JulesClient is fully compatible with `AgentOrchestrator` for multi-agent coordination:

```python
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.core import AgentRequest

# Create orchestrator with Jules and other agents
jules = JulesClient()
orchestrator = AgentOrchestrator([jules, other_agent])

# Parallel execution
request = AgentRequest(prompt="write unit tests")
responses = orchestrator.execute_parallel(request)

# Sequential execution with fallback
response = orchestrator.execute_with_fallback(request)
```

## Integration with Codomyrmex Modules

Jules integrates with Codomyrmex modules via `JulesIntegrationAdapter`:

- **AI Code Editing**: Generate and edit code through Jules task sessions
- **LLM Module**: Use Jules for text completion and conversation
- **Code Execution**: Analyze code using Jules task system

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1.  **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2.  **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3.  **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4.  **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

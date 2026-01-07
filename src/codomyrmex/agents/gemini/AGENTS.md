# Codomyrmex Agents — src/codomyrmex/agents/gemini

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Gemini Agents](AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Gemini submodule providing integration with Google's Gemini CLI tool. This includes a client wrapper for executing gemini commands and integration adapters for Codomyrmex modules.

Gemini CLI is an interactive command-line interface for Google's Gemini AI models. The client integrates with the agent orchestration system and provides adapters for seamless integration with Codomyrmex modules.

## Capabilities

GeminiClient supports the following capabilities:
- `CODE_GENERATION` - Generate code from prompts using Gemini models
- `CODE_EDITING` - Edit and refactor code through interactive sessions
- `CODE_ANALYSIS` - Analyze code quality and provide improvement suggestions
- `TEXT_COMPLETION` - Complete text and code snippets
- `STREAMING` - Stream command output in real-time
- `MULTI_TURN` - Support multi-turn conversations with session management

## Function Signatures

### GeminiClient

```python
def __init__(self, config: Optional[dict[str, Any]] = None) -> None
```

Initialize Gemini client.

**Parameters:**
- `config` (Optional[dict[str, Any]]): Optional configuration override

**Returns:** None

```python
def execute(self, request: AgentRequest) -> AgentResponse
```

Execute a Gemini request. Sends the prompt to Gemini CLI and returns the response.

**Parameters:**
- `request` (AgentRequest): Agent request with prompt and context

**Returns:** `AgentResponse` - Response with content and metadata

**Context Parameters:**
- `files` (list[str]): List of file paths to include via @ commands
- `directories` (list[str]): List of directory paths to include
- `model` (str): Gemini model name (optional)

```python
def stream(self, request: AgentRequest) -> Iterator[str]
```

Stream Gemini command output.

**Parameters:**
- `request` (AgentRequest): Agent request

**Yields:** `str` - Chunks of output

```python
def execute_gemini_command(self, command: str, args: Optional[list[str]] = None, input_text: Optional[str] = None) -> dict[str, Any]
```

Execute a gemini slash command.

**Parameters:**
- `command` (str): Gemini command name (e.g., "/model", "/settings")
- `args` (Optional[list[str]]): Command arguments
- `input_text` (Optional[str]): Optional input text to send

**Returns:** `dict` - Command result with output, exit_code, stdout, stderr, success

```python
def get_gemini_help(self) -> dict[str, Any]
```

Get gemini help information.

**Returns:** `dict` - Help information with help_text, exit_code, available

```python
def save_chat(self, tag: str, prompt: Optional[str] = None) -> dict[str, Any]
```

Save current chat session.

**Parameters:**
- `tag` (str): Tag for identifying the conversation
- `prompt` (Optional[str]): Optional prompt to save

**Returns:** `dict` - Save result dictionary

```python
def resume_chat(self, tag: str) -> dict[str, Any]
```

Resume a saved chat session.

**Parameters:**
- `tag` (str): Tag of the conversation to resume

**Returns:** `dict` - Resume result dictionary

```python
def list_chats(self) -> dict[str, Any]
```

List available chat sessions.

**Returns:** `dict` - List of available chats

### GeminiIntegrationAdapter

```python
def adapt_for_ai_code_editing(self, prompt: str, language: str = "python", **kwargs) -> str
```

Adapt Gemini for AI code editing module. Generates code using Gemini.

**Parameters:**
- `prompt` (str): Code generation prompt
- `language` (str): Programming language
- `**kwargs`: Additional parameters (files, directories, etc.)

**Returns:** `str` - Generated code

```python
def adapt_for_llm(self, messages: list[dict], model: str = None, **kwargs) -> dict
```

Adapt Gemini for LLM module. Converts messages to a prompt and uses Gemini for completion.

**Parameters:**
- `messages` (list[dict]): Conversation messages
- `model` (str): Model name (optional, can use /model command)
- `**kwargs`: Additional parameters

**Returns:** `dict` - Completion result with content, model, usage, metadata

```python
def adapt_for_code_execution(self, code: str, language: str = "python", **kwargs) -> dict[str, Any]
```

Adapt Gemini for code execution sandbox. Uses Gemini to analyze code.

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
- `gemini_client.py` - Component file.
- `gemini_integration.py` - Component file.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update task queues when necessary.
- Gemini CLI must be installed and available in PATH for full functionality.
- Node.js must be installed for Gemini CLI to function.
- Some interactive features may not be fully accessible programmatically.
- Shell commands (!) are disabled by default for safety.

## Orchestration Integration

GeminiClient is fully compatible with `AgentOrchestrator` for multi-agent coordination:

```python
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.core import AgentRequest

# Create orchestrator with Gemini and other agents
gemini = GeminiClient()
orchestrator = AgentOrchestrator([gemini, other_agent])

# Parallel execution
request = AgentRequest(prompt="write unit tests")
responses = orchestrator.execute_parallel(request)

# Sequential execution with fallback
response = orchestrator.execute_with_fallback(request)
```

## Integration with Codomyrmex Modules

Gemini integrates with Codomyrmex modules via `GeminiIntegrationAdapter`:

- **AI Code Editing**: Generate and edit code using Gemini models
- **LLM Module**: Use Gemini for text completion and conversation
- **Code Execution**: Analyze code using Gemini's analysis capabilities

## Configuration

Gemini client configuration is managed through `AgentConfig` and environment variables:

```python
from codomyrmex.agents import AgentConfig, set_config

# Create custom configuration
config = AgentConfig(
    gemini_command="gemini",
    gemini_timeout=120,
    gemini_working_dir="/path/to/project",
    gemini_api_key="your-api-key",
    gemini_auth_method="api_key"
)

# Set as global configuration
set_config(config)
```

### Environment Variables

- `GEMINI_COMMAND` - Gemini CLI command (default: "gemini")
- `GEMINI_TIMEOUT` - Operation timeout in seconds (default: 60)
- `GEMINI_WORKING_DIR` - Working directory for CLI operations
- `GEMINI_API_KEY` - API key for authentication (optional)
- `GEMINI_AUTH_METHOD` - Authentication method: "oauth" or "api_key" (default: "oauth")
- `GEMINI_SETTINGS_PATH` - Path to .gemini/settings.json (optional)

## Error Handling

Gemini operations raise `GeminiError` for command failures:

```python
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.exceptions import GeminiError
from codomyrmex.agents.core import AgentRequest

gemini = GeminiClient()
request = AgentRequest(prompt="test prompt")

try:
    response = gemini.execute(request)
except GeminiError as e:
    print(f"Gemini error: {e}")
    print(f"Command: {e.context.get('command')}")
    print(f"Exit code: {e.context.get('exit_code')}")
```

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3. **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4. **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.


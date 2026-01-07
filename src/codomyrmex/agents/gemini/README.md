# src/codomyrmex/agents/gemini

## Signposting
- **Parent**: [agents](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Gemini submodule providing integration with Google's Gemini CLI tool. This includes a client wrapper for executing gemini commands and integration adapters for Codomyrmex modules.

Gemini CLI is an interactive command-line interface for Google's Gemini AI models. It supports various built-in commands, file operations, shell integration, and session management.

## Usage

### Basic Usage

```python
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.core import AgentRequest

# Create client
gemini = GeminiClient()

# Execute request
request = AgentRequest(
    prompt="Write a Python function to calculate fibonacci numbers"
)
response = gemini.execute(request)

if response.is_success():
    print(response.content)
```

### Using File Operations (@ commands)

```python
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.core import AgentRequest

gemini = GeminiClient()

# Include files in the prompt
request = AgentRequest(
    prompt="@src/main.py Explain this code",
    context={"files": ["src/main.py", "src/utils.py"]}
)
response = gemini.execute(request)
```

### Using Slash Commands

```python
from codomyrmex.agents.gemini import GeminiClient

gemini = GeminiClient()

# Change model
result = gemini.execute_gemini_command("/model", ["gemini-1.5-pro"])

# Get help
help_info = gemini.get_gemini_help()

# List available tools
tools = gemini.execute_gemini_command("/tools")
```

### Using Integration Adapter

```python
from codomyrmex.agents.gemini import GeminiClient, GeminiIntegrationAdapter

# Create client and adapter
gemini = GeminiClient()
adapter = GeminiIntegrationAdapter(gemini)

# Generate code via AI code editing module
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a REST API endpoint",
    language="python",
    files=["src/models.py"]  # Optional: include files
)

# Use with LLM module
messages = [
    {"role": "user", "content": "Explain this code"},
    {"role": "assistant", "content": "I'll analyze it"}
]
result = adapter.adapt_for_llm(messages, model="gemini-1.5-pro")

# Analyze code via code execution module
analysis = adapter.adapt_for_code_execution(
    code="def test(): pass",
    language="python"
)
```

### Session Management

```python
from codomyrmex.agents.gemini import GeminiClient

gemini = GeminiClient()

# Save a chat session
gemini.save_chat("my_session", prompt="Continue working on the authentication module")

# List available sessions
sessions = gemini.list_chats()

# Resume a session
gemini.resume_chat("my_session")
```

### Multi-Agent Orchestration

```python
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.claude import ClaudeClient
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.core import AgentRequest

# Create multiple agents
gemini = GeminiClient()
claude = ClaudeClient()

# Create orchestrator
orchestrator = AgentOrchestrator([gemini, claude])

# Execute in parallel
request = AgentRequest(prompt="write comprehensive tests")
responses = orchestrator.execute_parallel(request)

# Execute with fallback (try Gemini first, fallback to Claude)
response = orchestrator.execute_with_fallback(request)
```

### Streaming Output

```python
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.core import AgentRequest

gemini = GeminiClient()
request = AgentRequest(prompt="analyze codebase structure")

# Stream output in real-time
for chunk in gemini.stream(request):
    print(chunk)
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Module**: [agents](../README.md)

## Capabilities

GeminiClient supports the following agent capabilities:

- **CODE_GENERATION**: Generate code from prompts using Gemini models
- **CODE_EDITING**: Edit and refactor code through interactive sessions
- **CODE_ANALYSIS**: Analyze code quality and provide improvement suggestions
- **TEXT_COMPLETION**: Complete text and code snippets
- **STREAMING**: Stream command output in real-time
- **MULTI_TURN**: Support multi-turn conversations with session management

## Configuration

Gemini client can be configured via environment variables or config dictionary:

```python
# Environment variables
GEMINI_COMMAND=gemini          # Gemini CLI command (default: "gemini")
GEMINI_TIMEOUT=60             # Command timeout in seconds (default: 60)
GEMINI_WORKING_DIR=/path/to/dir  # Working directory (optional)
GEMINI_API_KEY=your-api-key   # API key for authentication (optional)
GEMINI_AUTH_METHOD=oauth       # Authentication method: "oauth" or "api_key" (default: "oauth")
GEMINI_SETTINGS_PATH=~/.gemini/settings.json  # Path to settings file (optional)

# Or via config dictionary
gemini = GeminiClient(config={
    "gemini_command": "gemini",
    "gemini_timeout": 120,
    "gemini_working_dir": "/path/to/project",
    "gemini_api_key": "your-api-key",
    "gemini_auth_method": "api_key",
    "gemini_enable_shell_commands": False  # Disable ! commands for safety
})
```

### Authentication

Gemini CLI supports two authentication methods:

1. **OAuth** (default): Interactive browser-based authentication
   - Run `gemini` CLI manually first to authenticate
   - The Python client will use the existing authentication

2. **API Key**: Programmatic authentication
   - Set `GEMINI_API_KEY` environment variable
   - Set `gemini_auth_method` to `"api_key"` in config

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

## Integration with Codomyrmex Modules

Gemini integrates seamlessly with Codomyrmex modules:

- **AI Code Editing** (`agents/ai_code_editing`): Generate and edit code
- **LLM Module** (`llm`): Text completion and conversation
- **Code Execution** (`code`): Code analysis and validation

All integrations use the `GeminiIntegrationAdapter` which provides a consistent interface across modules.

## Gemini CLI Features

The Gemini CLI supports many built-in features:

### Slash Commands
- `/model` - Change the Gemini model
- `/settings` - Open settings editor
- `/chat` - Save/resume/list chat sessions
- `/memory` - Manage hierarchical memory (GEMINI.md files)
- `/directory` - Manage workspace directories
- `/mcp` - Manage Model Context Protocol servers
- `/tools` - List available tools
- `/help` - Display help information

### File Operations
- `@path/to/file` - Include file content in prompt
- `@path/to/directory` - Include directory contents

### Shell Integration
- `!command` - Execute shell commands (disabled by default for safety)
- Enable via `gemini_enable_shell_commands` config option

## Limitations

- **Interactive Features**: Some interactive features (like `/settings` dialog) may not be fully accessible programmatically
- **OAuth Authentication**: Requires manual browser interaction for initial setup
- **Shell Commands**: Shell command execution (`!`) is disabled by default for safety
- **Node.js Dependency**: Gemini CLI is a Node.js tool, so Node.js must be installed

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3. **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4. **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.


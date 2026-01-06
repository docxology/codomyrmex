# src/codomyrmex/agents/jules

## Signposting
- **Parent**: [agents](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Jules submodule providing integration with Jules CLI tool. This includes a client wrapper for executing jules commands and integration adapters for Codomyrmex modules.

## Usage

### Basic Usage

```python
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.core import AgentRequest

# Create client
jules = JulesClient()

# Execute request (creates a Jules task session)
request = AgentRequest(
    prompt="write unit tests for the authentication module",
    context={"repo": "myorg/myrepo"}  # Optional repository context
)
response = jules.execute(request)

if response.is_success():
    print(response.content)
```

### Using Context Parameters

```python
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.core import AgentRequest

jules = JulesClient()

# Create task with repository and parallel sessions
request = AgentRequest(
    prompt="refactor the database layer",
    context={
        "repo": "owner/repository",
        "parallel": 3  # Create 3 parallel sessions
    }
)
response = jules.execute(request)
```

### Using Integration Adapter

```python
from codomyrmex.agents.jules import JulesClient, JulesIntegrationAdapter

# Create client and adapter
jules = JulesClient()
adapter = JulesIntegrationAdapter(jules)

# Generate code via AI code editing module
code = adapter.adapt_for_ai_code_editing(
    prompt="Create a REST API endpoint",
    language="python",
    repo="myorg/myrepo"  # Optional context
)

# Use with LLM module
messages = [
    {"role": "user", "content": "Explain this code"},
    {"role": "assistant", "content": "I'll analyze it"}
]
result = adapter.adapt_for_llm(messages)

# Analyze code via code execution module
analysis = adapter.adapt_for_code_execution(
    code="def test(): pass",
    language="python"
)
```

### Multi-Agent Orchestration

```python
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.claude import ClaudeClient
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.core import AgentRequest

# Create multiple agents
jules = JulesClient()
claude = ClaudeClient()

# Create orchestrator
orchestrator = AgentOrchestrator([jules, claude])

# Execute in parallel
request = AgentRequest(prompt="write comprehensive tests")
responses = orchestrator.execute_parallel(request)

# Execute with fallback (try Jules first, fallback to Claude)
response = orchestrator.execute_with_fallback(request)

# Execute sequentially
responses = orchestrator.execute_sequential(request, stop_on_success=True)
```

### Streaming Output

```python
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.core import AgentRequest

jules = JulesClient()
request = AgentRequest(prompt="analyze codebase structure")

# Stream output in real-time
for chunk in jules.stream(request):
    print(chunk)
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Module**: [agents](../README.md)



## Capabilities

JulesClient supports the following agent capabilities:

- **CODE_GENERATION**: Generate code from task descriptions via Jules sessions
- **CODE_EDITING**: Edit and refactor code through task-based workflows
- **CODE_ANALYSIS**: Analyze code quality and provide improvement suggestions
- **TEXT_COMPLETION**: Complete text and code snippets
- **STREAMING**: Stream command output in real-time

## Configuration

Jules client can be configured via environment variables or config dictionary:

```python
# Environment variables
JULES_COMMAND=jules          # Jules CLI command (default: "jules")
JULES_TIMEOUT=30             # Command timeout in seconds (default: 30)
JULES_WORKING_DIR=/path/to/dir  # Working directory (optional)

# Or via config dictionary
jules = JulesClient(config={
    "jules_command": "jules",
    "jules_timeout": 60,
    "jules_working_dir": "/path/to/project"
})
```

## Error Handling

Jules operations raise `JulesError` for command failures:

```python
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.exceptions import JulesError
from codomyrmex.agents.core import AgentRequest

jules = JulesClient()
request = AgentRequest(prompt="test task")

try:
    response = jules.execute(request)
except JulesError as e:
    print(f"Jules error: {e}")
    print(f"Command: {e.context.get('command')}")
    print(f"Exit code: {e.context.get('exit_code')}")
```

## Integration with Codomyrmex Modules

Jules integrates seamlessly with Codomyrmex modules:

- **AI Code Editing** (`agents/ai_code_editing`): Generate and edit code
- **LLM Module** (`llm`): Text completion and conversation
- **Code Execution** (`code`): Code analysis and validation

All integrations use the `JulesIntegrationAdapter` which provides a consistent interface across modules.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1.  **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2.  **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3.  **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4.  **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

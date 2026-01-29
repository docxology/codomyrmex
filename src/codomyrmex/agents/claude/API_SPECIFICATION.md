# Claude Module - API Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Complete programmatic API reference for the Claude agent module. All public classes and methods are documented with type signatures and usage examples.

---

## Module Exports

```python
from codomyrmex.agents.claude import (
    ClaudeClient,           # Main API client
    ClaudeIntegrationAdapter,  # Module integration bridge
    CLAUDE_PRICING,         # Pricing dictionary
)
```

---

## ClaudeClient

Full-featured client for Anthropic Claude API with retry logic, session management, and tool calling.

### Class Signature

```python
class ClaudeClient(APIAgentBase):
    """Client for interacting with Claude API."""
    
    # Default configuration
    DEFAULT_MAX_RETRIES: int = 3
    DEFAULT_INITIAL_DELAY: float = 1.0
    DEFAULT_MAX_DELAY: float = 60.0
    DEFAULT_BACKOFF_FACTOR: float = 2.0
```

### Constructor

```python
def __init__(
    self,
    config: Optional[dict[str, Any]] = None,
    session_manager: Optional[SessionManager] = None,
) -> None:
    """Initialize Claude client.
    
    Args:
        config: Configuration override dictionary:
            - claude_api_key: API key (or ANTHROPIC_API_KEY env var)
            - claude_model: Model name (default: claude-3-5-sonnet-20241022)
            - claude_timeout: Request timeout in seconds
            - claude_max_tokens: Maximum output tokens
            - claude_temperature: Sampling temperature
            - max_retries: Maximum retry attempts (default: 3)
            - initial_retry_delay: Initial delay between retries
        session_manager: Optional session manager for multi-turn conversations
    
    Raises:
        AgentConfigurationError: If API key not found
    """
```

### Core Methods

#### execute

```python
def execute(self, request: AgentRequest) -> AgentResponse:
    """Execute Claude API request with automatic retry.
    
    Args:
        request: AgentRequest with prompt and optional context
    
    Returns:
        AgentResponse containing:
            - content: Response text
            - tokens_used: Total tokens
            - execution_time: Time in seconds
            - metadata: {usage, stop_reason, cost_usd, tool_calls}
    
    Raises:
        ClaudeError: On API errors after retries exhausted
    
    Example:
        >>> client = ClaudeClient()
        >>> response = client.execute(AgentRequest(prompt="Hello Claude"))
        >>> print(response.content)
    """
```

#### stream

```python
def stream(self, request: AgentRequest) -> Iterator[str]:
    """Stream Claude API response.
    
    Args:
        request: AgentRequest with prompt and context
    
    Yields:
        Chunks of response content as strings
    
    Example:
        >>> for chunk in client.stream(AgentRequest(prompt="Tell me a story")):
        ...     print(chunk, end="", flush=True)
    """
```

### Tool/Function Calling

#### register_tool

```python
def register_tool(
    self,
    name: str,
    description: str,
    input_schema: dict[str, Any],
    handler: Optional[Callable] = None,
) -> None:
    """Register a tool for function calling.
    
    Args:
        name: Unique tool name
        description: Description of tool functionality
        input_schema: JSON Schema for tool parameters
        handler: Optional callable to execute tool
    
    Example:
        >>> client.register_tool(
        ...     name="get_weather",
        ...     description="Get weather for a location",
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {"location": {"type": "string"}}
        ...     },
        ...     handler=lambda location: f"Sunny in {location}"
        ... )
    """
```

#### execute_with_tools

```python
def execute_with_tools(
    self,
    request: AgentRequest,
    auto_execute: bool = True,
    max_tool_rounds: int = 10,
) -> AgentResponse:
    """Execute request with automatic tool execution loop.
    
    Args:
        request: AgentRequest
        auto_execute: Whether to automatically execute tool calls
        max_tool_rounds: Maximum tool execution iterations
    
    Returns:
        AgentResponse with final content and tool_calls metadata
    
    Raises:
        ClaudeError: If max_tool_rounds exceeded
    """
```

#### execute_tool_call

```python
def execute_tool_call(
    self,
    tool_name: str,
    tool_input: dict[str, Any],
) -> Any:
    """Execute a registered tool handler.
    
    Args:
        tool_name: Name of registered tool
        tool_input: Input parameters for tool
    
    Returns:
        Tool execution result
    
    Raises:
        ClaudeError: If tool not found or execution fails
    """
```

### Session Management

#### create_session

```python
def create_session(
    self,
    session_id: Optional[str] = None
) -> AgentSession:
    """Create a new conversation session.
    
    Args:
        session_id: Optional specific session ID
    
    Returns:
        New AgentSession instance
    """
```

#### execute_with_session

```python
def execute_with_session(
    self,
    request: AgentRequest,
    session: Optional[AgentSession] = None,
    session_id: Optional[str] = None,
) -> AgentResponse:
    """Execute request with session context.
    
    Args:
        request: AgentRequest
        session: Existing session to use
        session_id: Session ID to retrieve from manager
    
    Returns:
        AgentResponse with session context preserved
    
    Example:
        >>> session = client.create_session()
        >>> r1 = client.execute_with_session(
        ...     AgentRequest(prompt="My name is Alice"),
        ...     session=session
        ... )
        >>> r2 = client.execute_with_session(
        ...     AgentRequest(prompt="What is my name?"),
        ...     session=session
        ... )
    """
```

### Claude Code Methods

#### edit_file

```python
def edit_file(
    self,
    file_path: str,
    instructions: str,
    language: Optional[str] = None,
) -> dict[str, Any]:
    """Apply AI-guided edits to a file.
    
    Args:
        file_path: Absolute path to file
        instructions: Natural language edit instructions
        language: Programming language (auto-detected if None)
    
    Returns:
        Dictionary with:
            - success: bool
            - original_content: str
            - modified_content: str
            - diff: Unified diff string
            - explanation: Description of changes
    
    Example:
        >>> result = client.edit_file(
        ...     "/path/to/file.py",
        ...     "Add type hints to all function parameters"
        ... )
        >>> print(result["diff"])
    """
```

#### create_file

```python
def create_file(
    self,
    file_path: str,
    description: str,
    language: str = "python",
) -> dict[str, Any]:
    """Generate a new file from description.
    
    Args:
        file_path: Path where file should be created
        description: Description of file contents
        language: Programming language
    
    Returns:
        Dictionary with:
            - success: bool
            - content: Generated file content
            - file_path: Actual file path
    
    Example:
        >>> result = client.create_file(
        ...     "/path/to/utils.py",
        ...     "Utility functions for string manipulation"
        ... )
    """
```

#### review_code

```python
def review_code(
    self,
    code: str,
    language: str = "python",
    analysis_type: str = "general",
) -> dict[str, Any]:
    """Perform AI-powered code review.
    
    Args:
        code: Code to review
        language: Programming language
        analysis_type: One of "general", "security", "bugs", "performance"
    
    Returns:
        Dictionary with:
            - success: bool
            - output: Full analysis text
            - issues: List of identified issues
            - recommendations: List of suggestions
    """
```

#### scan_directory

```python
def scan_directory(
    self,
    path: str,
    max_depth: int = 3,
    include_patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Scan directory for project context.
    
    Args:
        path: Directory path to scan
        max_depth: Maximum directory depth
        include_patterns: Glob patterns to include
        exclude_patterns: Glob patterns to exclude
    
    Returns:
        Dictionary with:
            - success: bool
            - structure: Hierarchical dict of directory
            - file_count: Total files found
            - summary: AI-generated project summary
    """
```

#### generate_diff

```python
def generate_diff(
    self,
    original: str,
    modified: str,
    filename: str = "file",
) -> dict[str, Any]:
    """Generate unified diff between code versions.
    
    Args:
        original: Original code content
        modified: Modified code content
        filename: Filename for diff header
    
    Returns:
        Dictionary with:
            - diff: Unified diff string
            - additions: Number of lines added
            - deletions: Number of lines removed
    """
```

#### run_command

```python
def run_command(
    self,
    command: str,
    cwd: Optional[str] = None,
    timeout: int = 60,
    capture_output: bool = True,
) -> dict[str, Any]:
    """Execute a shell command.
    
    Args:
        command: Shell command to execute
        cwd: Working directory for execution
        timeout: Maximum execution time in seconds
        capture_output: Whether to capture stdout/stderr
    
    Returns:
        Dictionary with:
            - success: bool
            - return_code: Process return code
            - stdout: Standard output
            - stderr: Standard error
            - duration: Execution time
    
    Example:
        >>> result = client.run_command("ls -la")
        >>> print(result["stdout"])
    """
```

#### get_project_structure

```python
def get_project_structure(
    self,
    path: str,
    max_depth: int = 4,
    include_analysis: bool = False,
) -> dict[str, Any]:
    """Get comprehensive project structure analysis.
    
    Args:
        path: Root directory of the project
        max_depth: Maximum scan depth
        include_analysis: Include AI-powered analysis
    
    Returns:
        Dictionary with:
            - success: bool
            - structure: Directory tree
            - file_count: Total files
            - language_breakdown: Files by language
            - analysis: AI analysis (if requested)
    
    Example:
        >>> result = client.get_project_structure("/path/to/project")
        >>> print(result["language_breakdown"])
    """
```

#### explain_code

```python
def explain_code(
    self,
    code: str,
    language: str = "python",
    detail_level: str = "medium",
) -> dict[str, Any]:
    """Generate comprehensive code explanation.
    
    Args:
        code: Code to explain
        language: Programming language
        detail_level: "brief", "medium", or "detailed"
    
    Returns:
        Dictionary with:
            - success: bool
            - explanation: Full explanation text
            - summary: One-line summary
            - concepts: Key concepts mentioned
            - tokens_used: Tokens consumed
    
    Example:
        >>> result = client.explain_code("def fib(n): ...")
        >>> print(result["summary"])
    """
```

#### suggest_tests

```python
def suggest_tests(
    self,
    code: str,
    language: str = "python",
    framework: Optional[str] = None,
) -> dict[str, Any]:
    """Generate test suggestions for code.
    
    Args:
        code: Code to generate tests for
        language: Programming language
        framework: Testing framework (e.g., "pytest", "jest")
    
    Returns:
        Dictionary with:
            - success: bool
            - tests: Generated test code
            - test_cases: List of test case descriptions
            - coverage_notes: Notes about test coverage
    
    Example:
        >>> result = client.suggest_tests("def add(a, b): return a + b")
        >>> print(result["tests"])
    """
```

---

## ClaudeIntegrationAdapter

Bridges ClaudeClient with other Codomyrmex modules.

### Class Signature

```python
class ClaudeIntegrationAdapter(AgentIntegrationAdapter):
    """Integration adapter for Claude with Codomyrmex modules."""
```

### Constructor

```python
def __init__(self, agent: ClaudeClient) -> None:
    """Initialize adapter with Claude client.
    
    Args:
        agent: ClaudeClient instance
    """
```

### Methods

#### adapt_for_ai_code_editing

```python
def adapt_for_ai_code_editing(
    self,
    prompt: str,
    language: str = "python",
    style: Optional[str] = None,
    context_code: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    **kwargs: Any
) -> str:
    """Generate code using Claude.
    
    Args:
        prompt: Description of code to generate
        language: Target programming language
        style: Coding style ("functional", "oop", "minimal", "verbose")
        context_code: Existing code for context
        max_tokens: Override max output tokens
        temperature: Override sampling temperature
    
    Returns:
        Generated code as string
    
    Raises:
        RuntimeError: If generation fails
    
    Example:
        >>> adapter = ClaudeIntegrationAdapter(client)
        >>> code = adapter.adapt_for_ai_code_editing(
        ...     "Binary search function",
        ...     language="python",
        ...     style="functional"
        ... )
    """
```

#### adapt_for_llm

```python
def adapt_for_llm(
    self,
    messages: list[dict],
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs: Any
) -> dict[str, Any]:
    """OpenAI-compatible interface for LLM module.
    
    Args:
        messages: List of message dicts with "role" and "content"
        model: Model name (optional)
        system_prompt: System prompt
    
    Returns:
        Completion result with:
            - content: Response text
            - model: Model used
            - usage: {prompt_tokens, completion_tokens, total_tokens}
            - metadata: Additional info
    """
```

#### adapt_for_code_execution

```python
def adapt_for_code_execution(
    self,
    code: str,
    language: str = "python",
    analysis_type: str = "general",
    **kwargs: Any
) -> dict[str, Any]:
    """Analyze code for code execution sandbox.
    
    Args:
        code: Code to analyze
        language: Programming language
        analysis_type: "general", "security", "bugs", or "performance"
    
    Returns:
        Analysis result with:
            - success: bool
            - output: Analysis text
            - issues: List of issues
            - recommendations: List of suggestions
    """
```

#### adapt_for_code_refactoring

```python
def adapt_for_code_refactoring(
    self,
    code: str,
    instruction: str,
    language: str = "python",
    **kwargs: Any
) -> dict[str, Any]:
    """Refactor code based on instructions.
    
    Args:
        code: Code to refactor
        instruction: Refactoring instruction
        language: Programming language
    
    Returns:
        Result with:
            - success: bool
            - refactored_code: Modified code
            - explanation: Description of changes
            - original_code: Original code
    """
```

---

## Constants

### CLAUDE_PRICING

```python
CLAUDE_PRICING: dict[str, dict[str, float]] = {
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022": {"input": 1.00, "output": 5.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
}
# Prices per 1 million tokens
```

---

## Data Types

### AgentRequest

```python
@dataclass
class AgentRequest:
    prompt: str                              # Main prompt text
    context: Optional[dict[str, Any]] = None # Optional context including:
                                              # - system: System prompt
                                              # - messages: Conversation history
                                              # - images: List of base64 images
```

### AgentResponse

```python
@dataclass
class AgentResponse:
    content: str = ""                        # Response content
    error: Optional[str] = None              # Error message if failed
    tokens_used: Optional[int] = None        # Total tokens consumed
    execution_time: Optional[float] = None   # Execution time in seconds
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def is_success(self) -> bool:
        """Return True if no error."""
```

---

## Navigation

- [README.md](README.md) - Human documentation
- [AGENTS.md](AGENTS.md) - Agent documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tools
- [SPEC.md](SPEC.md) - Technical specification

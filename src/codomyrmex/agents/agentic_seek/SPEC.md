# Technical Specification - agenticSeek

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.agents.agentic_seek`

## 1. Purpose

Integration with the [agenticSeek](https://github.com/Fosowl/agenticSeek) framework—a fully-local autonomous agent system providing multi-agent routing, web browsing, multi-language code execution, and task planning.

## 2. Architecture

### 2.1 Components

```
agentic_seek/
├── __init__.py               # Module exports (90+ symbols)
├── agentic_seek_client.py    # CLIAgentBase client (subprocess / Docker)
├── agent_router.py           # Keyword + heuristic agent classification
├── agent_types.py            # Enums, dataclasses, language resolution
├── code_execution.py         # Code block extraction, command building
├── task_planner.py           # JSON plan parsing, topological ordering
├── browser_automation.py     # Link/form extraction, prompt builders
├── README.md                 # User documentation
├── AGENTS.md                 # Agent guidelines
├── SPEC.md                   # This file
├── PAI.md                    # PAI integration notes
└── py.typed                  # PEP 561 marker
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `agents` (uses `CLIAgentBase`, `AgentCapabilities`, `AgentRequest`, `AgentResponse`)
- Optional runtime: Docker, Ollama, SearxNG (for full agenticSeek execution)

## 3. Interfaces

### 3.1 Public API

```python
from codomyrmex.agents.agentic_seek import (
    # Client
    AgenticSeekClient,          # CLIAgentBase subclass
    # Data models
    AgenticSeekAgentType,       # Enum: CODER, BROWSER, PLANNER, FILE, CASUAL
    AgenticSeekConfig,          # Frozen dataclass for config.ini
    AgenticSeekProvider,        # Enum: OLLAMA, LM_STUDIO, OPENAI, etc.
    AgenticSeekMemoryEntry,     # Conversation turn (role, content, timestamp)
    AgenticSeekTaskStatus,      # Enum: PENDING, RUNNING, COMPLETED, FAILED
    AgenticSeekTaskStep,        # Plan step with dependencies
    AgenticSeekExecutionResult, # Code execution outcome
    SUPPORTED_LANGUAGES,        # Dict of language metadata
    resolve_language,           # Alias → canonical language key
    # Router
    AgenticSeekRouter,          # Heuristic query classifier
    # Code execution
    AgenticSeekCodeExecutor,    # Facade for extract → classify → command
    CodeBlock,                  # Frozen dataclass for fenced code blocks
    extract_code_blocks,        # Regex-based code block extraction
    classify_language,          # Block → canonical language
    build_execution_command,    # Block → subprocess command list
    parse_execution_output,     # stdout/stderr → ExecutionResult
    # Task planning
    AgenticSeekTaskPlanner,     # Facade for parse → validate → order
    parse_plan_json,            # JSON → list[TaskStep]
    validate_plan,              # Structural + cycle detection
    get_execution_order,        # Topological sort
    extract_task_names,         # Heading extraction
    # Browser
    AgenticSeekBrowserConfig,   # Frozen dataclass
    extract_links,              # URL extraction from text
    clean_links,                # Trailing punct cleanup
    extract_form_fields,        # [name](value) pattern extraction
    build_search_prompt,        # Search result selection prompt
    build_navigation_prompt,    # Page navigation prompt
    get_today_date,             # Human-readable date string
)
```

### 3.2 Key Class Signatures

```python
class AgenticSeekClient(CLIAgentBase):
    def __init__(self, config: dict[str, Any] | None = None): ...
    def _execute_impl(self, request: AgentRequest) -> AgentResponse: ...
    def _stream_impl(self, request: AgentRequest) -> Iterator[str]: ...
    def get_available_agents(self) -> list[AgenticSeekAgentType]: ...
    def classify_query(self, query: str) -> AgenticSeekAgentType: ...
    def get_agent_status(self) -> dict[str, Any]: ...
    def validate_environment(self) -> dict[str, bool]: ...
    @staticmethod
    def parse_config_ini(path: str) -> AgenticSeekConfig: ...

class AgenticSeekRouter:
    def classify_query(self, query: str) -> AgenticSeekAgentType: ...
    def estimate_complexity(self, query: str) -> str: ...
```

## 4. Implementation Notes

### 4.1 Design Decisions

1. **CLIAgentBase**: agenticSeek is a locally-installed CLI/Docker application, not an API service, so we extend `CLIAgentBase` rather than `APIAgentBase`.
2. **Heuristic router**: The upstream uses `transformers` + `torch` for ML-based routing. We use lightweight keyword + structural heuristics to avoid heavy dependencies while preserving classification accuracy.
3. **Zero external deps**: All modules import cleanly without Docker, Ollama, or Selenium. Runtime execution requires these only when actually invoking agenticSeek.
4. **Frozen dataclasses**: `AgenticSeekConfig` and `AgenticSeekBrowserConfig` are frozen to prevent accidental mutation.

### 4.2 Limitations

- Subprocess execution requires agenticSeek to be cloned and installed locally
- The heuristic router is less accurate than the ML-based upstream router for ambiguous queries
- Docker Compose V2 is required for Docker-based execution

## 5. Testing

```bash
uv run pytest src/codomyrmex/tests/unit/agents/agentic_seek/ -v
```

## 6. Future Considerations

- WebSocket-based streaming for real-time output from Docker backend
- Integration with agenticSeek's session recovery system
- ML-based router option using `transformers` (optional dependency)
